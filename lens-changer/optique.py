import os
import json
from epics import PV

data_path = '.'


with open(os.path.join(data_path, 'camera.json')) as json_file:
    camera_lookup = json.load(json_file)
with open(os.path.join(data_path, 'lens.json')) as json_file:
    lens_lookup = json.load(json_file)


lens_select = PV("2bm:MCTOptics:LensSelect").get()
if(lens_select == 0):
    lens_name = PV("2bm:MCTOptics:LensName0").get()
elif(lens_select == 1):
    lens_name = PV("2bm:MCTOptics:LensName1").get()
elif(lens_select == 2):
    lens_name = PV("2bm:MCTOptics:LensName2").get()

lens_name = lens_name.upper().replace("X", "")
try:
    scintillator_type      = lens_lookup[lens_name]['scintillator_type']
    scintillator_thickness = lens_lookup[lens_name]['scintillator_thickness']
    magnification          = lens_lookup[lens_name]['magnification']
    tube_lens              = lens_lookup[lens_name]['tube_lens']
except KeyError as e:

	print('Lens called %s is not defined. Please add it to the /data/lens.json file' % e)
	exit()

print('Lens name: %s' % lens_name)
print('Scintillator type: %s' % scintillator_type)
print('Scintillator thickness: %s' % scintillator_thickness)
print('Magnification: %s' % magnification)
print('Tube lens: %s' % tube_lens)

camera_select = PV("2bm:MCTOptics:CameraSelect").get()
if(camera_select == 0):
    camera_name = PV("2bm:MCTOptics:CameraName0").get()
elif(camera_select == 1):
    camera_name = PV("2bm:MCTOptics:CameraName1").get()
elif(lens_select == 2):
    camera_name = PV("2bm:MCTOptics:CameraName2").get()

camera_name = camera_name.upper()
detector_pixel_size = camera_lookup[camera_name]['detector_pixel_size']
print('Camera selected %s, detector pixel size: %s' % (camera_name, detector_pixel_size))


image_pixel_size = float(detector_pixel_size)/float(magnification)
print(f'{image_pixel_size = }')