#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

import volmdlr as vm
import volmdlr.step
import volmdlr.step as STEP
from pathlib import Path


# step = STEP.Step('export_bis.stp')
# model = step.to_volume_model()
# print(model.primitives)
#
# model.babylonjs()
#
# model2 = model.copy()
#
# assert model == model2


def from_step_file(path):
    step = STEP.Step.from_file(path)
    model = step.to_volume_model()
    model.babylonjs()


DIR = Path(__file__).resolve().parent / 'datas' / 'model_step.step'
# EX :  DIR = Path.home() / 'Documents' / ...


from_step_file(path=DIR)

