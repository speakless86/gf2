'''
Global configs

Created on Apr 7, 2013

@author: charliez
'''

DEBUG = True

uri_map = {
    "upload_audio_form" : r'/upload_audio_form',
    "upload_audio" : r'/upload_audio',
    "play_audio" : r'/play_audio/([^/]+)?',
    "home_page": r'/',
    "login": r'/a/login',
    "signup": r'/a/signup',
    "signup_page": r'/p/signup',
    "check_email": r'/a/check_email',
}

