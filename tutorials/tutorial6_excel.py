# import volmdlr as vm
# import volmdlr.primitives2d as p2d
# import volmdlr.primitives3d as p3d
# import plot_data.core as plot_data
# import math
# from itertools import product
# from random import random
# import cma

from dessia_common.core import DessiaObject
# from typing import List


class Datas(DessiaObject):
    _standalone_in_db = True

    def __init__(self, param1: float, param2: float,
                 param3: float, param4: float, param5: float,
                 sum: float=None,
                 name: str = ''):

        DessiaObject.__init__(self, name=name)
        self.sum = sum
        self.param5 = param5
        self.param4 = param4
        self.param3 = param3
        self.param2 = param2
        self.param1 = param1
