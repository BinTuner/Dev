#!/usr/bin/env python
#
#
import adddeps  
import argparse
import opentuner
import os
import time 
import math
import ast
import collections
import json
import logging
import random
import re
import shutil
import subprocess
import sys
import lzma


from opentuner.resultsdb.models import Result, TuningRun
from opentuner.search import manipulator

from opentuner import ConfigurationManipulator
from opentuner import EnumParameter
from opentuner import IntegerParameter
from opentuner import MeasurementInterface
from opentuner import Result
from opentuner.resultsdb.models import Result, TuningRun

argparser = argparse.ArgumentParser(parents=opentuner.argparsers())
argparser.add_argument('source', help='source file to compile')
argparser.add_argument('dependency', help='dependency -UTA', nargs='?')
argparser.add_argument('--compile-template',
                       default='{cc} {source} -o {output} -lpthread {flags}',
                       help='command to compile {source} into {output} with'
                            ' {flags}')
argparser.add_argument('--compile-limit', type=float, default=30,
                       help='kill gcc if it runs more than {default} sec')
argparser.add_argument('--scaler', type=int, default=4,
                       help='by what factor to try increasing parameters')
argparser.add_argument('--cc', default='g++', help='g++ or gcc')
argparser.add_argument('--output', default='./tmp.bin',
                       help='temporary file for compiler to write to')
argparser.add_argument('--debug', action='store_true',
                       help='on gcc errors try to find minimal set '
                            'of args to reproduce error')
argparser.add_argument('--force-killall', action='store_true',
                       help='killall cc1plus before each collection')
argparser.add_argument('--memory-limit', default=1024 ** 3, type=int,
                       help='memory limit for child process')
argparser.add_argument('--no-cached-flags', action='store_true',
                       help='regenerate the lists of legal flags each time')
argparser.add_argument('--flags-histogram', action='store_true',
                       help='print out a histogram of flags')
argparser.add_argument('--flag-importance',
                       help='Test the importance of different flags from a '
                            'given json file.')


LLVM_detect=    ['llvm'] # detect compiler
LLVM_FLAGS_fno = [

  #'aligned-allocation', 
  
  'blocks',
  'borland-extensions', 
  'delayed-template-parsing',
  'fast-math',
  'ms-extensions', 'access-control', 'autolink','common',
  'elide-constructors','integrated-as',
  
  'jump-tables', 'lax-vector-conversions', 'merge-all-constants', 'objc-infer-related-result-type',
  'reroll-loops', 

  'preserve-as-comments',
  'stack-protector', 'standalone-debug',  
  'threadsafe-statics', 'trigraphs', 'unroll-loops',
  
  'objc-weak',  'reciprocal-math',
  'relaxed-template-template-args', 'rtlib-add-rpath',  'sized-deallocation',
  'slp-vectorize', 'strict-enums',
  'strict-return',  
  'wrapv', 'zvector',  
  'whole-program-vtables',  'lto',
  
  #----------------------------------------- -----------options
  #'profile-instr-use',  
  #, 'use-cxa-atexit'
  #  'use-init-array', 'objc-arc-exceptions', 'objc-exceptions',
  #,'gnu-inline-asm'
  # , 'modules'  ,'ms-compatibility',
     
    
  #'rtlib-add-rpath', 'rtti', 'sanitize-cfi-cross-dso',
  #'sanitize-memory-track-origins', 'sanitize-stats', 'sanitize-thread-atomics',
  #'sanitize-thread-func-entry-exit', 'sanitize-thread-memory-access', 
    
  # 'sanitize-cfi-cross-dso',  
  #----------------------------------------- -----------options  
    
  #'whole-program-vtables',  'ltocc' 
    
  #'gnu-runtime',      LLVM only on 
  # 'sjlj-exception',  not on off command
  # 'pcc-struct-return', doesn't support linux hardware
  #  , 'reg-struct-return', doesn't support linux hardware  
  # , 'stack-protector-all' LLVM only on  
  #  'visibility-ms-compat', LLVM only on 
  #  'visibility-inlines-hidden', LLVM only on  
  #  , 'obj-arc' , ??? 
  # , 'coverage-mapping' , '-fcoverage-mapping' only allowed with '-fprofile-instr-generate'
  # , 'modules-ts' LLVM only on
  # , 'sanitize-blacklist' LLVM only off  
  # 'crash-diagnostics', LLVM only off
  # 'operator-names',  LLVM only off 
  #  , 'trapv'  LLVM only on  
]

# LLVM_FLAGS_no = [
  
#   #IP Optimization
#   'ip',
  
#   #Advanced Optimization
#   'unroll-aggressive', 'scalar-rep','ansi-alias', 'ansi-alias-check',
#   'complex-limited-range', 'alias-const', 'vec', 'vec-guard-write',
#   'use-intel-optimized-headers', 'intel-extensions', 'simd', 'simd-function-pointers',
    
#   #PG Optimization
#   'prof-src-dir', 'prof-data-order', 'prof-func-order', 'prof-func-groups',
    
#   #Inlining
#   'inline-forceinline','inline-calloc',
    
# ]

LLVM_FLAGS_mno = [
  'backchain', 
  'incremental-linker-compatible',
  'global-merge',
  'hvx-double',
  'hvx',
  'long-calls',  
]


LLVM_FLAGS_On = [
  'gnu-runtime',      
  'stack-protector-all',  
  #'visibility-ms-compat',      (12/6_C++)
  #'visibility-inlines-hidden', (12/6_C++) 
  #'modules-ts',
  'trapv',   
  
]

LLVM_FLAGS_Off = [
  'sanitize-blacklist',   
  'crash-diagnostics', 
  #'operator-names',  
]

GlobalOpt = 0


def Baseline_UTA():
    gcc_cmd = 'clang-5.0  -lstdc++  -std=c++11 -stdlib=libc++ -m64  -DSPEC -DNDEBUG -I./641  -g -O0 -march=native -DSPEC_OPENMP -DSPEC_LP64     641/FullBoard.cpp 641/KoState.cpp 641/Playout.cpp 641/TimeControl.cpp 641/UCTSearch.cpp 641/GameState.cpp 641/Leela.cpp 641/SGFParser.cpp 641/Timing.cpp 641/Utils.cpp 641/FastBoard.cpp 641/Matcher.cpp 641/SGFTree.cpp 641/TTable.cpp 641/Zobrist.cpp 641/FastState.cpp 641/GTP.cpp 641/MCOTable.cpp 641/Random.cpp 641/SMP.cpp 641/UCTNode.cpp                      -o O0.bin '
    os.popen(gcc_cmd)
  
class GccFlagsTuner(MeasurementInterface):

  def manipulator(self):
    """
    Define the search space by creating a
    ConfigurationManipulator
    """
    LLVM_FLAGS = LLVM_FLAGS_fno + LLVM_FLAGS_mno  + LLVM_FLAGS_On +LLVM_FLAGS_Off  + LLVM_detect
    #print "manipulator" 
    manipulator = ConfigurationManipulator()
    manipulator.add_parameter(
      IntegerParameter('opt_level', 0, 3))
    for flag in LLVM_FLAGS:
      manipulator.add_parameter(
        EnumParameter(flag,
                      ['on', 'off'])) # only on & off ( icc)
    #for param, min, max in GCC_PARAMS:
    #  manipulator.add_parameter(
    #    IntegerParameter(param, min, max))
    return manipulator
  

  def compile(self, cfg, id):
    """
    Compile a given configuration in parallel
    """
    LLVM_FLAGS = LLVM_FLAGS_fno + LLVM_FLAGS_mno + LLVM_FLAGS_On +LLVM_FLAGS_Off
     
    
    gcc_cmd = 'clang-5.0  -lstdc++  -std=c++11 -stdlib=libc++  -m64  -DSPEC -DNDEBUG -I./641  -g  -march=native -DSPEC_OPENMP -DSPEC_LP64     641/FullBoard.cpp 641/KoState.cpp 641/Playout.cpp 641/TimeControl.cpp 641/UCTSearch.cpp 641/GameState.cpp 641/Leela.cpp 641/SGFParser.cpp 641/Timing.cpp 641/Utils.cpp 641/FastBoard.cpp 641/Matcher.cpp 641/SGFTree.cpp 641/TTable.cpp 641/Zobrist.cpp 641/FastState.cpp 641/GTP.cpp 641/MCOTable.cpp 641/Random.cpp 641/SMP.cpp 641/UCTNode.cpp  -o ./tmp{0}.bin '.format(id)
    
    gcc_cmd += ' -O{0}'.format(cfg['opt_level'])
    OptLevel = ' -O{0}'.format(cfg['opt_level'])
    print cfg['opt_level']
    global GlobalOptLevel 
    GlobalOptLevel = OptLevel
    Default_seq = ''
    for flag in LLVM_FLAGS:
        
        if cfg[flag] == 'on':
           if flag in LLVM_FLAGS_fno: 
              gcc_cmd += ' -f{0}'.format(flag)  #-fno-{0}
 
           elif flag in LLVM_FLAGS_mno:
              gcc_cmd += ' -m{0}'.format(flag)
           elif flag in LLVM_FLAGS_On:
              gcc_cmd += ' -f{0}'.format(flag)
           elif flag in LLVM_FLAGS_Off:
              pass
        elif cfg[flag] == 'off':
           
           if flag in LLVM_FLAGS_fno: 
              gcc_cmd += ' -fno-{0}'.format(flag)  #-fno-{0}
           # elif flag in ICC_FLAGS_no: 
           #    gcc_cmd += ' -no-' + str(flag) 
           elif flag in LLVM_FLAGS_mno:
              gcc_cmd += ' -mno-{0}'.format(flag)
           elif flag in LLVM_FLAGS_On:
               pass
           elif flag in LLVM_FLAGS_Off:
              gcc_cmd += ' -fno-{0}'.format(flag)  #-fno-{0}


    print "---CMD---:"
    global clang_GlobalCMD
    clang_GlobalCMD = gcc_cmd
    print clang_GlobalCMD

    return self.call_program(gcc_cmd)
  
  def run_precompiled(self, desired_result, input, limit, compile_result, id):
    """
    Run a compile_result from compile() sequentially and return NCD
    """

    assert compile_result['returncode'] == 0

    try:    

        #f = os.popen('idal64 -c -A -SIDAMetrics_static_64_BB.py tmp0.bin')

        print GlobalOptLevel    
        #KC = (BasicBlockNumber*(BasicBlockNumber-1))/2

        #-------------------Kolmogorov complexity----------------
    
        fopen  = open("tmp0.bin",'r')
        P   = fopen.read()
        fopen.close()            #must close the file. The buffer may have influce on the result
        
        CP  = len(lzma.compress(P)) 
        NCP = CP / (len(P) + 2*(math.log(len(P))))
        #print len(P)
        #print CP
        #print NCP

        #-------------------Normalized Compression Distance-----
    
        fopen   = open("tmp0.bin",'r')
        gopen   = open("O0.bin",'r')
        P = fopen.read()
        O = gopen.read()       
        fopen.close()
        gopen.close()
        
        ncBytesXY = len(lzma.compress(P + O))
        ncBytesX = len(lzma.compress(P))
        ncBytesY = len(lzma.compress(O))        
    
        ncd = float(ncBytesXY - min(ncBytesX, ncBytesY)) / max(ncBytesX, ncBytesY)
    

        global clang_GlobalCMD       

        #NCP = 0
        #NCD = 0
        #print ("--NCP:%s" % NCP)
        print ("--NCD:%s" % ncd)

        global maximumValue # max ncd value
        global currentValue # current ncd value
        global countValue # set up iteration times 
        print "---Test----"
        
        print ("--Max:%s" % maximumValue)
        print ("--Current:%s" % currentValue)
        print ("--Count:%s" % countValue)
        
        if maximumValue != 0 :
            currentValue = ncd  #ncd
            if currentValue > maximumValue :
                  maximumValue = currentValue
                  if (maximumValue - currentValue) < currentValue*0.05 :
                       countValue +=1
                       print "---+1 1--"
                       if countValue >10:
                          print "---over-1--"
        os._exit(0)
                  else:
                    countValue = 0
            else:
                countValue +=1
                print "---+1 2--"
                if countValue >10:
                    print "---over-2--"
      os._exit(0)
       
            
        else:
            maximumValue = ncd  #ncd  


    finally:
        print "-------------------------------------------------"
        #self.call_program('rm ./tmp{0}.bin'.format(id))
    #print format(id)
    #return Result(time=run_result['time'])
    return Result(time=0 , NCD=ncd, CMD = VC_GlobalCMD) 

  def compile_and_run(self, desired_result, input, limit):
    """
    Compile and run a given configuration then
    return performance
    """
    #print "compile_and_run" 
    cfg = desired_result.configuration.data
    compile_result = self.compile(cfg, 0)
    return self.run_precompiled(desired_result, input, limit, compile_result, 0)


  def cfg_to_flags(self, cfg):
    flags = ['-O%d' % cfg['opt_level']]
    #flags.append('-m32')
    for flag in GCC_FLAGS:
      if cfg[flag] == 'on':
        eachflag = '-f' + flag
        flags.append(eachflag)
      elif cfg[flag] == 'off':
        eachflag = '-fno-' + flag
        flags.append(eachflag)
        #flags.append(self.invert_gcc_flag(flag))

    for param, min, max in GCC_PARAMS:
      paramflag = ' --param {0}={1}'.format( param, cfg[param])
      flags.append(paramflag)
    return flags  



  def make_command(self, cfg):
    return args.compile_template.format(source=args.source, output=args.output,
                                        flags=' '.join(self.cfg_to_flags(cfg)),
                                        cc=args.cc)

  def save_final_config(self, configuration):
    """called at the end of tuning"""
    print "Calculate Result"
    
  def save_list_config(self, List):
    """called at the end of tuning"""
    for i in range(1, 3, 1):
      json_filename = "UTA-" + str(i+1) +"-Rank.json"
      cmd_filename  = "UTA-" + str(i+1) +"-Rank.cmd"
      print "Rank" + str(i+1) +" flags written to UTA-" + str(i+1) +"-Rank.{json,cmd}"
      self.manipulator().save_to_file(List[0][i].configuration.data, json_filename)
      with open(cmd_filename, 'w') as fd:
        fd.write(self.make_command(List[0][i].configuration.data))  


    
if __name__ == '__main__':
  
  os.environ["TVHEADLESS"] = "1"  
  args = argparser.parse_args()
  args2 = argparser.parse_args()  
  print "Program Start"
  
  Baseline_UTA()

  clang_GlobalCMD  = []
  maximumValue = 0
  currentValue = 0
  countValue = 0

  GccFlagsTuner.main(args)

  