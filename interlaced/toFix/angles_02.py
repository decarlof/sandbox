import sys
import math
import argparse
import numpy as np
import matplotlib.pyplot as plt
import log


def _compute_senses():
    '''Computes whether this motion will be increasing or decreasing encoder counts.
    
    user direction, overall sense.
    '''
    # Encoder direction compared to dial coordinates
    encoder_dir = 1 #if self.epics_pvs['PSOEncoderCountsPerStep'].get() > 0 else -1
    # Get motor direction (dial vs. user); convert (0,1) = (pos, neg) to (1, -1)
    motor_dir = 1 # if self.epics_pvs['RotationDirection'].get() == 0 else -1
    # Figure out whether motion is in positive or negative direction in user coordinates
    user_direction = 1 #if self.rotation_stop > self.rotation_start else -1
    # Figure out overall sense: +1 if motion in + encoder direction, -1 otherwise
    return user_direction * motor_dir * encoder_dir, user_direction

def compute_positions_PSO(rotation_start, rotation_step, num_angles, PSOCountsPerRotation):
    '''Computes several parameters describing the fly scan motion.
    Computes the spacing between points, ensuring it is an integer number
    of encoder counts.
    Uses this spacing to recalculate the end of the scan, if necessary.
    Computes the taxi distance at the beginning and end of scan to allow
    the stage to accelerate to speed.
    Assign the fly scan angular position to theta[]
    '''
    overall_sense, user_direction = _compute_senses()
    # Get the distance needed for acceleration = 1/2 a t^2 = 1/2 * v * t
    motor_accl_time = 3 #float(self.epics_pvs['RotationAccelTime'].get()) # Acceleration time in s
    accel_dist = motor_accl_time / 2.0 * 100#float(self.motor_speed) 

    # Compute the actual delta to keep each interval an integer number of encoder counts
    encoder_multiply = PSOCountsPerRotation / 360.   #float(self.epics_pvs['PSOCountsPerRotation'].get()) / 360.
    raw_delta_encoder_counts = rotation_step * encoder_multiply
    delta_encoder_counts = round(raw_delta_encoder_counts)
    if abs(raw_delta_encoder_counts - delta_encoder_counts) > 1e-4:
        log.warning('  *** *** *** Requested scan would have used a non-integer number of encoder counts.')
        log.warning('  *** *** *** Calculated # of encoder counts per step = {0:9.4f}'.format(raw_delta_encoder_counts))
        log.warning('  *** *** *** Instead, using {0:d}'.format(delta_encoder_counts))
    # self.epics_pvs['PSOEncoderCountsPerStep'].put(delta_encoder_counts)
    # Change the rotation step Python variable and PV
    rotation_step = delta_encoder_counts / encoder_multiply
    # self.epics_pvs['RotationStep'].put(self.rotation_step)
      
    # Make taxi distance an integer number of measurement deltas >= accel distance
    # Add 1/2 of a delta to ensure that we are really up to speed.
    taxi_dist = (math.ceil(accel_dist / rotation_step) + 0.5) * rotation_step 
    # self.epics_pvs['PSOStartTaxi'].put(self.rotation_start - taxi_dist * user_direction)
    # self.epics_pvs['PSOEndTaxi'].put(self.rotation_stop + taxi_dist * user_direction)
    
    #Where will the last point actually be?
    rotation_stop = (rotation_start 
                            + (num_angles - 1) * rotation_step * user_direction)
    # Assign the fly scan angular position to theta[]
    theta = rotation_start + np.arange(num_angles) * rotation_step * user_direction
    log.info(theta)

def sequence(nproj_total, nproj_per_rot, prime, continuous_angle=True):

    # seq = np.array((nproj_total * nproj_per_rot))
    seq = []
    # nproj_per_rot = int(nproj_per_rot)
    # print (len(seq))
    i = 0

    while len(seq) < nproj_total:

        b = i
        i += 1
        r = 0
        q = 1 / prime

        while (b != 0):
            a = np.mod(b, prime)
            r += (a * q)
            # print (b, r, a, q)
            q /= prime
            b = np.floor(b / prime)
        r *= (360.0 / nproj_per_rot)

        k = 0
        while (np.logical_and(len(seq) < nproj_total, k < nproj_per_rot)):
            seq.append(float(r + k * 360.0 / nproj_per_rot ))
            k += 1

    if continuous_angle:
        j = 0
        for x in range(len(seq)):       
            if (x%nproj_per_rot == 0):
                for y in range(nproj_per_rot):
                    if (x+y) < len(seq):
                        seq[x+y] += j*360.0
                j += 1

    return seq

def main(arg):

    lfname = './logger.txt'
 
    log.setup_custom_logger(lfname)
    log.info("Saving log at %s" % lfname)


    rotation_start = 0 
    rotation_step = 0.12
    num_angles = 1500  
    PSOCountsPerRotation = 7200000

    compute_positions_PSO(rotation_start, rotation_step, num_angles, PSOCountsPerRotation)
    parser = argparse.ArgumentParser()
    parser.add_argument("--nproj_total", nargs='?', type=int, default=100, help="total number of projections: 100 (default 100)")
    parser.add_argument("--nproj_per_rot", nargs='?', type=int, default=10, help="total number of projections per rotation: 10 (default 10)")
    parser.add_argument("--prime", nargs='?', type=int, default=10, help="prime: 2 (default 2). Ratio to position the first angle past 360")
    parser.add_argument("--continuous_angle",action="store_true", help="set to generate continuous angles past 360 deg")

    args = parser.parse_args()

    nproj_total = args.nproj_total
    nproj_per_rot = args.nproj_per_rot
    prime = args.prime
    continuous_angle = args.continuous_angle

    seq = sequence(nproj_total, nproj_per_rot, prime, continuous_angle)

    log.info(seq)
    plt.plot(seq)
    plt.grid('on')
    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])

