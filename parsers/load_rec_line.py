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

def main(args):

    if len(sys.argv) == 1:
        print ('ERROR: Must provide the path to a run-file folder as the argument')
        print ('Example:')
        print ('        python %s /data/2022-12/Finfrock-2022-12'% sys.argv[0])
        sys.exit(1)
    else:
        search_folder   = sys.argv[1]
        p = pathlib.Path(search_folder)
        if p.is_dir():
            print('%s is a valid directory' % p)
            rec_line_file_names = tuple(p.glob('*_rec/rec_line.txt'))
            with open("rec_batch", 'a') as f:
                for rec_line_file_name in rec_line_file_names:
                    f.write(load_rec_line(rec_line_file_name))
                    f.write('\n')
        else:
            print('ERROR: %s does not exist' % p)
            sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv)
