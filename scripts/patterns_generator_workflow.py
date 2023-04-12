import plot_data

import tutorials.pattern_generator as patterns
from dessia_common.workflow.core import Pipe, Workflow
from dessia_common.workflow.blocks import InstantiateModel, ModelMethod, MultiPlot

from dessia_api_client.users import PlatformUser
from dessia_common.typings import MethodType

block_generator = InstantiateModel(patterns.PatternGenerator,
                                      name='Pattern Generator')
block_generate = ModelMethod(MethodType(class_=patterns.PatternGenerator,
                                           name='generate'), name='Generate')

list_attribute = ['minor_axis_size_in_mm', 'excentricity',
                  'clearence', 'piece_diameter']
display = MultiPlot(list_attribute, order=1, name='Display')

# display = Display(name='Display')

block_workflow = [block_generator, block_generate]

pipe_workflow = [Pipe(block_generator.outputs[0], block_generate.inputs[0]),
                 Pipe(block_generate.outputs[0], display.inputs[0])]

workflow = Workflow(block_workflow, pipe_workflow,
                       block_generate.outputs[0])

list_diameters = [0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3]
excentricity_min_max = (0.3, 0.9)
diameter_percetage_clearence_min_max = (0.1, 0.6)
MINOR_AXIS_SIZE_IN_MM = 1

input_values = {workflow.input_index(block_generator.inputs[0]):
                    MINOR_AXIS_SIZE_IN_MM,
                workflow.input_index(block_generator.inputs[1]):
                    list_diameters,
                workflow.input_index(block_generator.inputs[2]):
                    excentricity_min_max,
                workflow.input_index(block_generator.inputs[3]):
                    diameter_percetage_clearence_min_max}

workflow_run = workflow.run(input_values)
# c = PlatformUser(api_url='https://api.platform-dev.dessia.tech')
# r = c.objects.create_object_from_python_object(workflow)
