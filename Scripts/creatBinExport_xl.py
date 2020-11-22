# use .i64 file  creat .BinExport file
# python creatBinExport_xl.py gcc-400- 5010

import sys
import os

#import globalvar as GlobalVar

#import threading as thd
import time



print "--- creat .BinExport file  --->"
#print('sys.argv:',sys.argv)
#print sys.argv
if len(sys.argv) < 3:
   print "Usage: python creatBinExport_xl.py $base $count"
   sys.exit(1)

baseName = sys.argv[1].split('.')[0]
countV = int(sys.argv[2].split('.')[0])

print('one:', baseName)  # gcc-400-
print('two:', countV)  # 5010



count = 1  #3889
while (count < countV):
  print '#:', count
  #gl.set_value('cValue', count)
  #GlobalVar.set_mq_client('10')
  #ftxt = open("store.txt",'wb')
  #ftxt.write(str(count))
  #ftxt.close()
  #print gl.set_value('cValue', count)

  #metricsCMD = 'idaq64 -c -A -SIDAMetrics_xl.py ' + baseName  + str(count) +'.bin'  # add other row number = i value  /home/xl/Downloads/llvm/clang_400_ncd_top10

  metricsCMD = 'idaq64 -A -c -OExporterModule:"/home/xl/Downloads/llvm/clang_400_ncd_top10/" -S"bindiff_export.idc" ' + baseName  + str(count) +'.bin'
  #subprocess.call(["idaq64","-OExporterModule:" + SecFile,"-S\""bindiff_export.idc"\"", str(count) + ".i64"])



  print metricsCMD
  os.system(metricsCMD)  
  count = count + 1

  

'''
idaq64 -A -OExporterModule:"/media/xl/400_creatBin/" -S"bindiff_export.idc" "gcc-400-2.i64"

'''

 
print "--- ----- end ------ --->"
