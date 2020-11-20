import numpy as np 
import log

log.setup_custom_logger("test.log")

# start = 32.55
# step_size = 1.4
# steps = 2
# end = start + (step_size * steps) + 1e-6
# for i in np.arange(start, end, step_size):
#     print (i)

# print("-----------------------------")
# start = 30.75
# step_size = 1.4
# steps = 3
# end = start + (step_size * steps) + 1e-6
# for i in np.arange(start, end, step_size):
#     print (i)
# print("-----------------------------")

# start = 32.55
# step_size = 1.4
# steps = 2
# end = start + (step_size * steps)
# for i in np.linspace(start, end, steps):
#     print (i)

print("-----------------------------")
start = 30.35
step_size = 1.4
steps = 3
end = start + (step_size * steps)
print(start, step_size, steps, end)

log.info('vertical positions (mm): %s', np.linspace(start, end, steps))

for i in np.linspace(start, end, steps):
    print (i)