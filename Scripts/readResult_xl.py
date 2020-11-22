import sys
import os
import time
import xlrd
import xlwt
from xlutils.copy import copy
# python readResult_xl.py O0_vs_

print "--- read .result files and store it to excel   --->"

if len(sys.argv) < 4:
   print "Usage: python readResult_xl.py $BinExport-0 $BinExport-X $countV"
   sys.exit(1)

baselineBE = sys.argv[1].split('.')[0]
startBE = sys.argv[2].split('.')[0]
countV = int(sys.argv[3].split('.')[0])

print('one:', baselineBE)  # O0.BinExport
print('two:', startBE)  # x.BinExport
print('two:', countV)  # 5010

count = 1  #5010
while (count < countV):
  print '#:', count
  # FileBindff = baselineBE + '_vs_' +startBE+str(count) + '.results'
  # print FileBindff
  if "-" in startBE:
    FileBindff = baselineBE + '_vs_' +startBE+str(count) + '.results'
    
  else:
    FileBindff = baselineBE + '_vs_' +startBE + '.results'
    

  f = open(FileBindff,'r') 
  for read in f.readlines():  # remove  '\n'
    tmp =read.strip('\n')           
    if tmp.split(':')[0] == 'similarity':
      print "---------- similarity ---------"
      dif = 1 - float(tmp.split(':')[1])
      print dif
      f = xlrd.open_workbook('clang_400_result.xls',formatting_info =True)
      #get sheet page
      r_sheet = f.sheet_by_index(0)
      #get sheet lines
      row = r_sheet.nrows

      #copy
      wb = copy(f)
      #get sheet
      w_sheet = wb.get_sheet(0)



      countFromLast = int(count) -1

      print('xixi->:', countFromLast)
      #row= line
    
      if baselineBE == 'O0':
        if startBE == 'O1':
          w_sheet.write(countFromLast,27,str(dif)) 
          w_sheet.write(countFromLast,28,str(float(tmp.split(':')[1])*100)+"%")
        elif startBE == 'O2':
          w_sheet.write(countFromLast,29,str(dif)) 
          w_sheet.write(countFromLast,30,str(float(tmp.split(':')[1])*100)+"%")
        elif startBE == 'O3':
          w_sheet.write(countFromLast,31,str(dif)) 
          w_sheet.write(countFromLast,32,str(float(tmp.split(':')[1])*100)+"%")
        else:    
          w_sheet.write(countFromLast,7,str(dif) ) 
          w_sheet.write(countFromLast,8,str(float(tmp.split(':')[1])*100)+"%")
          #print '-->O0'
      elif baselineBE == 'O1': 
          #print '-->O1'
          w_sheet.write(countFromLast,9,str(dif) ) #7 9 11
          w_sheet.write(countFromLast,10,str(float(tmp.split(':')[1])*100)+"%")#8 10 12
      elif baselineBE == 'O2': 
          #print '-->O2'
          w_sheet.write(countFromLast,11,str(dif) ) #7 9 11
          w_sheet.write(countFromLast,12,str(float(tmp.split(':')[1])*100)+"%")#8 10 12
      elif baselineBE == 'O3': 
          #print '-->O3'
          w_sheet.write(countFromLast,13,str(dif) ) #7 9 11
          w_sheet.write(countFromLast,14,str(float(tmp.split(':')[1])*100)+"%")#8 10 12
      else:
          print 'Error!!!' 
      # w_sheet.write(countFromLast,11,str(dif)+"%" ) #7 9 11
      # w_sheet.write(countFromLast,12,str(float(tmp.split(':')[1])*100)+"%")#8 10 12

      #save
      wb.save('clang_400_result.xls')

      print "--Bindiff finish----"
      break

  count = count + 1

'''
differ -log_format  --primary=/media/xl/400_creatBin/gcc-400-2.BinExport --secondary=/media/xl/400_creatBin/gcc-400-1.BinExport
BinDiff 4.3.0, (c)2004-2011 zynamics GmbH, (c)2011-2017 Google Inc.
setup: 0.08s sec.
primary:   gcc-400-2: 266 functions, 1416 calls
secondary: gcc-400-1: 266 functions, 1416 calls
matching: 0.06 sec.
matched: 266 of 266/266 (primary/secondary, 264/264 non-library)
call graph MD index: primary          15.699800
                     secondary        15.699800
similarity: 99.2752% (confidence: 99.2752%)
writing results: 0.999 sec.

'''

print "--- ----- end ------ --->"
