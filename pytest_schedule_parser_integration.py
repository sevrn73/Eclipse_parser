import pytest
import pandas as pd
import numpy as np
from typing import List, Tuple


class TestUnitParser:
    @pytest.fixture
    def set_up(self):
        """
        Prepares info for reference input file(s)
        @return: None
        """
        self.keywords = ("DATES", "COMPDAT", "COMPDATL")
        self.parameters = ("Date", "Well name", "Local grid name", "I", "J", "K upper", "K lower", "Flag on connection",
                  "Saturation table", "Transmissibility factor", "Well bore diameter", "Effective Kh",
                  "Skin factor", "D-factor", "Dir_well_penetrates_grid_block", "Press_eq_radius")

        # TODO: с названиями стоит подумать
        self.input_file_reference = "data/test_schedule_input_reference.inc"
        self.output_csv_reference = "data/schedule_output_reference.csv"

        self.clean_file = "tests/handled_schedule.inc"
        self.output_csv = "data/schedule_output.csv"

        with open(self.clean_file, "r", encoding="utf-8") as file:
            self.clean_file_text = file.read()

        self.parse_list_output_reference = [
        [np.nan, 'W1', np.nan, '10', '10', '1', '3', 'OPEN', 'DEFAULT', '1', '2', '1', 'DEFAULT', 'DEFAULT', 'DEFAULT', '1.0'],
        [np.nan, 'W2', np.nan, '32', '10', '1', '3', 'OPEN', 'DEFAULT', '1', '2', '1', 'DEFAULT', 'DEFAULT', 'DEFAULT', '2.0'],
        [np.nan, 'W3', np.nan, '5', '36', '2', '2', 'OPEN', 'DEFAULT', '1', '2', '1', 'DEFAULT', 'DEFAULT', 'DEFAULT', '3.0'],
        [np.nan, 'W4', np.nan, '40', '30', '1', '3', 'OPEN', 'DEFAULT', '1', '2', '1', 'DEFAULT', 'DEFAULT', 'DEFAULT', '4.0'],
        [np.nan, 'W5', np.nan, '21', '21', '4', '4', 'OPEN', 'DEFAULT', '1', '2', '1', 'DEFAULT', 'DEFAULT', 'DEFAULT', '5.0'],
        ['01 JUN 2018', np.nan],
        ['01 JUL 2018', 'W3', np.nan, '32', '10', '1', '1', 'OPEN', 'DEFAULT', '1', '2', '1', 'DEFAULT', 'DEFAULT', 'DEFAULT', '1.0718'],
        ['01 JUL 2018', 'W5', np.nan, '21', '21', '1', '3', 'OPEN', 'DEFAULT', '1', '2', '1', 'DEFAULT', 'DEFAULT', 'DEFAULT', '5.0'],
        ['01 AUG 2018', np.nan],
        ['01 SEP 2018', 'W1', np.nan, '10', '10', '2', '3', 'OPEN', 'DEFAULT', '1', '2', '1', 'DEFAULT', 'DEFAULT', 'DEFAULT', '1.0918'],
        ['01 SEP 2018', 'W2', np.nan, '32', '10', '1', '2', 'OPEN', 'DEFAULT', '1', '2', '1', 'DEFAULT', 'DEFAULT', 'DEFAULT', '2.0'],
        ['01 SEP 2018', 'W3', 'LGR1', '10', '10', '2', '2', 'OPEN', 'DEFAULT', '1', '2', '1', 'DEFAULT', 'DEFAULT', 'DEFAULT', '1.0918'],
        ['01 OCT 2018', np.nan],
        ['01 NOV 2018', np.nan],
        ['01 DEC 2018', np.nan]]

    def test_parse_schedule(self, set_up):
        assert parse_schedule(self.clean_file_text, keywords_tuple=self.keywords) \
               == self.parse_list_output_reference


def parse_schedule(text: str, keywords_tuple: Tuple[str]) -> List[List[str]]:
    """
    return list of elements ready to be transformed to the resulting DataFrame
    @param text: cleaned input text from .inc file
    @param keywords_tuple: a tuple of keywords we are interested in (DATES, COMPDAT, COMPDATL, etc.)
    @return: list of elements [[DATA1, WELL1, PARAM1, PARAM2, ...], [DATA2, ...], ...] ready to be transformed
    to the resulting DataFrame
    """
    results = []
    date = None
    indicator = False
    for line in text.splitlines():
        if line in keywords_tuple:
            indicator = True
            keyword = line
            continue
        elif line == '/':
            indicator = False
      
        if indicator:
            if keyword != 'DATES':
                res = [np.nan if date is None else date]
                res.extend(parse_keyword_COMPDAT_line(line))
            else:
                date = parse_keyword_DATE_line(line)
                res = [date, np.nan]
            results.append(res) 
            
    filter_results = []
    for i in range(len(results)-1):
        # print(results[i])
        if not isinstance(results[i][0], str):
            filter_results.append(results[i])
        elif i == len(results):
            filter_results.append(results[i])
        else:
            if results[i][0] == results[i+1][0] and len(results[i]) > 2:
                filter_results.append(results[i])
            elif results[i][0] != results[i+1][0]:
                filter_results.append(results[i])   
    filter_results.append(results[-1])
    
    return filter_results
    
# парсим строки с параметрами, находящиеся в блоке под конкретным кл. словом. просится в отдельный модуль
def parse_keyword_DATE_line(current_date_line: str) -> str:
    """
    parse a line related to a current DATA keyword block
    @param current_date_line: line related to a current DATA keyword block
    @return: list of parameters in a DATE line
    """
    return current_date_line.replace(' /', '').replace('/', '')


def parse_keyword_COMPDAT_line(well_comp_line: str) -> List[str]:
    """
    parse a line related to a current COMPDAT keyword block
    @param well_comp_line: line related to a current COMPDAT keyword block
    @return: list of parameters (+ NaN Loc. grid. parameter) in a COMPDAT line
    """
    result = well_comp_line.replace(' /', '').replace('/', '').split()
    try:
        if isinstance(float(result[1]), float):
            result.insert(1, np.nan)
    except:
        pass
    for index, element in enumerate(result):
        if not isinstance(element, float):
            if element.find('*') != -1:
                
                n = int(element[0])
                
                result.remove(result[index])
                for _ in range(n):
                    result.insert(index, 'DEFAULT')
            else:
                result[index] = element.replace("'","")
  
    return result


def parse_keyword_COMPDATL_line(well_comp_line: str) -> List[str]:
    """
    parse a line related to a current COMPDATL keyword block
    @param well_comp_line: line related to a current COMPDATL keyword block
    @return: list of parameters in a COMPDATL line
    """
    return parse_keyword_COMPDAT_line(well_comp_line)

# для парсинга параметров по-умолчанию
def default_params_unpacking_in_line(line: str) -> str:
    """
    unpack default parameters set by the 'n*' expression
    @param line: line related to a current COMPDAT/COMPDATL keyword block
    @return: the unpacked line related to a current COMPDAT/COMPDATL keyword block
    """
    while line.find('*') != -1:
        n = line[line.find('*')-1]
        s = ''
        for _ in range(int(n)):
            s += 'DEFAULT' if s == '' else ' DEFAULT' 
           
        line = line.replace(f'{n}*', s)
    return line