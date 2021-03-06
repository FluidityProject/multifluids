#!/usr/bin/env python

import glob
import sys
import os
import vtktools
import numpy
import pylab
import re

def get_filelist():

    def key(s):
        return int(s.split('_')[-1].split('.')[0])
   
    list = glob.glob("*vtu")
    list = [l for l in list if 'check' not in l]
    vtu_nos = [float(s.split('_')[-1].split('.')[0]) for s in list]
    vals = zip(vtu_nos, list)
    vals.sort()
    unzip = lambda l:tuple(apply(zip,l))
    vtu_nos, list = unzip(vals)

    return list

#### taken from http://www.codinghorror.com/blog/archives/001018.html  #######
def tryint(s):
    try:
        return int(s)
    except:
        return s
    
def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)
##############################################################################
# There are shorter and more elegant version of the above, but this works
# on CX1, where this test might be run...

###################################################################

# Reattachment length:
def reatt_length(filelist, yarray, exclude_initial_results):

  print "Calculating reattachment point locations using change of x-velocity sign\n"
  print "Processing output files...\n"
  nums=[]; results=[]
  files = []

  ##### check for no files
  if (len(filelist) == 0):
    print "No files!"
    sys.exit(1)
  for file in filelist:
    try:
      os.stat(file)
    except:
      print "No such file: %s" % file
      sys.exit(1)
    num = int(re.split("\.p?vtu", file)[0].split('_')[-1])
    ##### Exclude data from simulation spin-up time
    if num > exclude_initial_results:
        print file
        files.append(file)

  

  sort_nicely(files)

  for file in files:

    print file
    ##### Read in data from vtu
    datafile = vtktools.vtu(file)

    ##### points near bottom surface, 0 < x < 25
    x2array=[]; pts=[]; no_pts = 52; offset = 0.1
    x = 0.0
    for i in range(1, no_pts):
      x2array.append(x)
      for j in range(len(yarray)):
        pts.append((x, yarray[j], offset))
      x += 0.5

    x2array = numpy.array(x2array)
    pts = numpy.array(pts)

    ##### Get x-velocity on bottom boundary
    uvw = datafile.ProbeData(pts, "Velocity")
    u = uvw[:,0]
    u = u.reshape([x2array.size,yarray.size])

    ##### Find all potential reattachment points:
    points = []
    for j in range(len(u[0,:])):
      for i in range(len(u[:,0])-1):
        ##### Hack to ignore division by zero entries in u.
        ##### All u should be nonzero away from boundary!
        if((u[i,j] / u[i+1,j]) < 0. and not numpy.isinf(u[i,j] / u[i+1,j])):
          ##### interpolate between nodes
          p = x2array[i] + (x2array[i+1]-x2array[i]) * (0.0-u[i,j]) / (u[i+1,j]-u[i,j])
          ##### Ignore spurious corner points
          if(p>0.1):
            points.append(p)

    ##### This is the spanwise-averaged reattachment point:
    avpt = sum(points) / len(points)
    ##### Get time for plot:
    t = min(datafile.GetScalarField("Time"))
    results.append([avpt,t])

  return results

#########################################################################

# Velocity profiles:
def meanvelo(filelist,xarray,yarray,zarray):

  print "\nRunning velocity profile script on files at times...\n"
  ##### check for no files
  if (len(filelist) < 0):
    print "No files!"
    sys.exit(1)

  ##### create array of points
  pts=[]
  for i in range(len(xarray)):
    for j in range(len(yarray)):
      for k in range(len(zarray)):
        pts.append([xarray[i], yarray[j], zarray[k]])
  pts=numpy.array(pts)

  ##### Create output array of correct shape
  files = 3; filecount = 0
  profiles = numpy.zeros([files, xarray.size, zarray.size], float)

  for file in filelist:
    try:
      os.stat(file)
    except:
      f_log.write("No such file: %s" % files)
      sys.exit(1)

    ##### Only process these 3 datafiles:
    vtu_no = float(file.split('_')[-1].split('.')[0])
    if (vtu_no == 6 or vtu_no == 11 or vtu_no == 33):

      datafile = vtktools.vtu(file)
      t = min(datafile.GetScalarField("Time"))
      print file, ', elapsed time = ', t

      ##### Get x-velocity
      uvw = datafile.ProbeData(pts, "Velocity")
      umax = max(abs(datafile.GetVectorField("Velocity")[:,0]))
      u = uvw[:,0]/umax
      u = u.reshape([xarray.size,yarray.size,zarray.size])

      ##### Spanwise averaging
      usum = numpy.zeros([xarray.size,zarray.size],float)
      usum = numpy.array(usum)
      for i in range(len(yarray)):
        uav = u[:,i,:]
        uav = numpy.array(uav)
        usum += uav
      usum = usum / len(yarray)
      profiles[filecount,:,:] = usum

      ##### reset time to something big to prevent infinite loop
      t = 100.
      filecount += 1

  print "\n...Finished extracting data.\n"
  return profiles

#########################################################################

def plot_length(reattachment_length):
  ##### Plot time series of reattachment length using pylab(matplotlib)
  plot1 = pylab.figure()
  pylab.title("Time series of reattachment length behind 3D step")
  pylab.xlabel('Time (s)')
  pylab.ylabel('Reattachment Length (L/h)')
  pylab.plot(reattachment_length[:,1], reattachment_length[:,0], marker = 'o', markerfacecolor='white', markersize=6, markeredgecolor='black', linestyle="solid")
  pylab.savefig("reattachment_length_3D.pdf")
  return

def plot_meanvelo(profiles,xarray,yarray,zarray):
  ##### Plot velocity profiles at different points behind step, and at 3 times using pylab(matplotlib)
  plot1 = pylab.figure(figsize = (16.5, 8.5))
  pylab.suptitle('Evolution of U-velocity profiles downstream of backward facing step', fontsize=30)

  size = 15
  ax = pylab.subplot(141)
  ax.plot(profiles[0,0,:],zarray, color='green', linestyle="dashed")
  ax.plot(profiles[1,0,:],zarray, color='blue', linestyle="dashed")
  ax.plot(profiles[2,0,:],zarray, color='red', linestyle="dashed")
  pylab.legend(("5secs", "10secs", "50secs"), loc="upper left")
  ax.set_title('(a) x/h = 4', fontsize=16)
  ax.grid("True")
  for tick in ax.xaxis.get_major_ticks():
    tick.label1.set_fontsize(size)
  for tick in ax.yaxis.get_major_ticks():
    tick.label1.set_fontsize(size)

  bx = pylab.subplot(142, sharex=ax, sharey=ax)
  bx.plot(profiles[0,1,:],zarray, color='green', linestyle="dashed")
  bx.plot(profiles[1,1,:],zarray, color='blue', linestyle="dashed")
  bx.plot(profiles[2,1,:],zarray, color='red', linestyle="dashed")
  pylab.legend(("5secs", "10secs", "50secs"), loc="upper left")
  bx.set_title('(b) x/h = 6', fontsize=16)
  bx.grid("True")
  for tick in bx.xaxis.get_major_ticks():
    tick.label1.set_fontsize(size)
  pylab.setp(bx.get_yticklabels(), visible=False)

  cx = pylab.subplot(143, sharex=ax, sharey=ax)
  cx.plot(profiles[0,2,:],zarray, color='green', linestyle="dashed")
  cx.plot(profiles[1,2,:],zarray, color='blue', linestyle="dashed")
  cx.plot(profiles[2,2,:],zarray, color='red', linestyle="dashed")
  pylab.legend(("5secs", "10secs", "50secs"), loc="upper left")
  cx.set_title('(c) x/h = 10', fontsize=16)
  cx.grid("True")
  for tick in cx.xaxis.get_major_ticks():
    tick.label1.set_fontsize(size)
  pylab.setp(cx.get_yticklabels(), visible=False)

  dx = pylab.subplot(144, sharex=ax, sharey=ax)
  dx.plot(profiles[0,3,:],zarray, color='green', linestyle="dashed")
  dx.plot(profiles[1,3,:],zarray, color='blue', linestyle="dashed")
  dx.plot(profiles[2,3,:],zarray, color='red', linestyle="dashed")
  pylab.legend(("5secs", "10secs", "50secs"), loc="upper left")
  dx.set_title('(d) x/h = 19', fontsize=16)
  dx.grid("True")
  for tick in dx.xaxis.get_major_ticks():
    tick.label1.set_fontsize(size)
  pylab.setp(dx.get_yticklabels(), visible=False)

  pylab.axis([-0.25, 1., 0., 2.])
  bx.set_xlabel('Normalised U-velocity (U/Umax)', fontsize=24)
  ax.set_ylabel('z/h', fontsize=24)

  pylab.savefig("velo_profiles_3d_parallel.pdf")
  return

#########################################################################

def main():
    ##### Points to generate profiles:
    xarray = numpy.array([4.0, 6.0, 10.0, 19.0])
    yarray = numpy.array([0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 3.9])
    zarray = numpy.array([0.01, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0])

    ##### Call reattachment_length function defined above
    filelist = get_filelist()
    reattachment_length = numpy.array(reatt_length(filelist, yarray, exclude_initial_results=40))
    av_length = sum(reattachment_length[:,0]) / len(reattachment_length[:,0])
    numpy.save("reattachment_length_3D", reattachment_length)
    print "\nTime-averaged reattachment length (in step heights): ", av_length
    plot_length(reattachment_length)

    ##### Call meanvelo function defined above

    profiles = meanvelo(filelist, xarray, yarray, zarray)
    numpy.save("velo_profiles_3d_parallel", profiles)
    print "Showing plot of velocity profiles.\nTo continue script, close plot window."
    plot_meanvelo(profiles,xarray,yarray,zarray)
    pylab.show()

    print "\nAll done.\n"

if __name__ == "__main__":
    sys.exit(main())

