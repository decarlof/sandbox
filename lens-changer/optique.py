import os
import json
from epics import PV

data_path = '.'


with open(os.path.join(data_path, 'camera.json')) as json_file:
    camera_lookup = json.load(json_file)
with open(os.path.join(data_path, 'lens.json')) as json_file:
    lens_lookup = json.load(json_file)


lens_select = PV("2bm:MCTOptics:LensSelect").value
if(lens_select == 0):
    lens_name = PV("2bm:MCTOptics:LensName0").value
elif(lens_select == 1):
    lens_name = PV("2bm:MCTOptics:LensName1").value
elif(lens_select == 2):
    lens_name = PV("2bm:MCTOptics:LensName2").value

lens_name = lens_name.upper().replace("X", "")
lens_magnification = lens_lookup[lens_name]['magnification']
print('Lens selected: %s, magnification %s' % (lens_name, lens_magnification))

camera_select = PV("2bm:MCTOptics:CameraSelect").value
if(camera_select == 0):
    camera_name = PV("2bm:MCTOptics:CameraName0").value
elif(camera_select == 1):
    camera_name = PV("2bm:MCTOptics:CameraName1").value
elif(lens_select == 2):
    camera_name = PV("2bm:MCTOptics:CameraName2").value

camera_name = camera_name.upper()
detector_pixel_size = camera_lookup[camera_name]['detector_pixel_size']
print('Camera selected %s, detector pixel size: %s' % (camera_name, detector_pixel_size))


image_pixel_size = float(detector_pixel_size)/float(lens_magnification)
print(f'{image_pixel_size = }')