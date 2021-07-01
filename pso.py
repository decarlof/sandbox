def compute_positions_PSO(PSOCountsPerRotation, rotation_step):
    # Compute the actual delta to keep each interval an integer number of encoder counts
    encoder_multiply = float(PSOCountsPerRotation) / 360.
    raw_delta_encoder_counts = rotation_step * encoder_multiply
    delta_encoder_counts = round(raw_delta_encoder_counts)
    if abs(raw_delta_encoder_counts - delta_encoder_counts) > 1e-4:
        print('  *** *** *** Requested scan would have used a non-integer number of encoder counts.')
        print('  *** *** *** Calculated # of encoder counts per step = {0:9.4f}'.format(raw_delta_encoder_counts))
        print('  *** *** *** Instead, using {0:d}'.format(delta_encoder_counts))
    PSOEncoderCountsPerStep = delta_encoder_counts
    # self.epics_pvs['PSOEncoderCountsPerStep'].put(delta_encoder_counts)
    # Change the rotation step Python variable and PV

    # self.rotation_step = delta_encoder_counts / encoder_multiply
    # self.epics_pvs['RotationStep'].put(self.rotation_step)
    rotation_step = delta_encoder_counts / encoder_multiply

    return PSOEncoderCountsPerStep, rotation_step

start_angle = 0
rotation_step = 0.12
numer_of_angles = 1500
print(start_angle + rotation_step *(numer_of_angles-1))
pso_counts_per_rotation = 94400
PSOEncoderCountsPerStep, rotation_step = compute_positions_PSO(pso_counts_per_rotation, rotation_step)
rotation_stop = start_angle + rotation_step * (numer_of_angles - 1)
print(PSOEncoderCountsPerStep, rotation_step, rotation_stop)
print(180-rotation_stop)