"""
import pandas as pd 
table = pd.read_excel('gcc_400_result.xls')
b = table['CMD']
print "---"
print b
"""

"""
import xlrd
a = xlrd.open_workbook('gcc_400_result.xls')
sheet = a.sheets()[0]
sheet.col_values(19)
print sheet.col_values(20)
"""
import os
import xlrd
data = xlrd.open_workbook('clang_400_result.xls')
table = data.sheet_by_index(0)

nrows = table.nrows
ncols = table.ncols
print "---------"
print nrows
#print ncols

for row in range(0,nrows ):
	print "---"
	print row
	print nrows 
	options = table.cell(row,18).value 
	number = row 
	print '#'+str(number+1)
	gcc_cmd = options+' -o gcc-400-'+str(number+1)+'.bin'
	print gcc_cmd
	os.popen(gcc_cmd)
	