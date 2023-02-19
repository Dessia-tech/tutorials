import random

from tutorials.knapsack_problem_with_displays import Knapsack, Generator, Item
from dessia_common.workflow.blocks import InstantiateModel, ModelMethod, ModelAttribute, MultiPlot, Markdown, Unpacker, \
    PlotData, CadView
from dessia_common.typings import MethodType
from dessia_common.datatools.dataset import Dataset
from dessia_common.workflow.core import TypedVariable, Pipe, Workflow

block_0 = InstantiateModel(model_class=Generator, name='GENERATOR', position=[-426.27884474719355, -197.67219288999567])
block_1 = ModelMethod(method_type=MethodType(Generator, 'generate'), name='_generate_',
                      position=[-124.05791819073008, -185.06367196641366])
block_2 = InstantiateModel(model_class=Dataset, name='DATASET', position=[162.1159937393057, -96.39613408640047])
block_3 = ModelAttribute(attribute_name='dessia_objects', name='extract',
                         position=[452.9770685403816, 1.7984784075740556])
block_4 = MultiPlot(attributes=['mass', 'price', 'golds', 'silvers', 'bronzes'], name='Multiplot',
                    position=[781.280317117172, -141.01673915293895])
block_5 = Markdown(name='MarkDown')
block_6 = Unpacker(indices=[0], name='extract_solution', position=[804.5481046770818, 112.7202979561202])
block_7 = PlotData(name='plot_2d')
block_8 = CadView(name='CAD')
blocks = [block_0, block_1, block_2, block_3, block_4, block_5, block_6, block_7, block_8]

variable_0 = TypedVariable(name='Result Name', position=[-135.41769504700423, 146.07556919422217], type_=str)

pipe_0 = Pipe(block_0.outputs[0], block_1.inputs[0])
pipe_1 = Pipe(block_1.outputs[0], block_2.inputs[0])
pipe_2 = Pipe(variable_0, block_2.inputs[1])
pipe_3 = Pipe(block_2.outputs[0], block_3.inputs[0])
pipe_4 = Pipe(block_3.outputs[0], block_4.inputs[0])
pipe_5 = Pipe(block_2.outputs[0], block_5.inputs[0])
pipe_6 = Pipe(block_3.outputs[0], block_6.inputs[0])
pipe_7 = Pipe(block_6.outputs[0], block_7.inputs[0])
pipe_8 = Pipe(block_6.outputs[0], block_8.inputs[0])
pipes = [pipe_0, pipe_1, pipe_2, pipe_3, pipe_4, pipe_5, pipe_6, pipe_7, pipe_8]

workflow = Workflow(blocks, pipes, output=block_3.outputs[0], name='WORKFLOW KNAPSACK PROBLEM_Display')


def generate_random_item(i: int):
    mass = random.uniform(0.1, 1)
    price = random.uniform(0.5, 1000)
    name = f'Item_{i}'
    return Item(mass=mass, price=price, name=name)


items = [generate_random_item(i=i) for i in range(10)]

value_0_0 = items
value_0_1 = Knapsack(allowed_mass=30, name="knapsack")
value_1_1 = 5
value_nbv_0 = 'str'
input_values = {
    workflow.input_index(block_0.inputs[0]): value_0_0,
    workflow.input_index(block_0.inputs[1]): value_0_1,
    workflow.input_index(block_1.inputs[1]): value_1_1,
    workflow.input_index(variable_0): value_nbv_0,
}

workflow_run = workflow.run(input_values=input_values)
