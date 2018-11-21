#!/usr/bin/env python

import json
import typing
import os.path
import os
from . import env_utils

THIS_DIR = env_utils.fileDirNameAbsolute(__file__)


class MsvcInstall(object):
    version: str
    installDir: str
    def __init__(self, version, installDir):
        self.version = version
        self.installDir = installDir


class ClInfo(object):
    msvcInstall: MsvcInstall
    installDir: str
    hostArch: str
    targetArch: str
    def __init__(self, msvcInstall, installDir, hostArch, targetArch):
        self.msvcInstall = msvcInstall
        self.installDir = installDir
        self.hostArch = hostArch
        self.targetArch = targetArch
    def __str__(self):
        result = "version: " + self.msvcInstall.version + " hostArch:" \
                + self.hostArch + " targetArch:" + self.targetArch + " (" + self.installDir + ")"
        return result


def implFindMsvcUpTo2015() -> typing.List[MsvcInstall]:
    versions = ["8.0", "9.0", "10.0", "11.0", "12.0", "13.0", "14.0", "15.0"]
    if env_utils.isOs64bit():
        softwareSubkey = "SOFTWARE\\Wow6432Node"
    else:
        softwareSubkey = "SOFTWARE"
    keyTemplate = softwareSubkey + "\\Microsoft\\VisualStudio\\__VERSION__\\"

    result = []
    for version in versions:
        valueName = "InstallDir"
        key = keyTemplate.replace("__VERSION__", version)
        installDir = env_utils.readRegistryValueLocalMachine(key, valueName)
        if installDir is not None and os.path.isdir(installDir):
            result.append(MsvcInstall(version, installDir))
    return result


def implFindMsvc2017() -> typing.List[MsvcInstall]:
    jsonStr = env_utils.callCmdGetOutput(THIS_DIR + "\\..\\vswhere.exe -format json")
    jsonData = json.loads(jsonStr)
    result = []
    for entry in jsonData:
        result.append(
            MsvcInstall(entry["installationVersion"], entry["installationPath"]))
    return result


def findMsvc() -> typing.List[MsvcInstall]:
    return implFindMsvcUpTo2015() + implFindMsvc2017()


def implfindClExesForOldMsvc(msvcInstall: MsvcInstall) -> typing.List[ClInfo]:
    result = []
    mainClPath = env_utils.dirNameAbsolute(msvcInstall.installDir + "\\..\\..\\vc\\bin")
    if not os.path.isdir(mainClPath):
        return []
    subDirs = env_utils.listSubdirs(mainClPath, appendFolder=False) + ["."]
    def hasClExe(subdir):
        return os.path.isfile(mainClPath + "\\" + subdir + "\\cl.exe")
    dirsWithCl = [dir for dir in subDirs if hasClExe(dir)]
    # dirWithCl is something like
    # ['amd64', 'amd64_arm', 'amd64_x86', 'x86_amd64', 'x86_arm', '.']
    # in this ist : "." = x86_x86 and amd64 = amd64_amd64
    for dirWithCl in dirsWithCl:
        fullDir = env_utils.dirNameAbsolute(mainClPath + "\\" + dirWithCl)
        if dirWithCl == ".":
            hostArch = "x86"
            targetArch = "x86"
        elif dirWithCl == "amd64":
            hostArch = "amd64"
            targetArch = "amd64"
        else:
            tokens = dirWithCl.split("_")
            hostArch = tokens[0]
            targetArch = tokens[1]
        result.append(ClInfo(msvcInstall, fullDir, hostArch, targetArch))
    return result


def implfindClExesForMsvc2017(msvcInstall: MsvcInstall) -> typing.List[ClInfo]:
    result = []
    topDir = msvcInstall.installDir + "\\VC\\Tools\\MSVC"
    for dirpath, _, filenames in os.walk(topDir):
        for file in filenames:
            if file == "cl.exe":
                # dirpath looks like
                # c:\Program Files (x86)\...\bin\Hostx64\x64
                dirTokens = dirpath.split("\\")
                hostArch = dirTokens[-2].replace("Host", "")
                targetArch = dirTokens[-1]
                result.append(ClInfo(msvcInstall, dirpath, hostArch, targetArch))
    return result


def findClExesList() -> typing.List[ClInfo]:
    result = []
    msvcInstallOld = implFindMsvcUpTo2015()
    for msvcInstall in msvcInstallOld:
        result = result + implfindClExesForOldMsvc(msvcInstall)

    msvcInstallNew = implFindMsvc2017()
    for msvcInstall in msvcInstallNew:
        result = result + implfindClExesForMsvc2017(msvcInstall)

    return result


def printClList(clInfoList: typing.List[ClInfo]) -> str:
    def clInfoToData(clInfo: ClInfo):
        return [clInfo.msvcInstall.version, clInfo.targetArch,
                clInfo.hostArch, env_utils.shortDirectoryName(clInfo.installDir)]
    headers = ["#", "version", "targetArch", "hostArch", "folder (shortened)"]
    data = [clInfoToData(clInfo) for clInfo in clInfoList]
    rowFormat = "{:>4}{:>18}{:>11}{:>11}{:>80}"

    print(rowFormat.format(*headers))
    rowId = 1
    for version in data:
        print(rowFormat.format(rowId, *version))
        rowId = rowId + 1
