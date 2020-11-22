# differ O0.BinExport with gcc-400-1.BinExport and get .result file 
import sys
import os
import time
# differ -log_format --primary=/media/xl/400_creatBin/gcc-400-2.BinExport --secondary=/media/xl/400_creatBin/gcc-400-1.BinExport

print "--- differ .BinExport files  --->"

if len(sys.argv) < 4:
   print "Usage: python differ_xl.py $BinExport-0 $BinExport-X $countV"
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
  #metricsCMD = 'differ -log_format  --primary=/media/xl/445_creatBin/'+ baselineBE + '.BinExport' + ' --secondary=/media/xl/445_creatBin/' + startBE +str(count) + '.BinExport'
  #metricsCMD = 'idaq64 -A -c -OExporterModule:"/media/xl/400_creatBin/" -S"bindiff_export.idc" ' + baseName  + str(count) +'.bin'
  metricsCMD = 'differ -log_format  --primary=/home/xl/Downloads/llvm/clang_400_ncd_top10/'+ baselineBE + '.BinExport' + ' --secondary=/home/xl/Downloads/llvm/clang_400_ncd_top10/' + startBE +str(count) + '.BinExport'

  print metricsCMD
  os.system(metricsCMD)  
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
