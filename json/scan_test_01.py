import json


    ts_pvs['RotationStart']         = PV(tomoscan_prefix + 'RotationStart')  
    ts_pvs['RotationStep']          = PV(tomoscan_prefix + 'RotationStep')  
    ts_pvs['NumAngles']             = PV(tomoscan_prefix + 'NumAngles')  
    ts_pvs['ReturnRotation']        = PV(tomoscan_prefix + 'ReturnRotation')  
    ts_pvs['NumDarkFields']         = PV(tomoscan_prefix + 'NumDarkFields')  
    ts_pvs['DarkFieldMode']         = PV(tomoscan_prefix + 'DarkFieldMode')  
    ts_pvs['DarkFieldValue']        = PV(tomoscan_prefix + 'DarkFieldValue')  
    ts_pvs['NumFlatFields']         = PV(tomoscan_prefix + 'NumFlatFields')
    ts_pvs['FlatFieldAxis']         = PV(tomoscan_prefix + 'FlatFieldAxis')
    ts_pvs['FlatFieldMode']         = PV(tomoscan_prefix + 'FlatFieldMode')
    ts_pvs['FlatFieldValue']        = PV(tomoscan_prefix + 'FlatFieldValue')  
    ts_pvs['FlatExposureTime']      = PV(tomoscan_prefix + 'FlatExposureTime')  
    ts_pvs['DifferentFlatExposure'] = PV(tomoscan_prefix + 'DifferentFlatExposure')
    ts_pvs['SampleInX']             = PV(tomoscan_prefix + 'SampleInX')
    ts_pvs['SampleInY']             = PV(tomoscan_prefix + 'SampleInY')
    ts_pvs['SampleOutAngleEnable']  = PV(tomoscan_prefix + 'SampleOutAngleEnable') 
    ts_pvs['SampleOutAngle']        = PV(tomoscan_prefix + 'SampleOutAngle')  
    ts_pvs['SampleOutX']            = PV(tomoscan_prefix + 'SampleOutX')  
    ts_pvs['SampleOutY']            = PV(tomoscan_prefix + 'SampleOutY')  
    ts_pvs['ScanType']              = PV(tomoscan_prefix + 'ScanType')
    ts_pvs['FlipStitch']            = PV(tomoscan_prefix + 'FlipStitch')
    ts_pvs['ExposureTime']          = PV(tomoscan_prefix + 'ExposureTime')  

scan_dict = {
            '00' :  {'SampleX' : 0.0,  'SampleY' : 1.0,  'RotationStart' : 0, 'RotationStep' : 0.12,  'NumAngles' : 1500, 'ReturnRotation' : 'No', 'NumDarkFields' : 20, 'DarkFieldMode' : 'Start', 'DarkFieldValue': 0, 'NumFlatFields' : 20, 'FlatFieldValue' : 0, 'FlatExposureTime' : 0.1, 'DifferentFlatExposure' : 'No', 'FlatFieldMode' : 'Start', 'FlatFieldAxis' : 'X', 'SampleInX' : 0, 'SampleOutX' : 1, 'SampleInY' : 0, 'SampleOutY' : 1, 'SampleOutAngle' : 90, 'SampleOutAngleEnable' : 'No', 'ScanType' : 'Single', 'FlipStitch' : 'No', 'ExposureTime' : 0.01 },
            '01' :  {'SampleX' : 0.1,  'SampleY' : 0.9,  'RotationStart' : 0, 'RotationStep' : 0.12,  'NumAngles' : 1500, 'ReturnRotation' : 'No', 'NumDarkFields' : 20, 'DarkFieldMode' : 'Start', 'DarkFieldValue': 0, 'NumFlatFields' : 20, 'FlatFieldValue' : 0, 'FlatExposureTime' : 0.1, 'DifferentFlatExposure' : 'No', 'FlatFieldMode' : 'Start', 'FlatFieldAxis' : 'X', 'SampleInX' : 0, 'SampleOutX' : 1, 'SampleInY' : 0, 'SampleOutY' : 1, 'SampleOutAngle' : 90, 'SampleOutAngleEnable' : 'No', 'ScanType' : 'Single', 'FlipStitch' : 'No', 'ExposureTime' : 0.01 },
            '02' :  {'SampleX' : 0.2,  'SampleY' : 0.8,  'RotationStart' : 0, 'RotationStep' : 0.12,  'NumAngles' : 1500, 'ReturnRotation' : 'No', 'NumDarkFields' : 20, 'DarkFieldMode' : 'Start', 'DarkFieldValue': 0, 'NumFlatFields' : 20, 'FlatFieldValue' : 0, 'FlatExposureTime' : 0.1, 'DifferentFlatExposure' : 'No', 'FlatFieldMode' : 'Start', 'FlatFieldAxis' : 'X', 'SampleInX' : 0, 'SampleOutX' : 1, 'SampleInY' : 0, 'SampleOutY' : 1, 'SampleOutAngle' : 90, 'SampleOutAngleEnable' : 'No', 'ScanType' : 'Single', 'FlipStitch' : 'No', 'ExposureTime' : 0.01 },
            '03' :  {'SampleX' : 0.3,  'SampleY' : 0.7,  'RotationStart' : 0, 'RotationStep' : 0.12,  'NumAngles' : 1500, 'ReturnRotation' : 'No', 'NumDarkFields' : 20, 'DarkFieldMode' : 'Start', 'DarkFieldValue': 0, 'NumFlatFields' : 20, 'FlatFieldValue' : 0, 'FlatExposureTime' : 0.1, 'DifferentFlatExposure' : 'No', 'FlatFieldMode' : 'Start', 'FlatFieldAxis' : 'X', 'SampleInX' : 0, 'SampleOutX' : 1, 'SampleInY' : 0, 'SampleOutY' : 1, 'SampleOutAngle' : 90, 'SampleOutAngleEnable' : 'No', 'ScanType' : 'Single', 'FlipStitch' : 'No', 'ExposureTime' : 0.01 },
            '04' :  {'SampleX' : 0.4,  'SampleY' : 0.6,  'RotationStart' : 0, 'RotationStep' : 0.12,  'NumAngles' : 1500, 'ReturnRotation' : 'No', 'NumDarkFields' : 20, 'DarkFieldMode' : 'Start', 'DarkFieldValue': 0, 'NumFlatFields' : 20, 'FlatFieldValue' : 0, 'FlatExposureTime' : 0.1, 'DifferentFlatExposure' : 'No', 'FlatFieldMode' : 'Start', 'FlatFieldAxis' : 'X', 'SampleInX' : 0, 'SampleOutX' : 1, 'SampleInY' : 0, 'SampleOutY' : 1, 'SampleOutAngle' : 90, 'SampleOutAngleEnable' : 'No', 'ScanType' : 'Single', 'FlipStitch' : 'No', 'ExposureTime' : 0.01 },
            '05' :  {'SampleX' : 0.5,  'SampleY' : 0.5,  'RotationStart' : 0, 'RotationStep' : 0.12,  'NumAngles' : 1500, 'ReturnRotation' : 'No', 'NumDarkFields' : 20, 'DarkFieldMode' : 'Start', 'DarkFieldValue': 0, 'NumFlatFields' : 20, 'FlatFieldValue' : 0, 'FlatExposureTime' : 0.1, 'DifferentFlatExposure' : 'No', 'FlatFieldMode' : 'Start', 'FlatFieldAxis' : 'X', 'SampleInX' : 0, 'SampleOutX' : 1, 'SampleInY' : 0, 'SampleOutY' : 1, 'SampleOutAngle' : 90, 'SampleOutAngleEnable' : 'No', 'ScanType' : 'Single', 'FlipStitch' : 'No', 'ExposureTime' : 0.01 },
            '06' :  {'SampleX' : 0.6,  'SampleY' : 0.4,  'RotationStart' : 0, 'RotationStep' : 0.12,  'NumAngles' : 1500, 'ReturnRotation' : 'No', 'NumDarkFields' : 20, 'DarkFieldMode' : 'Start', 'DarkFieldValue': 0, 'NumFlatFields' : 20, 'FlatFieldValue' : 0, 'FlatExposureTime' : 0.1, 'DifferentFlatExposure' : 'No', 'FlatFieldMode' : 'Start', 'FlatFieldAxis' : 'X', 'SampleInX' : 0, 'SampleOutX' : 1, 'SampleInY' : 0, 'SampleOutY' : 1, 'SampleOutAngle' : 90, 'SampleOutAngleEnable' : 'No', 'ScanType' : 'Single', 'FlipStitch' : 'No', 'ExposureTime' : 0.01 },
            '07' :  {'SampleX' : 0.7,  'SampleY' : 0.3,  'RotationStart' : 0, 'RotationStep' : 0.12,  'NumAngles' : 1500, 'ReturnRotation' : 'No', 'NumDarkFields' : 20, 'DarkFieldMode' : 'Start', 'DarkFieldValue': 0, 'NumFlatFields' : 20, 'FlatFieldValue' : 0, 'FlatExposureTime' : 0.1, 'DifferentFlatExposure' : 'No', 'FlatFieldMode' : 'Start', 'FlatFieldAxis' : 'X', 'SampleInX' : 0, 'SampleOutX' : 1, 'SampleInY' : 0, 'SampleOutY' : 1, 'SampleOutAngle' : 90, 'SampleOutAngleEnable' : 'No', 'ScanType' : 'Single', 'FlipStitch' : 'No', 'ExposureTime' : 0.01 },
            '08' :  {'SampleX' : 0.8,  'SampleY' : 0.2,  'RotationStart' : 0, 'RotationStep' : 0.12,  'NumAngles' : 1500, 'ReturnRotation' : 'No', 'NumDarkFields' : 20, 'DarkFieldMode' : 'Start', 'DarkFieldValue': 0, 'NumFlatFields' : 20, 'FlatFieldValue' : 0, 'FlatExposureTime' : 0.1, 'DifferentFlatExposure' : 'No', 'FlatFieldMode' : 'Start', 'FlatFieldAxis' : 'X', 'SampleInX' : 0, 'SampleOutX' : 1, 'SampleInY' : 0, 'SampleOutY' : 1, 'SampleOutAngle' : 90, 'SampleOutAngleEnable' : 'No', 'ScanType' : 'Single', 'FlipStitch' : 'No', 'ExposureTime' : 0.01 },
            '08' :  {'SampleX' : 0.9,  'SampleY' : 0.1,  'RotationStart' : 0, 'RotationStep' : 0.12,  'NumAngles' : 1500, 'ReturnRotation' : 'No', 'NumDarkFields' : 20, 'DarkFieldMode' : 'Start', 'DarkFieldValue': 0, 'NumFlatFields' : 20, 'FlatFieldValue' : 0, 'FlatExposureTime' : 0.1, 'DifferentFlatExposure' : 'No', 'FlatFieldMode' : 'Start', 'FlatFieldAxis' : 'X', 'SampleInX' : 0, 'SampleOutX' : 1, 'SampleInY' : 0, 'SampleOutY' : 1, 'SampleOutAngle' : 90, 'SampleOutAngleEnable' : 'No', 'ScanType' : 'Single', 'FlipStitch' : 'No', 'ExposureTime' : 0.01 },
            '10' :  {'SampleX' : 1.0,  'SampleY' : 0.0,  'RotationStart' : 0, 'RotationStep' : 0.12,  'NumAngles' : 1500, 'ReturnRotation' : 'No', 'NumDarkFields' : 20, 'DarkFieldMode' : 'Start', 'DarkFieldValue': 0, 'NumFlatFields' : 20, 'FlatFieldValue' : 0, 'FlatExposureTime' : 0.1, 'DifferentFlatExposure' : 'No', 'FlatFieldMode' : 'Start', 'FlatFieldAxis' : 'X', 'SampleInX' : 0, 'SampleOutX' : 1, 'SampleInY' : 0, 'SampleOutY' : 1, 'SampleOutAngle' : 90, 'SampleOutAngleEnable' : 'No', 'ScanType' : 'Single', 'FlipStitch' : 'No', 'ExposureTime' : 0.01 },
            } 

with open('data.json', 'w') as fp:
    json.dump(scan_dict, fp, indent=4, sort_keys=True)

with open('data.json') as json_file:
    data = json.load(json_file)


if scan_dict == data:
    print("Same")
else:
    print("Different")

for key, value in scan_dict.items():
    print(key, value['SampleX'], value['SampleY'])
    # print(type(item))