  import numpy as np                                                                                                                                  
  import tifffile                                                                                                                                     
  import os                                                                                                                                           
  import re                                                                                                                                           
                                                                                                                                                      
  # Map VGI datatypes to numpy dtypes                                                                                                                 
  DTYPE_MAP = {                                                                                                                                       
      "unsigned char":  np.uint8,
      "unsigned short": np.uint16,                                                                                                                    
      "unsigned int":   np.uint32,
      "char":           np.int8,
      "short":          np.int16,
      "int":            np.int32,
      "float":          np.float32,
      "double":         np.float64,
  }

  def parse_vgi(vgi_path):
      """Parse a VGI header file and return metadata dict."""
      meta = {}
      with open(vgi_path, "r") as f:
          for line in f:
              line = line.strip()
              if "=" in line:
                  key, _, val = line.partition("=")
                  meta[key.strip().lower()] = val.strip()
      return meta

  def load_vol(vgi_path):
      """Load raw volume data described by a VGI header."""
      meta = parse_vgi(vgi_path)

      # Dimensions
      size = list(map(int, meta["size"].split()))  # x y z
      nx, ny, nz = size

      # Data type
      dtype_str = meta.get("datatype", "unsigned short").lower()
      dtype = DTYPE_MAP.get(dtype_str)
      if dtype is None:
          raise ValueError(f"Unknown datatype: {dtype_str}")

      # Raw data file (same directory as .vgi)
      vgi_dir = os.path.dirname(vgi_path)
      vol_name = meta.get("name", os.path.splitext(os.path.basename(vgi_path))[0] + ".vol")
      vol_path = os.path.join(vgi_dir, vol_name)

      # Skip bytes (optional header in .vol)
      skip = int(meta.get("skipheader", meta.get("skipbytes", 0)))

      # Byte order
      endian = meta.get("byteorder", meta.get("endiantype", "little-endian")).lower()
      byteorder = "<" if "little" in endian else ">"

      # Read raw binary data
      vol = np.fromfile(vol_path, dtype=np.dtype(byteorder + dtype().dtype.str[1:]), offset=skip)
      vol = vol.reshape((nz, ny, nx))  # VG stores z-slices contiguously
      return vol

  def vg_to_tiff_stack(vgi_path, output_dir, prefix="slice", as_single_file=False):
      """
      Convert a VG volume to TIFF.

      Args:
          vgi_path:       Path to the .vgi file
          output_dir:     Directory to write TIFFs into
          prefix:         Filename prefix for individual slice TIFFs
          as_single_file: If True, write a single multi-page TIFF instead of a stack
      """
      os.makedirs(output_dir, exist_ok=True)
      vol = load_vol(vgi_path)
      print(f"Volume shape (z, y, x): {vol.shape}, dtype: {vol.dtype}")

      if as_single_file:
          out_path = os.path.join(output_dir, "volume.tiff")
          tifffile.imwrite(out_path, vol, photometric="minisblack")
          print(f"Saved multi-page TIFF: {out_path}")
      else:
          nz = vol.shape[0]
          pad = len(str(nz))
          for i, slice_ in enumerate(vol):
              fname = f"{prefix}_{str(i).zfill(pad)}.tiff"
              tifffile.imwrite(os.path.join(output_dir, fname), slice_)
          print(f"Saved {nz} TIFF slices to: {output_dir}")

  # --- Usage ---
  vg_to_tiff_stack(
      vgi_path="path/to/your_volume.vgi",
      output_dir="output_tiffs",
      prefix="slice",
      as_single_file=False,   # True = single multi-page TIFF
  )
