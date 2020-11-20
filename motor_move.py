from epics import PV

rotary_stage = PV('2bma:m82.VAL')

rotary_stage_position = rotary_stage.get()
print("First Position:", rotary_stage_position)

rotary_stage.put(10, wait=True)

rotary_stage_position = rotary_stage.get()
print("Second Position:", rotary_stage_position)

rotary_stage.put(-7, wait=True)

rotary_stage_position = rotary_stage.get()
print("Third Position:", rotary_stage_position)