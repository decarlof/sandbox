
from epics import PV
import pvaccess as pva
import time

epics_pv = {}

epics_pv['ImagePVAPName'] = PV('2bmbPG1:Pva1:')
# pva type channel that contains projection and metadata
image_pv_name = PV(epics_pvs['ImagePVAPName'].get()).get()
epics_pvs['PvaPImage']          = pva.Channel(image_pv_name + 'Image')
epics_pvs['PvaPDataType_RBV']   = pva.Channel(image_pv_name + 'DataType_RBV')
pva_plugin_image = epics_pvs['PvaPImage']