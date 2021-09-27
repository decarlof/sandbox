from epics import PV


def on_change(pvname=None, value=None, char_value=None, **kw):

    message = pvname + ': ' + 'value = ' + str(value) + '; char = ' + char_value 
    print(message)
    # print(kw)

shutter_permit = PV('ACIS:ShutterPermit', form='ctrl')
tt='test'
shutter_permit.add_callback(on_change)
# ops_message = PV('OPS:message1')
# ops_message.add_callback(on_change)

shutter_permit_value = shutter_permit.get(as_string=True)
# ops_message_value = ops_message.get(as_string=True)
print("Shutter Permit:", shutter_permit_value)
# print("OPS message:", ops_message_value)
