
import sys
import argparse
import winshell
from . import env_utils
from . import locate_cl_exe

CLCACHE_REPO = "https://github.com/pthom/clcache.git"
CLCACHE_BRANCH = "clcache-msbuild-install"
THIS_DIR = env_utils.fileDirNameAbsolute(__file__)
CLCACHE_REPO_DIR = env_utils.dirNameAbsolute(THIS_DIR + "\\..\\clcache")
MSBUILD_USER_SETTINGS_DIR = env_utils.appDataPathLocal() + "\\Microsoft\\MSBuild\\v4.0"
MSBUILD_SETTING_FILE_CONTENT_CLCACHE = """<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ImportGroup Label="PropertySheets">
  </ImportGroup>
  <PropertyGroup Label="UserMacros" />
  <PropertyGroup />
  <PropertyGroup>
    <CLToolExe>clcache.exe</CLToolExe>
    <CLToolPath>PIP_SCRIPTS_DIR</CLToolPath>
  </PropertyGroup>
  <ItemDefinitionGroup />
  <ItemGroup />
</Project>
"""
MSBUILD_SETTING_FILE_CONTENT_NO_CLCACHE = """<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ImportGroup Label="PropertySheets">
  </ImportGroup>
  <PropertyGroup Label="UserMacros" />
  <PropertyGroup />
  <ItemDefinitionGroup />
  <ItemGroup />
</Project>
"""


def cloneClCache():
    env_utils.showFunctionIntro("Clone and update clcache repo")
    if not env_utils.hasDir(CLCACHE_REPO_DIR):
        if not env_utils.callAndShowCmd("git clone " + CLCACHE_REPO, cwd=THIS_DIR + "\\.."):
            return False
    if not env_utils.callAndShowCmd("git checkout " + CLCACHE_BRANCH, cwd=CLCACHE_REPO_DIR):
        return False
    if not env_utils.callAndShowCmd("git pull", cwd=CLCACHE_REPO_DIR):
        return False
    return True


def installClcache():
    env_utils.showFunctionIntro("Installing clcache")
    status = env_utils.callAndShowCmd("pip install .", cwd=CLCACHE_REPO_DIR)
    if not status:
        return False
    if not env_utils.hasProgramInPath("clcache"):
        print("Humm. its seems that the install failed")
        return False
    return True


def implCopyMsvcPref(prefContent):
    files = env_utils.listFiles(MSBUILD_USER_SETTINGS_DIR)
    for file in files:
        with open(file, 'w') as f:
            f.write(prefContent)
            print("Wrote pref in " + file)
    return True


def copyMsvcPrefClcache():
    env_utils.showFunctionIntro("Force clcache via Msbbuild user settings")
    prefContent = MSBUILD_SETTING_FILE_CONTENT_CLCACHE.replace(
        "PIP_SCRIPTS_DIR", env_utils.pipScriptsDir())
    return implCopyMsvcPref(prefContent)


def copyMsvcPrefOriginal():
    env_utils.showFunctionIntro("Disable clcache via Msbbuild user settings")
    return implCopyMsvcPref(MSBUILD_SETTING_FILE_CONTENT_NO_CLCACHE)


def showClCacheUsage():
    env_utils.showFunctionIntro("Note about clcache usage:")
    env_utils.callAndShowCmd("clcache --help")
    return True


def showStatus():
    if env_utils.hasProgramInPath("clcache"):
        print("clcache is in your PATH")
    else:
        print("clcache is not installed")

    if env_utils.readEnvVariableFromRegistry("CLCACHE_LOG") is not None:
        print("logs are enabled")
    else:
        print("logs are disabled")

    if env_utils.readEnvVariableFromRegistry("CLCACHE_SERVER") is not None:
        print("clcache-server is enabled")
    else:
        print("clcache-server is disabled")

    prefFile = MSBUILD_USER_SETTINGS_DIR + "\\Microsoft.Cpp.Win32.user.props"
    isEnabled = False
    with open(prefFile, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "<CLToolExe>clcache.exe</CLToolExe>" in line:
                isEnabled = True
    if isEnabled:
        print("clcache is *ENABLED* in " + MSBUILD_USER_SETTINGS_DIR)
    else:
        print("clcache is *NOT ENABLED* in " + MSBUILD_USER_SETTINGS_DIR)

    cl = env_utils.readEnvVariableFromRegistry("CLCACHE_CL")
    print("CLCACHE_CL (real compiler) is :" + cl)
    print("call clcache -s for statistics")
    return True


def makeInitialChecks():
    if not env_utils.hasProgramInPath("python"):
        print("This program needs python 3")
        return False
    if not env_utils.hasProgramInPath("pip"):
        print("This program needs pip 3")
        return False

    if not "python 3" in env_utils.callCmdGetOutput("python --version").lower():
        print("Bad python version : this program needs python 3")
        return False

    if not "python 3" in env_utils.callCmdGetOutput("pip --version").lower():
        print("Bad pip version : this program needs pip for python 3")
        return False

    pipScriptsDir = env_utils.pipScriptsDir()
    if pipScriptsDir.lower() not in env_utils.readPathFromRegistry().lower():
        print("Can't find pip_scripts_dir in your PATH. pip_scripts_dir=" + pipScriptsDir)
        print("Please add this to your PATH")
        return False
    return True


def selectCl():
    env_utils.showFunctionIntro("Select cl compiler:")
    clExesList = locate_cl_exe.findClExesList()
    helpStr = """Below is the list of the available cl.exe versions for your different installations
of Microsoft Visual Studio.
    Notes: 
    * Versions
        - Version 10.0 corresponds to MSVC 2010
        - Version 11.0 corresponds to MSVC 2012
        - Version 12.0 corresponds to MSVC 2013
        - Version 14.0 corresponds to MSVC 2015
        - Versions 15.* correspond to MSVC 2017
    * targetArch is the arch you are targeting
    * hostArch is the arch of your installation of Visual Studio 
      (select x86 most of the times)
    * the folder presented below are somewhat abbreviated
    """
    print(helpStr)
    locate_cl_exe.printClList(clExesList)
    while True:
        answer = input("Enter the number corresponding to the desired compiler: ")
        try:
            nb = int(answer)
        except ValueError:
            print("Enter a number between 1 and " + str(len(clExesList)))
            continue
        if nb >= 1 and nb <= len(clExesList):
            clExe = clExesList[nb - 1].installDir + "\\cl.exe"
            print("Selected : " + clExe)
            env_utils.setAndStoreEnvVariable("CLCACHE_CL", clExe)
            return True
        else:
            print("Enter a number between 1 and " + str(len(clExesList)))
    return False


def fullClcacheSetup():
    if not cloneClCache():
        return False
    if not installClcache():
        return False
    if not selectCl():
        return False
    if not copyMsvcPrefClcache():
        return False
    if not showClCacheUsage():
        return False
    return True


def enableServer():
    """
    will enable the clache-server, start it,
    and make sure that it starts when your computer starts.
    """
    env_utils.setAndStoreEnvVariable("CLCACHE_SERVER", "1")

    env_utils.runProcessDetached(env_utils.pipScriptsDir() + "\\clcache-server.exe")

    dstFolder = winshell.startup()
    dst = dstFolder + "\\clache-server.lnk"
    src = env_utils.pipScriptsDir() + "\\clcache-server.exe"
    env_utils.createShortcut(src, dst)
    return True


def disableServer():
    """
    will disable the clcache-server and remove it from the startup programs.
    Note : this does not kil the clcache-server.exe process,
    however subsequent builds will not use it.
    """
    if env_utils.readEnvVariableFromRegistry("CLCACHE_SERVER") is not None:
        env_utils.removeEnvVariable("CLCACHE_SERVER")

    dstFolder = winshell.startup()
    dst = dstFolder + "\\clache-server.lnk"
    env_utils.removeFile(dst)
    return True


def main():
    epilog = r"""Actions summary:
    status         : Show the install status and tells if clcache is enabled    
    install:       : Install and enable clcache for msbuild integration
                     (will let you choose between the available cl.exe)
    enable :       : Enable clcache for msbuild:
                     Modifies the user msbuild preference files 
                     inside APPDATAPATHLOCAL\Microsoft\MSBuild\v4.0
    disable:       : Disable clcache
                     Modifies the user msbuild preference files 
                     inside APPDATAPATHLOCAL\Microsoft\MSBuild\v4.0
    enable_server  : will enable the clache-server, start it, 
                     and make sure that it starts when your computer starts.
    disable_server : will disable the clcache-server and remove it from the startup programs.
                     Note : this does not kil the clcache-server.exe process,
                     however subsequent builds will not use it.
    enable_logs    : Activate clcache logs during builds
    disable_logs   : Disable clcache logs during builds
    show_cl_list   : List available cl.exe compilers
    select_cl      : Choose which cl.exe to activate
    clone_clcache  : Clone clcache in the clcache/ subfolder 
                     (this step is done automatically during install)

What this script does:
**********************

* Check that python3 and pip3 are installed and are in the PATH
* Check that the pip installed scripts are in the PATH (PYTHONHOME\Scripts)
* Call `pip install .` from the repo and check that clcache is then in the PATH.
  `clcache` will subsequently be used from the PYTHONHOME\\Scripts directory.
* Modify the user msbuild preference files inside `APPDATAPATHLOCAL\Microsoft\MSBuild\v4.0`
  so that clcache becomes the default compiler. (These prefs are shared between MSVC 2010 to 2017).
* Find all cl.exes version on your computer (for MSVC 2010 to MSVC 2017), and allows you 
  to select the correct one, by showing a detailed list of their version and target architecture.
* Set the env variable `CLCACHE_CL` with the correct path to cl.exe

As additional options, this script can also 
* change the cache location
* change the cache size
* change the timeout CLCACHE_OBJECT_CACHE_TIMEOUT_MS

Caveat
******
since the msbuild preference files inside `APPDATAPATHLOCAL\Microsoft\MSBuild\v4.0` are shared
between different MSVC installations, clcache will be activated for all instances of MSVC.

    """
    epilog = epilog.replace("MSBUILD_USER_SETTINGS_DIR", MSBUILD_USER_SETTINGS_DIR)
    epilog = epilog.replace("APPDATAPATHLOCAL", env_utils.appDataPathLocal())
    helpTimeout = """clcache object cache timeout in seconds
    (increase if you have failures during your build)
    """
    parser = argparse.ArgumentParser(
        description="Configure clcache for use with msbuild",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog = "python -m clcache_msbuild_install"
        )
    choices = ["status", "install",
               "enable", "disable",
               "enable_server", "disable_server",
               "enable_logs", "disable_logs",
               "show_cl_list", "select_cl", "clone_clcache"]
    parser.add_argument("action", choices=choices, help="action")
    parser.add_argument("--cachedir", help="clcache directory")
    parser.add_argument("--cache_size", help="clcache size in Go", type=int, default=0)
    parser.add_argument("--clcache_timeout", help=helpTimeout, type=int, default=0)

    if sys.argv[0][-3:] == ".py":
        argv = sys.argv[1:]
    else:
        argv = sys.argv
    args = parser.parse_args(argv)

    if args.action == "status":
        if not showStatus():
            return False
    elif args.action == "install":
        if not makeInitialChecks():
            return False
        if not fullClcacheSetup():
            return False
    elif args.action == "enable":
        if not copyMsvcPrefClcache():
            return False
    elif args.action == "disable":
        if not copyMsvcPrefOriginal():
            return False
    elif args.action == "enable_server":
        if not enableServer():
            return False
    elif args.action == "disable_server":
        if not disableServer():
            return False
    elif args.action == "enable_logs":
        if not env_utils.setAndStoreEnvVariable("CLCACHE_LOG", "1"):
            return False
    elif args.action == "disable_logs":
        if not env_utils.removeEnvVariable("CLCACHE_LOG"):
            return False
    elif args.action == "show_cl_list":
        locate_cl_exe.printClList(locate_cl_exe.findClExesList())
        return True
    elif args.action == "select_cl":
        if not selectCl():
            return False
    elif args.action == "clone_clcache":
        if not cloneClCache():
            return False
    if args.cachedir is not None:
        env_utils.setAndStoreEnvVariable("CLCACHE_DIR", args.cachedir)

    if args.cache_size > 0:
        giga = 1024 * 1024 * 1024
        byteSize = giga * args.cache_size
        if not env_utils.callAndShowCmd("clcache -M " +str(byteSize)):
            return False

    if args.clcache_timeout > 0:
        timeMs = args.clcache_timeout * 1000
        env_utils.setAndStoreEnvVariable("CLCACHE_OBJECT_CACHE_TIMEOUT_MS", str(timeMs))

    return True


if __name__ == "__main__":
    if not main():
        print("FAILURE")
        sys.exit(1)
