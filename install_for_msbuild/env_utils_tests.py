#!/usr/bin/env python
import os.path
import time
import unittest
import winshell
import env_utils
import locate_cl_exe

class EnvUtilsTests(unittest.TestCase):
    def testEnvVars(self):
        env_utils.setAndStoreEnvVariable("DUMMYVAR", "dummy")
        result = env_utils.readEnvVariableFromRegistry("DUMMYVAR")
        self.assertEqual(result, "dummy")
        env_utils.removeEnvVariable("DUMMYVAR")
        result = env_utils.readEnvVariableFromRegistry("DUMMYVAR")
        self.assertTrue(result is None)
    def testShortcut(self):
        pythonProg = env_utils.whereProgram("python")
        dstFolder = winshell.startup()
        dst = dstFolder + "\\python.lnk"
        env_utils.createShortcut(pythonProg, dst)
        self.assertTrue(os.path.exists(dst))
        os.remove(dst)
        self.assertTrue(not os.path.exists(dst))
    # def testRunProcessDetached(self):
    #     prog = env_utils.whereProgram("Calc.exe")
    #     pid = env_utils.runProcessDetached(prog)
    #     time.sleep(1)
    #     env_utils.callAndShowCmd("taskkill /PID {}".format(pid))



class LocateClTests(unittest.TestCase):
    def testFindfindMsvcUpTo2015(self):
        result = locate_cl_exe.implFindMsvcUpTo2015()
        self.assertTrue(len(result) > 0)
    def testFindMsvc2017(self):
        aux = locate_cl_exe.implFindMsvc2017()
        self.assertTrue(len(aux) >= 0)
    def testFindMsvc(self):
        aux = locate_cl_exe.findMsvc()
        self.assertTrue(len(aux) > 0)
    def testFindCl(self):
        aux = locate_cl_exe.findClExesList()
        self.assertTrue(len(aux) > 0)


if __name__ == '__main__':
    unittest.TestCase.longMessage = True
    unittest.main()
