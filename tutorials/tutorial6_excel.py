from typing import Dict

from dessia_common.core import DessiaObject
from dessia_common.files import BinaryFile

import openpyxl


class ParameterData(DessiaObject):
    def __init__(self, datas: Dict[str, float], name: str = ''):
        self.datas = datas
        DessiaObject.__init__(self, name=name)

    @classmethod
    def read_excel(cls, stream: BinaryFile):
        workbook = openpyxl.load_workbook(stream)
        sheet = workbook.active

        datas = {}
        for row in sheet.iter_rows(min_row=1, max_col=2, values_only=True):
            if row[0] and isinstance(row[1], (int, float)):
                datas[row[0]] = row[1]

        return cls(datas=datas)

    @property
    def calculate_sum(self):
        return sum(self.datas.values())

