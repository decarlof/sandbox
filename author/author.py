
import re

filename  = '/Users/decarlo/APS-publications-2017-2020.txt'
img_authors = ['Nikitin', 'De Carlo', 'Parab', 'Cang Zhao', 'Tao Sun', 'Fezzaa', 'Kastengren', 'Xianghui Xiao', 'Xiaogang Yang', 'Prabat', 'Soriano']


file = open(filename,'r')
while True:
    next_line = file.readline()

    if not next_line:
        break;
    if next_line != '\n':
        first_author = next_line.strip().split(",")[0]
        for author in img_authors:
            if re.search(r"\b" + re.escape(author) + r"\b", first_author):
                print(first_author, next_line.strip().split(",")[-1])

file.close()