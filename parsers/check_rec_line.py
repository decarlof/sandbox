import os
import sys
import pathlib

def save_rec_line(rec_line):
    with open(file_name, 'a') as f:
        f.write(rec_line)

def load_rec_line(file_name):
    with open(file_name, 'r') as f:
        first_line = f.readline()

    return first_line

def read_rec_line(file_name):
    line = None
    try:
        with open(file_name, 'r') as fid:
            line = fid.readlines()[0]
    except:
        log.warning('Skipping the command line for reconstruction')
        line = ''
    return line

def main(args):

    if len(sys.argv) == 1:
        print ('ERROR: Must provide a full path file name to rec_line.txt as the argument')
        print ('Example:')
        print ('        python %s /data/2022-12/Finfrock-2022-12/sample_rec/rec_line.txt'% sys.argv[0])
        sys.exit(1)
    else:
        file_name   = sys.argv[1]
        rec_line = load_rec_line(file_name)

        p = pathlib.Path(file_name)
        if p.is_file():
            print('%s is a valid file' % p)
            rec_line = read_rec_line(file_name)
            print(rec_line)

        else:
            print('ERROR: %s does not exist' % p)
            sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv)
