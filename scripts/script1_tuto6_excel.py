# import tutorials.tutorial6_excel as tuto
# import plot_data.core as plot_data
# import volmdlr as vm

# from openpyxl import load_workbook
# from xlcalculator import ModelCompiler
# from xlcalculator import Evaluator

# # modify and update data of your excel file
# wb2 = load_workbook('datas/excel_tuto6.xlsx')
# ws = wb2.active
# ws['B2'] = 10
# print('value modify', ws['B2'].value)

# # create a copy and excecute excel simulation
# wb2.save('datas/excel_tuto6_bis.xlsx')
# filename = r'datas/excel_tuto6_bis.xlsx'

# compiler = ModelCompiler()
# new_model = compiler.read_and_parse_archive(filename)
# evaluator = Evaluator(new_model)
# sum1 = evaluator.evaluate('general!B8').value
# print('new sum', sum1)

# # build your python obj
# param1 = ws['B2'].value
# param2 = ws['B3'].value
# param3 = ws['B4'].value
# param4 = ws['B5'].value
# param5 = ws['B6'].value

# data1 = tuto.Datas(param1=param1, param2=param2,
#                    param3=param3, param4=param4, param5=param5,
#                    sum=sum1)

# print(data1.to_dict())
