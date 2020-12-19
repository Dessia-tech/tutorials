#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

import volmdlr as vm
import volmdlr.step

step = volmdlr.step.Step('export_bis.stp')
model = step.to_volume_model()
print(model.primitives)

model.babylonjs()

model2 = model.copy()

assert model == model2