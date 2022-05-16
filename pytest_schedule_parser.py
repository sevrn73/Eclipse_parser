import pytest
import numpy as np
from typing import List

class TestLineParsersUnit:
    """
    Pytest requires names of class to start with 'Test...'
    Info about keywords and asterisk (*) could be found by the link: http://www.ipt.ntnu.no/~kleppe/TPG4150/EclipseReferenceManual.pdf
    """
    def test_parse_keyword_DATE_line(self):
        input = "01 JUN 2018 /"
        output = "01 JUN 2018"
        assert parse_keyword_DATE_line(input) == output

    def test_parse_keyword_COMPDAT_line(self):
        input = "'W1' 10 10 1 3 OPEN 1* 1 2 1 3* 1.0 /"
        output = ['W1', np.nan, '10', '10', '1', '3', 'OPEN', 'DEFAULT', '1',
                  '2', '1', 'DEFAULT', 'DEFAULT', 'DEFAULT', '1.0']
        assert parse_keyword_COMPDAT_line(input) == output

    def test_parse_keyword_COMPDATL_line(self):
        input = "'W3' 'LGR1' 10 10  2   2 	OPEN 	1* 	1	2 	1 	3* 			1.0918 /"
        output = ['W3', 'LGR1', '10', '10', '2', '2', 'OPEN', 'DEFAULT', '1',
                  '2', '1', 'DEFAULT', 'DEFAULT', 'DEFAULT', '1.0918']
        assert parse_keyword_COMPDATL_line(input) == output

    def test_default_params_unpacking_in_line(self):
        input = "'W1' 10 10 1 3 OPEN 1* 1 2 1 3* 1.0 /"
        output = "'W1' 10 10 1 3 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 1.0 /"
        assert default_params_unpacking_in_line(input) == output


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
