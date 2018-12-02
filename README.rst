Camera Handler
=======================

Camera handling package to acquire images and archive images and to set
camera settings via HTTP-commands for Vivotek and Mobotix (beta) Fisheye network cameras

The camera module src/camera.py contains all necessary modules for downloading images, regulate exposure levels, gains, etc.,
drawing text into images.

Install in your system with pip

 .. code::

    cd CAMERA_DIRECTORY
    pip install .

    or use

    cd CAMERA_DIRECTORY
    python setup.py build
    python setup.py install

There is one example script using the camera module for downloading and archiving images!

Have a look in the script, adapt the few parameters and start the script with your favorable Python version!

This package requires "Pillow"-package for image handling to be installed

install by using pip

 .. code::

    pip install pillow

Start the example script

 .. code::

    python example.py

    or

    chmod 755 example.py
    ./example.py



Example.py
=======================

This script acquires camera images with different settings for
day and night time

During day (zenith angle < 110°), it acquires images every 10 seconds with an exposure level 0.0
During night (zenith angle > 110°), it acquire one image with an exposure level -2.0

This script should be started as a cronjob every minute as it only download 6 images during day (10s interval)
and 1 image in the night (after 10s)

The script also draws some text (date and time and a string (e.g. location) in the corners of the image)

Parameters which have to be set before usage:

Latitude (latitude)
Longitude (longitude)
IP-address of camera (camera_ip)
directory for images (outdir)
string for optional text (textstring)

It uses the camera module and its methods.

TS 11/2018
