import os
import json


data_path = '.'


lens_name = PV(2bm:MCTOptics:LensName0).value
print(lens_name)

with open(os.path.join(data_path, 'camera.json')) as json_file:
    camera_lookup = json.load(json_file)
with open(os.path.join(data_path, 'lens.json')) as json_file:
    lens_lookup = json.load(json_file)

print(lens_lookup["1.1"]['magnification'])
print(camera_lookup["Oryx ORX-10G-51S5M"]['detector_pixel_size'])

image_pixel_size = float(camera_lookup["Oryx ORX-10G-51S5M"]['detector_pixel_size'])/float(lens_lookup["1.1"]['magnification'])
print(image_pixel_size)