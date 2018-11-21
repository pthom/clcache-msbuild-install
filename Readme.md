# clcache msbuild install utility

Quick and easy integration of clcache with msbuild and Visual Studio.


This repository is an helper tool in order to easily integrate [clcache][1] with msbuild, so that it can be used from inside Visual Studio, or using cmake's "Visual Studio" generators. 

It is compatible with MSVC 2010, 2015 and 2017 (tested with MSVC 2015 and 2017).

 Notes: 
 * [clcache][1] is a compiler cache for `cl.exe`, much like ccache for gcc and clang
 * My tests showed that on a project with 600000 lines of code, it can reduce the compilation time from 25 minutes down to 4 minutes, when doing a full rebuild with no source modifications (i.e only cache hits)

### Difference with the original clcache

The original clcache has issues with incremental builds, when used in conjonction with msbuild. You will always get a full rebuild even if you modify only one file ! There is a pull request that succesfully correct this here: https://github.com/frerich/clcache/pull/319/commits

This tool uses a fork (https://github.com/pthom/clcache/tree/clcache-msbuild-install), which contains this correction.

# Usage

## Prerequisites
* python 3 and pip 3 must be installed and in your PATH. The pip scripts must also be in your PATH (PYTHONHOME\\Scripts).
* At least one install of Visual Studio (2010 to 2017)

## Installation

```bash
git clone https://github.com/pthom/clcache-msbuild-install.git
cd clcache-msbuild-install
pip install -r requirements.txt
```

## Usage & help

### One step 
The easiest way to use it is :
````
python path\to\clcache-msbuild-install\main.py install
````

### Detailed usage
````
> python path\to\clcache-msbuild-install\main.py -h
usage: python clcache-msbuild-install\main.py [-h] [--cachedir CACHEDIR]
                                              [--cache_size CACHE_SIZE]
                                              [--clcache_timeout CLCACHE_TIMEOUT]
                                              {status,install,enable,disable,enable_server,disable_server,enable_logs,disable_logs,show_cl_list,select_cl,clone_clcache}

Configure clcache for use with msbuild

positional arguments:
  {status,install,enable,disable,enable_server,disable_server,enable_logs,disable_logs,show_cl_list,select_cl,clone_clcache}
                        action

optional arguments:
  -h, --help            show this help message and exit
  --cachedir CACHEDIR   clcache directory
  --cache_size CACHE_SIZE
                        clcache size in Go
  --clcache_timeout CLCACHE_TIMEOUT
                        clcache object cache timeout in seconds (increase if
                        you have failures during your build)

Actions summary:
    status         : Show the install status and tells if clcache is enabled
    install:       : Install and enable clcache for msbuild integration
                     (will let you choose between the available cl.exe)
    enable :       : Enable clcache for msbuild:
                     Modifies the user msbuild preference files
                     inside C:\Users\pascal\AppData\Local\Microsoft\MSBuild\v4.0
    disable:       : Disable clcache
                     Modifies the user msbuild preference files
                     inside C:\Users\pascal\AppData\Local\Microsoft\MSBuild\v4.0
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

````

## What this tool does:
* Clone clcache (into clcache/)
* Check that python3 and pip3 are installed and are in the PATH
* Check that the pip installed scripts are in the PATH (PYTHONHOME\Scripts)
* Call `pip install .` from the ./clcache and check that clcache is then in the PATH.
  `clcache` will subsequently be used from the PYTHONHOME\\Scripts directory.
* Modify the user msbuild preference files inside `%AppData%\..\Local\Microsoft\MSBuild\v4.0`
  so that clcache becomes the default compiler. (These prefs are shared between MSVC 2010 to 2017).
* Find all cl.exes version on your computer (for MSVC 2010 to MSVC 2017), and allows you 
  to select the correct one, by showing a detailed list of their version and target architecture.
* Set the env variable `CLCACHE_CL` with the correct path to cl.exe

As additional options, this script can also 
* change the cache location
* change the cache size
* change the timeout CLCACHE_OBJECT_CACHE_TIMEOUT_MS

## Caveat 
Since the msbuild preference files inside `%AppData%\..\Local\Microsoft\MSBuild\v4.0` are shared
between different MSVC installations, clcache will be activated for all instances of MSVC.

## Note
`vswhere.exe` is a tool provided by Microsoft in order to locate installations of MSVC >= 2017.




# Sample usage session:

````
> python path\to\clcache-msbuild-install\main.py install
Looking for python in PATH
C:\Python36-32\python.exe
Looking for pip in PATH
C:\Python36-32\Scripts\pip.exe

######################################################################
Clone and update clcache repo (cloneClCache)
######################################################################
====> git checkout clcache-msbuild-install(in folder F:\dvp\OpenSource\clcache-msbuild-install\clcache)
Already on 'clcache-msbuild-install'
Your branch is up to date with 'origin/clcache-msbuild-install'.
====> git pull(in folder F:\dvp\OpenSource\clcache-msbuild-install\clcache)
Already up to date.

######################################################################
Installing clcache (installClcache)
######################################################################
====> pip install .(in folder F:\dvp\OpenSource\clcache-msbuild-install\clcache)
Processing f:\dvp\opensource\clcache-msbuild-install\clcache
Requirement already satisfied: pymemcache in c:\python36-32\lib\site-packages (from clcache==4.1.1.dev72+g09a364c) (2.0.0)
Requirement already satisfied: pyuv in c:\python36-32\lib\site-packages (from clcache==4.1.1.dev72+g09a364c) (1.4.0)
Requirement already satisfied: six in c:\python36-32\lib\site-packages (from pymemcache->clcache==4.1.1.dev72+g09a364c) (1.11.0)
Installing collected packages: clcache
  Found existing installation: clcache 4.1.1.dev72+g09a364c
    Uninstalling clcache-4.1.1.dev72+g09a364c:
      Successfully uninstalled clcache-4.1.1.dev72+g09a364c
  Running setup.py install for clcache ... done
Successfully installed clcache-4.1.1.dev72+g09a364c
You are using pip version 10.0.1, however version 18.1 is available.
You should consider upgrading via the 'python -m pip install --upgrade pip' command.
Looking for clcache in PATH
C:\Python36-32\Scripts\clcache.exe

######################################################################
Select cl compiler: (selectCl)
######################################################################
Below is the list of the available cl.exe versions for your different installations
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

   #           version targetArch   hostArch                                                              folder (shortened)
   1              14.0      amd64      amd64                                               C:\ProgX86\MSVC 14.0\vc\bin\amd64
   2              14.0        arm      amd64                                           C:\ProgX86\MSVC 14.0\vc\bin\amd64_arm
   3              14.0        x86      amd64                                           C:\ProgX86\MSVC 14.0\vc\bin\amd64_x86
   4              14.0      amd64        x86                                           C:\ProgX86\MSVC 14.0\vc\bin\x86_amd64
   5              14.0        arm        x86                                             C:\ProgX86\MSVC 14.0\vc\bin\x86_arm
   6              14.0        x86        x86                                                     C:\ProgX86\MSVC 14.0\vc\bin
   7   15.7.27703.2047        x64        x64       C:\ProgX86\MSVC\2017\Enterprise\VC\Tools\MSVC\14.14.26428\bin\Hostx64\x64
   8   15.7.27703.2047        x86        x64       C:\ProgX86\MSVC\2017\Enterprise\VC\Tools\MSVC\14.14.26428\bin\Hostx64\x86
   9   15.7.27703.2047        x64        x86       C:\ProgX86\MSVC\2017\Enterprise\VC\Tools\MSVC\14.14.26428\bin\Hostx86\x64
  10   15.7.27703.2047        x86        x86       C:\ProgX86\MSVC\2017\Enterprise\VC\Tools\MSVC\14.14.26428\bin\Hostx86\x86
Enter the number corresponding to the desired compiler: 6
Selected : C:\Program Files (x86)\Microsoft Visual Studio 14.0\vc\bin\cl.exe
====> SETX CLCACHE_CL "C:\Program Files (x86)\Microsoft Visual Studio 14.0\vc\bin\cl.exe"

SUCCESS: Specified value was saved.

######################################################################
Force clcache via Msbbuild user settings (copyMsvcPrefClcache)
######################################################################
Wrote pref in C:\Users\pascal\AppData\Local\Microsoft\MSBuild\v4.0\Microsoft.Cpp.ARM.user.props
Wrote pref in C:\Users\pascal\AppData\Local\Microsoft\MSBuild\v4.0\Microsoft.Cpp.Win32.user.props
Wrote pref in C:\Users\pascal\AppData\Local\Microsoft\MSBuild\v4.0\Microsoft.Cpp.x64.user.props

######################################################################
Note about clcache usage: (showClCacheUsage)
######################################################################
====> clcache --help
clcache.py v4.1.0-dev
  --help    : show this help
  -s        : print cache statistics
  -c        : clean cache
  -C        : clear cache
  -z        : reset cache statistics
  -M <size> : set maximum cache size (in bytes)
  ````

# Caveats with msbuild and clcache : 

## clcache is not compatible with `/Zi` debug information format : use `/Z7` instead.

See 
https://github.com/frerich/clcache/issues/30 
and https://stackoverflow.com/questions/284778/what-are-the-implications-of-using-zi-vs-z7-for-visual-studio-c-projects

With cmake, you can do the following:


  ```cmake
  message("msvc_clccache_force_z7_debug_format use /Z7 debug format")
  if(MSVC)
    string(REGEX REPLACE "/Z[iI7]" ""
           CMAKE_CXX_FLAGS_DEBUG
           "${CMAKE_CXX_FLAGS_DEBUG}")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Z7")
  endif()
  ````

[1]: https://github.com/frerich/clcache