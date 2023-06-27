''' Dumps a pca file into an excel spreasheet
'''

import os
import sys
import configparser
import pandas as pd

class GetDict:
    
    def __init__(self, config):
        self.config = config
    
    def get_dict(self):

        config = configparser.ConfigParser()
        config.optionxform = str
        config_file = open(self.config, encoding="cp1251")
        config.readfp(config_file)
        sections_dict = {}

        # get sections and iterate over each
        sections = config.sections()
        
        for section in sections:
            options = config.options(section)
            temp_dict = {}
            for option in options:
                temp_dict[option] = config.get(section,option)
            
            sections_dict[section] = temp_dict

        return sections_dict
    
if __name__== '__main__':

    if len(sys.argv) == 1:
        print ('Must provide the path to the pca file as the argument')
        sys.exit(1)
    
    file_name = sys.argv[1]
    getdict = GetDict(file_name)
    config_dict=getdict.get_dict()
    list_of_dicts = list(config_dict.values())
    df = pd.DataFrame.from_dict(list_of_dicts)
    
    file_name_excel = os.path.splitext(file_name)[0] + '.xlsx'
    df.to_excel(file_name_excel)
    print('Converted excel is at: %s', file_name_excel)
