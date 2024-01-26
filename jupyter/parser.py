from collections import OrderedDict
from pathlib import Path
import configparser
from types import SimpleNamespace


SECTIONS = OrderedDict()

LOGS_HOME = Path.home()/'logs'
CONFIG_FILE_NAME = Path.home()/'tomocupyon.conf'

SECTIONS['general'] = {
    'config': {
        'default': CONFIG_FILE_NAME,
        'type': str,
        'help': "File name of configuration file",
        'metavar': 'FILE'},
    'logs-home': {
        'default': LOGS_HOME,
        'type': str,
        'help': "Log file directory",
        'metavar': 'FILE'},
    'verbose': {
        'default': False,
        'help': 'Verbose output',
        'action': 'store_true'},
    'config-update': {
        'default': False,
        'help': 'When set, the content of the config file is updated using the current params values',
        'action': 'store_true'},
}

SECTIONS['file-reading'] = {
    'file-name': {
        'default': '.',
        'type': Path,
        'help': "Name of the last used hdf file or directory containing multiple hdf files",
        'metavar': 'PATH'},
    'flat-file-name': {
        'default': None,
        'type': Path,
        'help': "Name of the hdf file containing flat data",
        'metavar': 'PATH'},
    'dark-file-name': {
        'default': None,
        'type': Path,
        'help': "Name of the hdf file containing dark data",
        'metavar': 'PATH'},
    'out-path-name': {
        'default': None,
        'type': Path,
        'help': "Path for output files",
        'metavar': 'PATH'},
    'file-type': {
        'default': 'standard',
        'type': str,
        'help': "Input file type",
        'choices': ['standard', 'double_fov']},
    'binning': {
        'type': int,
        'default': 0,
        'help': "Reconstruction binning factor as power(2, choice)",
        'choices': [0, 1, 2, 3]},
    'blocked-views': {
        'type': str,
        'default': 'none',
        'help': "Angle range for blocked views [st,end]. Can be a list of ranges(e.g. [[0,1.2],[3,3.14]])"},
}


SECTIONS['remove-stripe'] = {
    'remove-stripe-method': {
        'default': 'none',
        'type': str,
        'help': "Remove stripe method: none, fourier-wavelet, titarenko",
        'choices': ['none', 'fw', 'ti', 'vo-all']},
}


SECTIONS['fw'] = {
    'fw-sigma': {
        'default': 1,
        'type': float,
        'help': "Fourier-Wavelet remove stripe damping parameter"},
    'fw-filter': {
        'default': 'sym16',
        'type': str,
        'help': "Fourier-Wavelet remove stripe filter",
        'choices': ['haar', 'db5', 'sym5', 'sym16']},
    'fw-level': {
        'type': int,
        'default': 7,
        'help': "Fourier-Wavelet remove stripe level parameter"},
    'fw-pad': {
        'default': True,
        'help': "When set, Fourier-Wavelet remove stripe extend the size of the sinogram by padding with zeros",
        'action': 'store_true'},
}


SECTIONS['vo-all'] = {
    'vo-all-snr': {
        'default': 3,
        'type': float,
        'help': "Ratio used to locate large stripes. Greater is less sensitive."},
    'vo-all-la-size': {
        'default': 61,
        'type': int,
        'help': "Window size of the median filter to remove large stripes."},        
    'vo-all-sm-size': {
        'type': int,
        'default': 21,
        'help': "Window size of the median filter to remove small-to-medium stripes."},
    'vo-all-dim': {
        'default': 1,
        'help': "Dimension of the window."},
}


SECTIONS['ti'] = {
    'ti-beta': {
        'default': 0.022,  # as in the paper
        'type': float,
        'help': "Parameter for ring removal (0,1)"},
    'ti-mask': {
        'default': 1,  
        'type': float,
        'help': "Mask size for ring removal (0,1)"},
}

SECTIONS['retrieve-phase'] = {
    'retrieve-phase-method': {
        'default': 'none',
        'type': str,
        'help': "Phase retrieval correction method",
        'choices': ['none', 'paganin','Gpaganin']},
    'energy': {
        'default': 0,
        'type': float,
        'help': "X-ray energy [keV]"},
    'propagation-distance': {
        'default': 0,
        'type': float,
        'help': "Sample detector distance [mm]"},
    'pixel-size': {
        'default': 0,
        'type': float,
        'help': "Pixel size [microns]"},
    'retrieve-phase-alpha': {
        'default': 0,
        'type': float,
        'help': "Regularization parameter"},
    'retrieve-phase-delta-beta': {
        'default': 1500.0,
        'type': float,
        'help': "delta/beta material for Generalized Paganin"},
    'retrieve-phase-W': {
        'default': 2e-4,
        'type': float,
        'help': "Characteristic transverse length for Generalized Paganin"},
    'retrieve-phase-pad': {
        'type': int,
        'default': 1,
        'help': "Padding with extra slices in z for phase-retrieval filtering"},
}

SECTIONS['rotate-proj'] = {
    'rotate-proj-angle': {
        'default': 0,
        'type': float,
        'help': "Rotation angle for projections (counterclockwise)"},
    'rotate-proj-order': {
        'default': 1,
        'type': int,
        'help': "Interpolation spline order for rotation"},
}

SECTIONS['lamino'] = {
    'lamino-search-width': {
        'type': float,
        'default': 5.0,
        'help': "+/- center search width (pixel). "},
    'lamino-search-step': {
        'type': float,
        'default': 0.25,
        'help': "+/- center search step (pixel). "},
    'lamino-angle': {
        'default': 0,
        'type': float,
        'help': "Pitch of the stage for laminography"},
    'lamino-start-row': {
        'default': 0,
        'type': int,
        'help': "Start slice for lamino reconstruction"},
    'lamino-end-row': {
        'default': -1,
        'type': int,
        'help': "End slice for lamino reconstruction"},
}

SECTIONS['reconstruction-types'] = {
    'reconstruction-type': {
        'default': 'try',
        'type': str,
        'help': "Reconstruct full data set. ",
        'choices': ['full', 'try']},
    'reconstruction-algorithm': {
        'default': 'fourierrec',
        'type': str,
        'help': "Reconstruction algorithm",
        'choices': ['fourierrec', 'lprec', 'linerec']},
}

SECTIONS['reconstruction-steps-types'] = {
    'reconstruction-type': {
        'default': 'try',
        'type': str,
        'help': "Reconstruct full data set. ",
        'choices': ['full', 'try', 'try_lamino']},
    'reconstruction-algorithm': {
        'default': 'fourierrec',
        'type': str,
        'help': "Reconstruction algorithm",
        'choices': ['fourierrec', 'linerec']},
    'pre-processing': {
        'default': 'True',
        'type': str,
        'help': "Preprocess projections or not",
        'choices': ['True', 'False']},
}

SECTIONS['reconstruction'] = {
    'rotation-axis': {
        'default': -1.0,
        'type': float,
        'help': "Location of rotation axis"},
    'center-search-width': {
        'type': float,
        'default': 50.0,
        'help': "+/- center search width (pixel). "},
    'center-search-step': {
        'type': float,
        'default': 0.5,
        'help': "+/- center search step (pixel). "},
    'nsino': {
        'default': '0.5',
        'type': str,
        'help': 'Location of the sinogram used for slice reconstruction and find axis (0 top, 1 bottom). Can be given as a list, e.g. [0,0.9].'},
    'nsino-per-chunk': {
        'type': int,
        'default': 8,
        'help': "Number of sinograms per chunk. Use larger numbers with computers with larger memory. ", },
    'nproj-per-chunk': {
        'type': int,
        'default': 8,
        'help': "Number of projections per chunk. Use larger numbers with computers with larger memory.  ", },
    'start-row': {
        'type': int,
        'default': 0,
        'help': "Start slice"},
    'end-row': {
        'type': int,
        'default': -1,
        'help': "End slice"},
    'start-column': {
        'type': int,
        'default': 0,
        'help': "Start position in x"},
    'end-column': {
        'type': int,
        'default': -1,
        'help': "End position in x"},
    'start-proj': {
        'type': int,
        'default': 0,
        'help': "Start projection"},
    'end-proj': {
        'type': int,
        'default': -1,
        'help': "End projection"},
    'nproj-per-chunk': {
        'type': int,
        'default': 8,
        'help': "Number of sinograms per chunk. Use lower numbers with computers with lower GPU memory.", },
    'rotation-axis-auto': {
        'default': 'manual',
        'type': str,
        'help': "How to get rotation axis auto calculate ('auto'), or manually ('manual')",
        'choices': ['manual', 'auto', ]},
    'rotation-axis-pairs': {
        'default': '[0,0]',
        'type': str,
        'help': "Projection pairs to find rotation axis. Each second projection in a pair will be flipped and used to find shifts from the first element in a pair. The shifts are used to calculate the center.  Example [0,1499] for a 180 deg scan, or [0,1499,749,2249] for 360, etc.", },
    'rotation-axis-sift-threshold': {
        'default': '0.5',
        'type': float,
        'help': "SIFT threshold for rotation search.", },
    'rotation-axis-method': {
        'default': 'sift',  
        'type': str,        
        'help': "Method for automatic rotation search.",
        'choices': ['sift', 'vo']},
    'find-center-start-row': {
        'type': int,
        'default': 0,
        'help': "Start row to find the rotation center"},
    'find-center-end-row': {
        'type': int,
        'default': -1,
        'help': "End row to find the rotation center"},
    'dtype': {
        'default': 'float32',
        'type': str,
        'choices': ['float32', 'float16'],
        'help': "Data type used for reconstruction. Note float16 works with power of 2 sizes.", },
    'save-format': {
        'default': 'tiff',
        'type': str,
        'help': "Output format",
        'choices': ['tiff', 'h5', 'h5sino', 'h5nolinks']},
    'clear-folder': {
        'default': 'False',
        'type': str,
        'help': "Clear output folder before reconstruction",
        'choices': ['True', 'False']},
    'fbp-filter': {
        'default': 'parzen',
        'type': str,
        'help': "Filter for FBP reconstruction",
        'choices': ['ramp', 'shepp', 'hann', 'hamming', 'parzen', 'cosine', 'cosine2']},
    'dezinger': {
        'type': int,
        'default': 0,
        'help': "Width of region for removing outliers"},
    'dezinger-threshold': {
        'type': int,
        'default': 5000,
        'help': "Threshold of grayscale above local median to be considered a zinger pixel"},
    'max-write-threads': {
        'type': int,
        'default': 8,
        'help': "Max number of threads for writing by chunks"},
    'max-read-threads': {
        'type': int,
        'default': 4,
        'help': "Max number of threads for reading by chunks"},
    'minus-log': {
        'default': 'True',
        'help': "Take -log or not"},    
    'flat-linear': {
        'default': 'False',
        'help': "Interpolate flat fields for each projections, assumes the number of flat fields at the beginning of the scan is as the same as a the end."},        
    'pad-endpoint': {
        'default': 'False',
        'help': "Include or not endpoint for smooting in double fov reconstruction (preventing circle in the middle)."},            
}

RECON_STEPS_PARAMS = ('file-reading', 'remove-stripe', 'reconstruction',
                      'retrieve-phase', 'fw', 'ti', 'vo-all', 'lamino', 'reconstruction-steps-types', 'rotate-proj')
TEST_PARAMS = ('file-reading',)


tomo_params = RECON_STEPS_PARAMS
# tomo_params = TEST_PARAMS


# for section in tomo_params:
#     for key, value in SECTIONS[section].items():
#         print('%s = %s \t\t\t# help: %s' % (key, value['default'], value['help']))

params_dict = {}
for section in tomo_params:
    # print(section)
    for key, value in SECTIONS[section].items():
        # print('%s = %s ' % (key, value['default']))
        key = key.replace('-', '_')
        params_dict[key] = value['default']

# print(params_dict)

args = SimpleNamespace(**params_dict)

print(args)