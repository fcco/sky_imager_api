#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module is used to handle Vivotek fisheye lens camera.

It consists of methods in order to
    - retrieve images directly from the camera (download_image_to_file)
    - retrieve stream
    - set exposure level (set_exposure_level)
    - set gain (set_gain)
    - set IR cut mode (cut_filter_mode)
    - white balance, Red/Blue gain (white_balance)
    - draw basic text (date,time,location-string) to image (add_text)
    - calculate solar position (solar_data)


Package requirements:
    PIL, urllib

Please care about the access to the camera via command-line and set proxies
if needed.


Thomas Schmidt 05/2015

History:

08/2016 upgrade to python 3
"""

import urllib.request, urllib.error, urllib.parse
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import numpy as np
from numpy import pi, cos, sin, radians, degrees, arcsin, arccos
import ssl

__author__ = "Thomas Schmidt"
__copyright__ = "Copyright 2015, Universität Oldenburg"
__credits__ = ["Thomas Schmidt"]
__version__ = "0.2"
__date__ = "2016-08-12"
__maintainer__ = "Thomas Schmidt"
__email__ = "t.schmidt@uni-oldenburg.de"
__status__ = "Production"



class vivotek():
    """
    This methods are written for Vivotek FE8172V/FE8174V camera. The camera uses
    cgi-scripts to handle some settings like exposure time, gain, etc.
    Be careful to set only values that are accepted by the camera, otherwise
    nothing will happen or errors occur.
    """


    def __init__(self,ip="",port="",http=None,https=None,user="",passwd=""):
        if port != "":
            self.ip = ip + ':' + str(port)
        else:
            self.ip = ip
        self.image_url = "https://" + self.ip + "/cgi-bin/viewer/video.jpg"
        self.settings_url = "https://" + self.ip + "/cgi-bin/admin/setparam.cgi?"
        self.maxexposure = 5
        self.minexposure = 32000
        self.level = 6
        self.maxgain = 100
        self.mingain = 0
        self.redgain = 37
        self.bluegain = 30
        self.ssl_context = ""

        # These two lines should only be used in context with Vivotek cameras
        # due to old ssl versions
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ssl_context.set_ciphers('ALL')

        opprox = self._proxy(http=http,https=https)
        httpshandl = urllib.request.HTTPSHandler(context=ssl_context)

        if user != "":
            opauth = self._auth(user,passwd)
            opener = urllib.request.build_opener(httpshandl,opauth,opprox)
        else:
            opener = urllib.request.build_opener(httpshandl,opprox)

        self.opener = opener

        urllib.request.install_opener(self.opener)




    def _auth(self,user,passwd):
        """
        Setup basic http authentification

        Parameters
        ----------
        :params user: string, usernamer
        :params passwd: string, password

        Returns
        -------
        :returns handler: HTTP handler object

        Notes
        ------

        """
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None,'https://'+self.ip, user, passwd)
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

        return handler







    def _proxy(self,http='',https=''):
        """
        Sets the proxy for the requests.

        If http is None, the environment variable (if set)
        is overwritten by an empty dictionary -< No proxy is used.

        If http is empty (""), the default environment proxy is used

        If http is an address, the specified address is used

        Parameters:
        -----------

        :param http: string, optional, address of proxy
        :param https: string, optional, address of https proxy

        """
        if http == None:
            proxy = urllib.request.ProxyHandler({})
        elif http == "" and https == "":
            proxy = urllib.request.ProxyHandler({'http': os.getenv('http_proxy'), \
                'https': os.getenv('https_proxy') })
        else:
            http = urllib.request.ProxyHandler({'http': http})

        return proxy






    def set_exposure_time(self,maxexposure=-1, minexposure=-1):
        """
        Sets exposure time for Vivotek network camera

        Parameters
        -----------

        :param minexposure, maxexposure: int, optional

              Exposure time range
              Possible  values:
              5, 15, 25, 50, 100, 200, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000

        """
        if maxexposure < 0: maxexposure = self.maxexposure
        if minexposure < 0: minexposure = self.minexposure

        elist = [5, 15, 25, 50, 100, 200, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000]

        if not minexposure in elist or not maxexposure in elist:
            print( 'Exposure times out of possible values: Use one of these values:', elist, ' -> Exit')
            return False

        if maxexposure > minexposure:
            print( 'Maximum exposure time must be smaller than minimum exposure time:', \
                maxexposure, ' > ', minexposure, ' -> Exit')

        url = self.settings_url + "videoin_c0_maxexposure=" + str(maxexposure) + \
            "&videoin_c0_minexposure=" + str(minexposure)
        req = urllib.request.Request(url)
        try:
            urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print( 'The server couldn\'t fulfill the request -> ', e.code)
            raise
        except urllib.error.URLError as e:
            print('Fail in reaching the server -> ' ,e.reason)
            raise






    def set_exposure_level(self,level=-1):
        """
        Sets exposure level for Vivotek network camera

        Parameters
        -----------

        :param level: int, optional
              Exposure between 0-12, 6 is equal to neutral
              If level is not given, the default (=6) is set. Can be used to reset settings

        """
        if level < 0: level = self.level

        url = self.settings_url + "videoin_c0_exposurelevel=" + str(level)
        req = urllib.request.Request(url)
        try:
            urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print( 'The server couldn\'t fulfill the request -> ', e.code)
            raise
        except urllib.error.URLError as e:
            print('Fail in reaching the server -> ' ,e.reason)
            raise






    def cut_filter_mode(self,mode="day"):
        """
        Sets IR cut filter mode for Vivotek network camera

        Parameters
        -----------

        :param mode: str, optional
              IR cut mode: "day" (default), "night", "auto", "di", "schedule"
        """
        if mode not in ["day", "night", "auto", "di", "schedule"]:
            print( 'Mode ', mode , ' not allowed, choose one of: ' \
                "day", "night", "auto", "di", "schedule" ' -> do nothing')
            return
        url = self.settings_url + "ircutcontrol_mode=" + str(mode)
        req = urllib.request.Request(url)
        try:
            urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print( 'The server couldn\'t fulfill the request -> ', e.code)
            raise
        except urllib.error.URLError as e:
            print('Fail in reaching the server -> ' ,e.reason)
            raise






    def set_gain(self,maxgain=None, mingain=None):
        """
        Sets gain for Vivotek network camera

        Parameters
        -----------
        :params maxgain: int, optional, maximum gain, default 100
        :params mingain: int, optional, minimum gain, default 0

        """
        if not maxgain: maxgain = self.maxgain
        if not mingain: mingain = self.mingain

        urllib.request.urlopen(self.settings_url + "videoin_c0_maxgain=" + maxgain + \
            "&videoin_c0_mingain=" + mingain)





    def white_balance(self,redgain=None, bluegain=None):
        """
        Sets white balance for Vivotek network camera in manual mode
        Corresponds to browser settings in media -> image -> image settings ->
        white balance

        Parameters
        -----------
        :params redgain: int, optional, red color gain (range 0-100)
        :params bluegain: int, optional, blue color gain (range 0-100)

        """
        if redgain:
            urllib.request.urlopen(self.settings_url + "videoin_c0_rgain=" + str(redgain) )

        if bluegain:
            urllib.request.urlopen(self.settings_url + "videoin_c0_bgain=" + str(bluegain) )





    def download_image_to_file(self, filename = None ):
        """Store the url content to filename

        Parameters:
        -----------
        :param filename: string, optional

            path + filename for output image, if not given the basename of the url
            is used as filename and image is stored at current directory.

        :returns flag: boolean

            True if saving was successful, otherwise False
        """


        flag = False
        url = self.image_url

        if not filename:
            filename = os.path.basename( os.path.realpath(url) )
        resource = urllib.request.urlopen(url, timeout=5)

        with open(filename,"wb") as output:
            output.write( resource.read() )
            output.close()
            flag = True

        return flag





    def addText(self,img, dt=None, loc=""):
        """ Adds some text into the image ( timestamp, name )

        :params img: image object
        :params dt: datetime, optional, date and time to draw in image corners
        :params loc: string, optional, string to draw in image corner
         """

        image = Image.open(img)
        draw = ImageDraw.Draw(image)
        lx, ly = image.size

        # Font
        try:
            f = '/usr/share/fonts/liberation/LiberationSans-Bold.ttf'
            txtfont = ImageFont.truetype(f, 50)
        except:
            print('Font ' + f + ' could not be found!')
            txtfont = ""

        # Draw Timestring
        string = dt.strftime("%H:%M:%S %Z")
        if dt: draw.text((lx-350, 20),string,fill = 'red',font=txtfont)

        # Draw Datestring
        string = dt.strftime("%Y/%m/%d")
        if dt: draw.text((20, 20),string,fill = 'red',font=txtfont)

        # Draw Location
        string = loc
        draw.text((20, ly-80),string,fill = 'red',font=txtfont)

        return image, draw


class mobotix():
    """
    This methods are written for Mobotix camera. The camera uses
    cgi-scripts to handle some settings like exposure time, gain, etc.
    Be careful to set only values that are accepted by the camera, otherwise
    nothing will happen or errors occur.
    """


    def __init__(self,ip="",port="",http=None,https=None,user="",passwd=""):
        if port != "":
            self.ip = ip + ':' + str(port)
        else:
            self.ip = ip
        self.image_url = "https://" + self.ip + "/record/current.jpg"
        self.settings_url = "https://" + self.ip + "/cgi-bin/admin/setparam.cgi?"
        self.maxexposure = 5
        self.minexposure = 32000
        self.level = 6
        self.maxgain = 100
        self.mingain = 0
        self.redgain = 37
        self.bluegain = 30
        self.ssl_context = ""

        # These two lines should only be used in context with Vivotek cameras
        # due to old ssl versions
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        ssl_context.set_ciphers('ALL')

        opprox = self._proxy(http=http,https=https)
        httpshandl = urllib.request.HTTPSHandler(context=ssl_context)

        opener = urllib.request.build_opener(httpshandl,opprox)

        self.opener = opener

        urllib.request.install_opener(self.opener)


    def _proxy(self,http='',https=''):
        """
        Sets the proxy for the requests.

        If http is None, the environment variable (if set)
        is overwritten by an empty dictionary -< No proxy is used.

        If http is empty (""), the default environment proxy is used

        If http is an address, the specified address is used

        Parameters:
        -----------

        :param http: string, optional, address of proxy
        :param https: string, optional, address of https proxy

        """
        if http == None:
            proxy = urllib.request.ProxyHandler({})
        elif http == "" and https == "":
            proxy = urllib.request.ProxyHandler({'http': os.getenv('http_proxy'), \
                'https': os.getenv('https_proxy') })
        else:
            http = urllib.request.ProxyHandler({'http': http})

        return proxy


    def set_exposure_time(self,maxexposure=-1, minexposure=-1):
        """
        Sets exposure time for Vivotek network camera

        Parameters
        -----------

        :param minexposure, maxexposure: int, optional

              Exposure time range
              Possible  values:
              5, 15, 25, 50, 100, 200, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000

        """
        if maxexposure < 0: maxexposure = self.maxexposure
        if minexposure < 0: minexposure = self.minexposure

        elist = [5, 15, 25, 50, 100, 200, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000]

        if not minexposure in elist or not maxexposure in elist:
            print( 'Exposure times out of possible values: Use one of these values:', elist, ' -> Exit')
            return False

        if maxexposure > minexposure:
            print( 'Maximum exposure time must be smaller than minimum exposure time:', \
                maxexposure, ' > ', minexposure, ' -> Exit')

        url = self.settings_url + "videoin_c0_maxexposure=" + str(maxexposure) + \
            "&videoin_c0_minexposure=" + str(minexposure)
        req = urllib.request.Request(url)
        try:
            urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print( 'The server couldn\'t fulfill the request -> ', e.code)
            raise
        except urllib.error.URLError as e:
            print('Fail in reaching the server -> ' ,e.reason)
            raise






    def set_exposure_level(self,level=-1):
        """
        Sets exposure level for Vivotek network camera

        Parameters
        -----------

        :param level: int, optional
              Exposure between 0-12, 6 is equal to neutral
              If level is not given, the default (=6) is set. Can be used to reset settings

        """
        if level < 0: level = self.level

        url = self.settings_url + "videoin_c0_exposurelevel=" + str(level)
        req = urllib.request.Request(url)
        try:
            urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print( 'The server couldn\'t fulfill the request -> ', e.code)
            raise
        except urllib.error.URLError as e:
            print('Fail in reaching the server -> ' ,e.reason)
            raise






    def cut_filter_mode(self,mode="day"):
        """
        Sets IR cut filter mode for Vivotek network camera

        Parameters
        -----------

        :param mode: str, optional
              IR cut mode: "day" (default), "night", "auto", "di", "schedule"
        """
        if mode not in ["day", "night", "auto", "di", "schedule"]:
            print( 'Mode ', mode , ' not allowed, choose one of: ' \
                "day", "night", "auto", "di", "schedule" ' -> do nothing')
            return
        url = self.settings_url + "ircutcontrol_mode=" + str(mode)
        req = urllib.request.Request(url)
        try:
            urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print( 'The server couldn\'t fulfill the request -> ', e.code)
            raise
        except urllib.error.URLError as e:
            print('Fail in reaching the server -> ' ,e.reason)
            raise






    def set_gain(self,maxgain=None, mingain=None):
        """
        Sets gain for Vivotek network camera

        Parameters
        -----------
        :params maxgain: int, optional, maximum gain, default 100
        :params mingain: int, optional, minimum gain, default 0

        """
        if not maxgain: maxgain = self.maxgain
        if not mingain: mingain = self.mingain

        urllib.request.urlopen(self.settings_url + "videoin_c0_maxgain=" + maxgain + \
            "&videoin_c0_mingain=" + mingain)





    def white_balance(self,redgain=None, bluegain=None):
        """
        Sets white balance for Vivotek network camera in manual mode
        Corresponds to browser settings in media -> image -> image settings ->
        white balance

        Parameters
        -----------
        :params redgain: int, optional, red color gain (range 0-100)
        :params bluegain: int, optional, blue color gain (range 0-100)

        """
        if redgain:
            urllib.request.urlopen(self.settings_url + "videoin_c0_rgain=" + str(redgain) )

        if bluegain:
            urllib.request.urlopen(self.settings_url + "videoin_c0_bgain=" + str(bluegain) )





    def download_image_to_file(self, filename = None ):
        """Store the url content to filename

        Parameters:
        -----------
        :param filename: string, optional

            path + filename for output image, if not given the basename of the url
            is used as filename and image is stored at current directory.

        :returns flag: boolean

            True if saving was successful, otherwise False
        """


        flag = False
        url = self.image_url

        if not filename:
            filename = os.path.basename( os.path.realpath(url) )
        resource = urllib.request.urlopen(url, timeout=5)

        with open(filename,"wb") as output:
            output.write( resource.read() )
            output.close()
            flag = True

        return flag





    def addText(self,img, dt=None, loc=""):
        """ Adds some text into the image ( timestamp, name )

        :params img: image object
        :params dt: datetime, optional, date and time to draw in image corners
        :params loc: string, optional, string to draw in image corner
         """

        image = Image.open(img)
        draw = ImageDraw.Draw(image)
        lx, ly = image.size

        # Font
        try:
            f = '/usr/share/fonts/liberation/LiberationSans-Bold.ttf'
            txtfont = ImageFont.truetype(f, 50)
        except:
            print('Font ' + f + ' could not be found!')
            txtfont = ""

        # Draw Timestring
        string = dt.strftime("%H:%M:%S %Z")
        if dt: draw.text((lx-350, 20),string,fill = 'red',font=txtfont)

        # Draw Datestring
        string = dt.strftime("%Y/%m/%d")
        if dt: draw.text((20, 20),string,fill = 'red',font=txtfont)

        # Draw Location
        string = loc
        draw.text((20, ly-80),string,fill = 'red',font=txtfont)

        return image, draw







def solar_data(dates, lat, lon):
    """
    Simple solar position algorithm.

    :param dates: list of datetime objects (must be in UTC)
    :type dates: list

    :param lat: latitude (degrees)
    :type lat: float

    :param lon: longitude (degrees)
    :type lat: float

    :returns: dictionary with 'sza' - solar zenith angle (degrees)
                             'saz' - solar azimuth angle (degrees)
                             'INull' - extraterrestrial radiation (W/m^2)

    .. note::

        Formulas from Spencer (1972) and can be also found in "Solar energy
        fundamentals and modeling techniques" from Zekai Sen
    """

    dt_1600 = datetime(1600, 1, 1)

    # Compute julian dates relative to 1600-01-01 00:00.
    julians_1600 = (np.array([(dt - dt_1600).total_seconds()
            for dt in dates]) / (24 * 60 * 60))

    lat = radians(lat)
    lon = radians(lon)

    # Compute gamma angle from year offset and calculate some intermediates.
    Gamma = 2. * pi * (julians_1600 % 365.2425) / 365.2425
    cos_gamma = cos(Gamma), cos(Gamma * 2), cos(Gamma * 3)
    sin_gamma = sin(Gamma), sin(Gamma * 2), sin(Gamma * 3)
    DayTime = (julians_1600 % 1) * 24

    # Eccentricity: correction factor of the earth's orbit.
    ENull = (1.00011 + 0.034221 * cos_gamma[0] + 0.001280 * sin_gamma[0] +
            0.000719 * cos_gamma[1] + 0.000077 * sin_gamma[1])

    # Declination.
    Declination = (0.006918 - 0.399912 * cos_gamma[0] +
            0.070257 * sin_gamma[0] -
            0.006758 * cos_gamma[1] + 0.000907 * sin_gamma[1] -
            0.002697 * cos_gamma[2] + 0.001480 * sin_gamma[2])

    # Equation of time (difference between standard time and solar time).
    TimeGl = (0.000075 + 0.001868 * cos_gamma[0] - 0.032077 * sin_gamma[0] -
            0.014615 * cos_gamma[1]  - 0.040849 * sin_gamma[1]) * 229.18

    # True local time    .
    Tlt = (DayTime + degrees(lon) / 15 + TimeGl / 60) % 24 - 12

    # Calculate sun elevation.
    SinSunElevation = (sin(Declination) * sin(lat) +
            cos(Declination) * cos(lat) * cos(radians(Tlt * 15)))

    # Compute the sun's elevation and zenith angle.
    el = arcsin(SinSunElevation)
    zenith = pi / 2 - el

    # Compute the sun's azimuth angle.
    y = -(sin(lat) * sin(el) - sin(Declination)) / (cos(lat) * cos(el))
    azimuth = arccos(y)

    # Convert azimuth angle from 0-pi to 0-2pi.
    Tlt_filter = 0 <= Tlt
    azimuth[Tlt_filter] = 2 * pi - azimuth[Tlt_filter]

    # Calculate the extraterrestrial radiation.
    INull = np.max(1360.8 * SinSunElevation * ENull, 0)

    return {
        'zenith': np.degrees(zenith),
        'azimuth': np.degrees(azimuth),
        'declination': Declination,
        'I_ext': INull,
        'eccentricity': ENull,
    }
