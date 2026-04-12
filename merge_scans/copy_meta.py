import h5py

# src = '/data2/2BM/2026-04-Herrera-1020972/VPPLT-1964_Y-18mm_007.h5'
# dst = '/data2/2BM/2026-04-Herrera-1020972/VPPLT-1964_Y-18mm_merged.h5'

src = '/data2/2BM/2026-04-Herrera-1020972/VPPLT-1964_Y-23mm_021.h5'
dst = '/data2/2BM/2026-04-Herrera-1020972/VPPLT-1964_Y-23mm_merged.h5'

# src = '/data2/2BM/2026-04-Herrera-1020972/VPPLT-1964_Y-28mm_041.h5'
# dst = '/data2/2BM/2026-04-Herrera-1020972/VPPLT-1964_Y-28mm_merged.h5'

# src = '/data2/2BM/2026-04-Herrera-1020972/VPPLT-1964_Y-33mm_061.h5'
# dst = '/data2/2BM/2026-04-Herrera-1020972/VPPLT-1964_Y-33mm_merged.h5'

# src = '/data2/2BM/2026-04-Herrera-1020972/VPPLT-1964_Y-38mm_081.h5'
# dst = '/data2/2BM/2026-04-Herrera-1020972/VPPLT-1964_Y-38mm_merged.h5'

# src = '/data2/2BM/2026-04-Herrera-1020972/LowerJawJussaricColombia_Y-33mm_040.h5'
# dst = '/data2/2BM/2026-04-Herrera-1020972/LowerJawJussaricColombia_Y-33mm_merged.h5'

# src = '/data2/2BM/2026-04-Herrera-1020972/LowerJawJussaricColombia_Y-38mm_020.h5'
# dst = '/data2/2BM/2026-04-Herrera-1020972/LowerJawJussaricColombia_Y-38mm_merged.h5'


groups = ['/process', '/measurement', '/defaults']

cam = '/exchange/web_camera_frame'

with h5py.File(src, 'r') as s:
 with h5py.File(dst, 'a') as d:
     for g in groups:
         if g in d:
             print('Skipping ' + g + ' (already exists)')
         elif g in s:
             s.copy(g, d)
             print('Copied ' + g)
         else:
             print('Not found in source: ' + g)
     if cam in d:
         print('Skipping ' + cam + ' (already exists)')
     elif cam in s:
         s.copy(s[cam], d['/exchange'], 'web_camera_frame')
         print('Copied ' + cam)
     else:
         print('Not found in source: ' + cam)
