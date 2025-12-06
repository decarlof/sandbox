# import numpy as np

# moved     = 1.9      # 1.6    # 1.9
# d_source  = 51000    # 36200  # 51000
# d_pin     = 641      # 345    # 641
# pixel     = 0.345    # 0.691  # 0.345 


# movement  = np.atan(moved/d_source)
# calculated_over_delta_pins = d_pin * np.sin(movement)

# print("%.2f μrad, %.2f μm => %.2f pixels" % (movement*1e6, calculated_over_delta_pins*1000, calculated_over_delta_pins*1000/pixel))

import numpy as np
import argparse

def compute(moved, d_source, d_pin, pixel):
    movement = np.atan(moved / d_source)
    calculated_over_delta_pins = d_pin * np.sin(movement)

    print(
        "%.2f μrad, %.2f μm => %.2f pixels"
        % (
            movement * 1e6,
            calculated_over_delta_pins * 1000,
            (calculated_over_delta_pins * 1000) / pixel,
        )
    )

def main():
    parser = argparse.ArgumentParser(description="Compute beam divergence geometry.")

    # moved must always be given
    parser.add_argument("--moved", type=float, required=True, help="Movement in mm")

    # optional arguments with defaults
    parser.add_argument("--d_source", type=float, default=51000, help="Source distance in mm (default: 51000)")
    parser.add_argument("--d_pin", type=float, default=641, help="Pin separation in mm (default: 641)")
    parser.add_argument("--pixel", type=float, default=0.345, help="Pixel size in μm (default: 0.345)")

    args = parser.parse_args()

    compute(args.moved, args.d_source, args.d_pin, args.pixel)

if __name__ == "__main__":
    main()
