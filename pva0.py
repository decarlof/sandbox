
from epics import PV
import pvaccess
import time


def connectionCallback(isConnected):
    print('Channel connected: %s' % isConnected)



# pv = PV('2bmb:m1')
# time.sleep(1)
# print(pv.connected)


pva = pvaccess.PvObject({'value': [pvaccess.pvaccess.ScalarType.FLOAT], 
                'sizex': pvaccess.pvaccess.ScalarType.INT, 
                'sizey': pvaccess.pvaccess.ScalarType.INT})
pvaServer = pvaccess.PvaServer('name', pva)
time.sleep(1)

channel = pvaccess.Channel('name')
print(channel)
time.sleep(1)

channel.setConnectionCallback(connectionCallback)
