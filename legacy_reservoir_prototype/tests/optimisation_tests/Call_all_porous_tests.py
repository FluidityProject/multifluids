# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 15:43:05 2014

@author: pablo
"""

import sys
import time
import os, subprocess

def getLog(path):
    #Returns the physical line and line to which certain edge belong
    a=open(path,'rb')
    lines = a.readlines()
    if lines:
        last_line = lines[-1]
    
    a.close()
    return last_line 

#Code starts here!

start = time.time()

path = os.getcwd()
binpath = path[:path.index('legacy_reservoir_prototype')] + 'bin/multiphase_prototype'


print 'Running the BL with gravity test case (in a second cpu)'
#os.chdir(path + '/BL_with_gravity/')
#os.system('python' +' *.py > log')
#We run in parallel this experiment because it is slower than the sum of the other three
p =subprocess.Popen('python' +' *.py > log', shell=True, cwd=path + '/BL_with_gravity/')


print 'Running the BL test case'
os.chdir(path + '/BL_fast/')
os.system('python' +' *.py > log')
#subprocess.Popen('python' +' *.py > log', shell=True, cwd=path + '/BL_fast/')

print 'Running the thicker BL test case'
os.chdir(path + '/BL_fast_thicker/')
os.system('python' +' *.py > log')

print 'Running the gravity-capillarity test case (in a second cpu)'
#os.chdir(path + '/Grav_cap_competing_fast/')
#os.system('python' +' *.py > log')
p =subprocess.Popen('python' +' *.py > log', shell=True, cwd=path + '/Grav_cap_competing_fast/')


#Wait until the BL with gravity finish
p.communicate()

#Now we show the results
logpath = path + '/BL_fast/log'
print getLog(logpath)

logpath = path + '/BL_fast_thicker/log'
print getLog(logpath)

logpath = path + '/Grav_cap_competing_fast/log'
print getLog(logpath)

logpath = path + '/BL_with_gravity/log'
print getLog(logpath)

end = time.time()
print 'Required time(s):',  end - start
