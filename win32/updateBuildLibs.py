import codecs
import datetime
import logging
import os
import re
import shutil
import subprocess
import sys
from sys import platform as _platform

import time
import traceback

MSBUILD_PATH = os.path.normpath("c:/Program Files (x86)/MSBuild/14.0/Bin/MSBuild.exe")

def pullAndBuildAllDependencies(branch):
    '''
        Compile libewf, libvhdi, libvmdk.
        Args:
            branch: String, which branch to compile (currently only support master)
    '''
    # Passed is a global variable that gets set to false
    # When an error occurs
    global passed
    passed = True

    # get the LIBEWF_HOME, LIBVHDI_HOME, LIBVMDH_HOME
    ewfHome = os.getenv("LIBEWF_HOME", "C:\\libewf_64bit")
    vhdiHome = os.getenv("LIBVHDI_HOME", "C:\\libvhdi_64bit")
    vmdkHome = os.getenv("LIBVMDK_HOME", "C:\\libvmdk_64bit")

    # check if ewfHome, vhdiHome or vmdhHome exits
    checkPathExist(ewfHome)
    checkPathExist(vhdiHome)
    checkPathExist(vmdkHome)
    # git update libewf, libvhdi and libvmdk
    if(passed):
        gitPull(ewfHome, "libewf_64bit", branch)
    if(passed):
        gitPull(vhdiHome, "libvhdi_64bit", branch)
    if(passed):
        gitPull(vmdkHome, "libvmdk_64bit", branch)

    # build 32-bit of libewf, libvhdi, libvmdk and TSK 
    if(passed): 
        buildDependentLibs(ewfHome, 32, "libewf")
    if(passed): 
        buildDependentLibs(vhdiHome, 32, "libvhdi")
    if(passed): 
        buildDependentLibs(vmdkHome, 32, "libvmdk")


    # build 64-bit of libewf, libvhdi, libvmdk and TSK 
    if(passed): 
        buildDependentLibs(ewfHome, 64, "libewf")
    if(passed): 
        buildDependentLibs(vhdiHome, 64, "libvhdi")
    if(passed): 
        buildDependentLibs(vmdkHome, 64, "libvmdk")


def buildTSKAll():
    if(passed):
        buildTSK(32, "Release")
    if(passed):
        buildTSK(32, "Release_NoLibs")
    if(passed):
        buildTSK(32, "Release_PostgreSQL")

    if(passed):
        buildTSK(64, "Release")
    if(passed):
        buildTSK(64, "Release_NoLibs")
    if(passed):
        buildTSK(64, "Release_PostgreSQL")

def checkPathExist(path):
    global passed

    if not os.path.exists(path):
        print (path + " not exist.")
        sys.stdout.flush()
        passed = False

def gitPull(libHome, repo, branch):
    '''
        Pull the latest code.
        Args:
            libHome: according the environment variable to get the location
            repo String of repository ("libewf_64bit", "libvmdk_64bit" or "libvhdi_64bit" which one to pull
            branch: String, which branch to pull
    '''

    global SYS
    global passed
    oldPath = os.getcwd()

    # save the build log in the output directory
    logPath = os.path.join(oldPath, "output")
    if not os.path.exists(logPath):
        os.makedirs(logPath)

    gppth = os.path.join(logPath, "GitPullOutput" + repo + ".txt")
    gpout = open(gppth, 'a')


    print("Resetting " + repo)
    sys.stdout.flush()
    call = ["git", "reset", "--hard"]
    ret = subprocess.call(call, stdout=sys.stdout, cwd=libHome)

    if ret != 0:
        passed = False
        return

    print("Checking out " + branch)
    sys.stdout.flush()
    call = ["git", "checkout", branch]
    ret = subprocess.call(call, stdout=sys.stdout, cwd=libHome)

    if ret != 0:
        passed = False
        return

    call = ["git", "pull"]
    print("Pulling " + repo + "/" + branch)
    sys.stdout.flush()
    ret = subprocess.call(call, stdout=sys.stdout, cwd=libHome)

    if ret != 0:
        passed = False

    gpout.close()
    if passed:
        print("Update " + repo + " successfully.")
    else:
        print("Update " + repo + " failed.")

def buildDependentLibs(libHome, wPlatform, targetDll):
    '''
        build libewf.dll, libvhdi.dll and libvmdk.dll
    '''
    global passed
    passed = True
 
    print("Building " + str(wPlatform) + "-bit " + targetDll)
    sys.stdout.flush()

    target = "Release"
    oldPath = os.getcwd()

    # save the build log in the output directory
    logPath = os.path.join(oldPath, "output")
    if not os.path.exists(logPath):
        os.makedirs(logPath)

    if wPlatform == 64:
        dllFile = os.path.join(libHome, "msvscpp", "x64", target, targetDll +".dll")
    elif wPlatform == 32: 
        dllFile = os.path.join(libHome, "msvscpp", target, targetDll +".dll")
    else:
        print("Invalid platform")
        sys.stdout.flush()
        passed = False
        return

    if (os.path.isfile(dllFile)):
        os.remove(dllFile)

    os.chdir(os.path.join(libHome, "msvscpp"))

    vs = []
    vs.append(MSBUILD_PATH)
    vs.append(os.path.join(targetDll + ".sln"))
    vs.append("/p:configuration=" + target)
    if wPlatform == 64:
        vs.append("/p:platform=x64")
    elif wPlatform == 32:
        vs.append("/p:platform=Win32")
    vs.append("/t:clean")
    vs.append("/t:build")

    outputFile = os.path.join(logPath, targetDll + "Output.txt")
    VSout = open(outputFile, 'w')
    ret = subprocess.call(vs, stdout=VSout)
    errorCode = ret
    VSout.close()
    if ret > 0:
        failed_proj = os.system("grep 'Done Building Project' " + outputFile + " | grep vcxproj |grep FAILED |wc -l |cut -f1 -d' '")
        failed_pyewf = os.system("grep 'Done Building Project' " + outputFile + " | grep pyewf |grep FAILED |grep pywc -l |cut -f1 -d' '")
        if failed_proj == failed_pyewf:
            errorCode = 0
    if errorCode != 0 or not os.path.exists(dllFile) or os.path.getctime(dllFile) < (time.time() - 2 * 60): # the new dll should not be 2 mins old
        print(targetDll + " " + str(wPlatform) + "-bit C++ failed to build.\n")
        print("return code: " + str(ret) + "\tdll file: " + dllFile + "\tcreated time: " + str(os.path.getctime(dllFile))) 
        sys.stdout.flush()
        passed = False
        os.chdir(oldPath)
        return
    else:
        print("Build " + str(wPlatform) + "-bit " + targetDll + " successfully")
 
    os.chdir(oldPath)
 
def buildTSK(wPlatform, target):
    '''
        Build C++ sleuthkit library
    '''
    global passed

    print ("Building TSK " + str(wPlatform) + "-bit " + target + " build.")
    sys.stdout.flush()

    vs = []
    vs.append(MSBUILD_PATH)
    vs.append(os.path.join("tsk-win.sln"))
    vs.append("/p:configuration=" + target)
    if wPlatform == 64:
        vs.append("/p:platform=x64")
    elif wPlatform == 32:
        vs.append("/p:platform=Win32")
    else:
        print("Invalid platform")
        sys.stdout.flush()
        passed = False
        return
    vs.append("/t:clean")
    vs.append("/t:build")

    # save the build log in the output directory
    logPath = os.path.join(os.getcwd(), "output")
    if not os.path.exists(logPath):
        os.makedirs(logPath)

    outputFile = os.path.join(logPath, "TSKOutput.txt")
    VSout = open(outputFile, 'w')
    ret = subprocess.call(vs, stdout=VSout)
    VSout.close()
    if ret != 0:
        print("ret = " + str(ret))
        print(vs)
        print("LIBTSK " + str(wPlatform) + "-bit C++ failed to build.\n")
        sys.stdout.flush()
        passed = False
        return


def usage():
    '''
    Print out how to use this script.
    '''
    print('Usage: python3 updataBuildlibs.py branch product')
    print('branch is which branch to build. Must exist libewf, libvhdi and libvmdk.')
    sys.stdout.flush()
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print('Missing arguments.')
        usage()

    branch = sys.argv[1]

    pullAndBuildAllDependencies(branch)
    buildTSKAll()

class OS:
  LINUX, MAC, WIN, CYGWIN = range(4)
if __name__ == "__main__":
    global SYS
    if _platform == "linux" or _platform == "linux2":
        SYS = OS.LINUX
    elif _platform == "darwin":
        SYS = OS.MAC
    elif _platform == "win32":
        SYS = OS.WIN
    elif _platform == "cygwin":
        SYS = OS.CYGWIN

    global passed
    if SYS is OS.WIN or SYS is OS.CYGWIN:
        passed = True
        main()
    else:
        passed = False
        print("We only support Windows and Cygwin at this time.")
        sys.stdout.flush()

    if (passed):
        sys.exit(0)
    else:
        sys.exit(1)

#/cygdrive/c/Program\ Files\ \(x86\)/MSBuild/14.0/Bin/MSBuild.exe libewf.sln /p:Configuration=Release /p:platform=x64 /t:clean /t:libewf_dll /m /clp:ErrorsOnly /nologo
