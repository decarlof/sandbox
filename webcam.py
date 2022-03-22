import os
import cv2
import pathlib
import json
import matplotlib.pyplot as plt
from dotenv import load_dotenv

def read_json(fname):
    with open(fname, 'r') as fp:
        alist = json.load(fp)
    return alist

# Create a file in the home directory called access.json
# {
#     "p": "password",
#     "u": "username"
# }


access_fname = os.path.join(str(pathlib.Path.home()), 'access.json')
access_dic = read_json(access_fname)

try:

    ret, frame = cv2.VideoCapture('http://' + access_dic['u'] +':' + access_dic['p'] + '@164.54.113.162/cgi-bin/mjpeg?stream=1').read()
    if ret:
    	plt.imshow(frame)
    	plt.show()

except FileNotFoundError:
    log.error('username and password are missing. Set them in a file called: %s' % access_fname )

