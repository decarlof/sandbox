import csv
import pandas

def email_list_merge(file_name_1, file_name_2):

    reader_1 = pandas.read_csv(file_name_1)
    reader_1 = reader_1.drop_duplicates(subset=['EMAIL'], keep='first')
    first_list = reader_1.loc[:, 'EMAIL'].tolist()

    reader_2 = pandas.read_csv(file_name_2)
    reader_2 = reader_2.drop_duplicates(subset=['EMAIL'], keep='first')
    second_list = reader_2.loc[:, 'EMAIL'].tolist()

    print(len(first_list), len(second_list))
    return list(set(first_list) | set(second_list))


file_name_1 = '/Users/decarlo/Downloads/mailing-list/query_results_10_years_2-BM.txt'
file_name_2 = '/Users/decarlo/Downloads/mailing-list/beamline_2-BM.txt'

file_name_1 = '/Users/decarlo/Downloads/mailing-list/query_results_10_years_7-BM.txt'
file_name_2 = '/Users/decarlo/Downloads/mailing-list/beamline_7-BM.txt'

file_name_1 = '/Users/decarlo/Downloads/mailing-list/query_results_10_years_32-ID.txt'
file_name_2 = '/Users/decarlo/Downloads/mailing-list/beamline_32-ID.txt'

merged_list = email_list_merge(file_name_1, file_name_2)
print(len(merged_list))
print(merged_list)
