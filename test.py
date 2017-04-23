import sys
from get_urls import process_input_files

def test_process_input_files():
    txt = '/Users/jpls/projects/UTIL/get_urls/test_text_files/URL_TXT_01_2.txt'
    links = process_input_files([txt])

    check = '/Users/jpls/projects/UTIL/get_urls/test_text_files/URL_TXT_01_2-CONFIRM.txt'

    with open(check, 'r') as ftxt:
        confirmed = [line.strip() for line in ftxt if line.strip() != '']

    for link in links:
        assert link in confirmed

    print('Passed: process_input_files')


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    test_process_input_files()
