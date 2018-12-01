#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
example.py

This script acquires camera images in a continuous loop.

The IP-address, the https-port, and user login are specified in the script.
Please change these settings.

The acquisition interval is 10 seconds (can be changed)

This example demonstrates the usage of functions to handle "exposure level",
drawing text on the image and downloading the image. For more functions, have a
look in the module.

Parameters which have to be set before usage:

IP-address of camera (camera_ip)
https-port (camera_port)
directory for images (outdir)
string for optional text (textstring)

It uses the camera module and its methods.

Note: The script is written to run operationally and continuously. In order to
provide stable image acquisition, it should be run as a regular cronjob
, e.g. once per minute. The process id file (pid) helps to check if the process
is still running to avoid multiple instances.


TS 09/2015
"""
import sys, os, shutil

from datetime import datetime, timedelta
import time

# the camera module
import camera

HOME = os.getenv('HOME')

# pid
pidfile = HOME + os.sep + '.cam_roof_g.pid'

# camera configuration
camera_ip = '192.168.135.3'
camera_port = 443
camera_user = None
camera_pass = None

# location
latitude = 53.13
longitude = 8.13

# acquisition interval
interval = 10

# Day / Night mode (no image download for zenithal angles > sza_max)
day_night = False
sza_max = 95

# Image  directory
outdir = "your-output-directory"

# text to be drawn in image corner
textstring = "My Location"


if __name__ == "__main__":


    # Check if another instance is still running
    if os.path.exists(pidfile):
        # read pid
        with open(pidfile, 'r') as f:
            pid = int(f.read())
        # check if there is a process with pid running
        if os.path.exists('/proc/%d' % pid):
            sys.exit(0)
        os.remove(pidfile)

    pid = os.getpid()
    with open(pidfile, 'w') as f:
        f.write(str(pid))

    # Current date and time
    dt = datetime.utcnow()

    # initialise camera connection
    cam = camera.vivotek(ip=camera_ip, port=camera_port, user=camera_user, passwd=camera_pass)
    #cam = camera.mobotix(ip=camera_ip, port=camera_port, user=camera_user, passwd=camera_pass)

    # set exposure level to -0.0
    cam.set_exposure_level(6)

    while 1:

        # wait until next interval
        now = datetime.utcnow().second + datetime.utcnow().microsecond/1e6
        wait_time = interval - now % interval
        if wait_time < 0: continue
        time.sleep(wait_time)
        dt = datetime.utcnow()

        # Day/Night mode
        solar_data = camera.solar_data([dt], latitude, longitude)
        if day_night and solar_data['zenith'][0] > sza_max: continue

        # current temporary file
        fname = outdir + os.sep + 'current.jpg'

        # download image
        img = cam.download_image_to_file(filename=fname)

        # archive directory
        dname = outdir + os.sep + dt.strftime("%Y%m%d")
        if not os.path.exists(dname): os.makedirs(dname)

        # draw text (date+time and location)
        img, draw = cam.addText(fname, dt=dt, loc=textstring)
        img.save(fname)

        # archive filename
        archiv = dt.strftime("%Y%m%d_%H%M%S.jpg")

        # save/archive image
        shutil.copy(fname, dname + os.sep + archiv)


    os.remove(pidfile)
