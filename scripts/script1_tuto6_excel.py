import tutorials.tutorial6_excel as tutorial
from dessia_common.files import BinaryFile


steam = BinaryFile.from_file("datas/excel_tuto6.xlsx")
parameter = tutorial.ParameterData.read_excel(stream=steam)

