# Parameters
N = 10  # frames per rotation
n = 3   # number of rotations
exposure_time   = 0.2   # detector exposure time in s
detector_x_size = 2048  # horizontal detector size in pixels
blurr_error     = 1     # in pixel  

r = detector_x_size / 2

max_speed = np.degrees(np.acos((r - blurr_error) / r )) / exposure_time


print(max_speed)

exit()
