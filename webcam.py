import os
import cv2
import pathlib
import matplotlib.pyplot as plt
from dotenv import load_dotenv

env_path = os.path.join(str(pathlib.Path.home()), '.webcam')

try:
    with open(env_path,'rb') as fid:
        print('U_KEY and P_KEY file found at %s' % env_path)
    load_dotenv(dotenv_path=env_path)

    ret, frame = cv2.VideoCapture('http://' + u_key +':' + p_secret + '@164.54.113.162/cgi-bin/mjpeg?stream=1').read()
    plt.imshow(frame)
    plt.show()

except FileNotFoundError:
    log.error('U_KEY and P_KEY are missing. Set them in a file called: %s' % env_path)
    exit()

