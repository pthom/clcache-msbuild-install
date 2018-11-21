import ctypes
import winreg
import os
import os.path
import sys
import subprocess
import platform
# import winshell
from win32com.client import Dispatch

def createShortcut(src_file, dst_shortcut_path):
    path = os.path.join(dst_shortcut_path)
    wDir = os.path.dirname(src_file)
    icon = src_file
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = src_file
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()
    print("Created shortcut : {} points to {}".format(dst_shortcut_path, src_file))


def removeFile(filename):
    if os.path.exists(filename):
        os.remove(filename)
        print("Removed file " +  filename)
    else:
        print("Cannot remove " +  filename + " (does not exist)")


def runProcessDetached(command):
    pid = subprocess.Popen(command).pid
    print("Launched detached process with pid={} for command {}".format(pid, command))
    return pid


def shortDirectoryName(folder):
    result = folder
    result = result.replace("Program Files (x86)", "ProgX86")
    result = result.replace("Program Files", "Prog")
    result = result.replace("Microsoft Visual Studio", "MSVC")
    return result


def isOs64bit():
    return platform.machine().endswith('64')

def dirNameAbsolute(folder: str) -> str:
    return os.path.abspath(os.path.realpath(folder))


def fileDirNameAbsolute(file: str) -> str:
    return dirNameAbsolute(os.path.dirname(file))


def appDataPathLocal() -> str:
    result = dirNameAbsolute(os.getenv('APPDATA') + "\\..\\Local")
    return result

def isAdmin():
    return ctypes.windll.shell32.IsUserAnAdmin()


def currentFuncName(n=0):
    return sys._getframe(n + 1).f_code.co_name #pylint: disable=W0212


def showFunctionIntro(details=""):
    print()
    print("######################################################################")
    print(details + " (" + currentFuncName(1) + ")")
    print("######################################################################")


def hasProgramInPath(prog):
    print("Looking for " + prog + " in PATH")
    result = subprocess.call("where " + prog)
    if result != 0:
        print(prog + " not found in PATH")
    return result == 0


def hasDir(folder):
    return os.path.isdir(folder)


def whereProgram(prog: str) -> str:
    allProgrs = subprocess.check_output("where " + prog).decode("utf-8")
    firstProg = allProgrs.split("\r")[0]
    return firstProg


def whereProgramFolder(prog: str) -> str:
    progLocation = whereProgram(prog)
    return os.path.dirname(progLocation)


def pipScriptsDir():
    return whereProgramFolder("python") + "\\Scripts"


def showCmd(cmd):
    print("====> " + cmd)


def callAndShowCmd(command: str, cwd: str = None) -> bool:
    if cwd is not None:
        print("====> " + command + "(in folder " + cwd +  ")")
    else:
        print("====> " + command)
    if cwd is not None:
        return subprocess.call(command, cwd=cwd) == 0
    else:
        return subprocess.call(command) == 0


def callCmdGetOutput(command: str, cwd: str = None) -> str:
    return subprocess.check_output(command, cwd=cwd).decode("utf-8")


def implSetAndStoreEnvVariable(name, value, allUsers=False):
    if allUsers:
        cmd = "SETX {0} \"{1}\" /M".format(name, value)
    else:
        cmd = "SETX {0} \"{1}\"".format(name, value)
    if not callAndShowCmd(cmd):
        return False
    os.environ[name] = value
    return True


def setAndStoreEnvVariable(name, value):
    return implSetAndStoreEnvVariable(name, value, allUsers=isAdmin())


def implRemoveEnvVariable(name, allUsers=False):
    if allUsers:
        command = "REG DELETE HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment /F /V " + name
    else:
        command = "REG DELETE HKCU\\Environment /F /V " + name
    if not callAndShowCmd(command):
        return False
    if name is os.environ:
        os.environ.pop(name, None)
    return True


def removeEnvVariable(name):
    return implRemoveEnvVariable(name, allUsers=isAdmin())


def implReadRegistryValue(registryKind: int, keyName: str, valueName: str) -> str:
    reg = winreg.ConnectRegistry(None, registryKind)
    try:
        key = winreg.OpenKey(reg, keyName)
        result = winreg.QueryValueEx(key, valueName)
        return result[0]
    except FileNotFoundError:
        return None


def readRegistryValueLocalMachine(keyName: str, valueName: str) -> str:
    return implReadRegistryValue(winreg.HKEY_LOCAL_MACHINE, keyName, valueName)


def implReadEnvVariableFromRegistry(valueName, allUsers=False) -> str:
    if allUsers:
        keyName = "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"
        return implReadRegistryValue(winreg.HKEY_LOCAL_MACHINE, keyName, valueName)
    else:
        return implReadRegistryValue(winreg.HKEY_CURRENT_USER, "Environment", valueName)


def readEnvVariableFromRegistry(name):
    return implReadEnvVariableFromRegistry(name, allUsers=isAdmin())


def readPathFromEnvironment() -> str:
    return os.environ["PATH"]


def readPathFromRegistry() -> str:
    result = implReadEnvVariableFromRegistry("PATH", allUsers=False)
    result = result + ";" + implReadEnvVariableFromRegistry("PATH", allUsers=True)
    return result


def listFiles(folder, appendFolder=True):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if appendFolder:
        files = [os.path.join(folder, f) for f in files]
    return files


def listSubdirs(folder, appendFolder=True):
    files = [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
    if appendFolder:
        files = [os.path.join(folder, f) for f in files]
    return files
