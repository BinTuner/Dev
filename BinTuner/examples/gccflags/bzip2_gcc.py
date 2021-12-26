#!/usr/bin/env python
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


GCC_FLAGS = [
  #O1
  'auto-inc-dec', 'branch-count-reg', 'combine-stack-adjustments',
  'compare-elim', 'cprop-registers', 'dce',
  'defer-pop', 'delayed-branch', 'dse',
  'forward-propagate', 'guess-branch-probability', 'if-conversion2',
  'if-conversion', 'inline-functions-called-once', 'ipa-pure-const',
  'ipa-profile', 'ipa-reference', 'merge-constants',
  'move-loop-invariants', 'reorder-blocks', 'shrink-wrap',
  'split-wide-types', 'tree-bit-ccp', 'tree-ccp',
  'tree-ch', 'tree-coalesce-vars', 'tree-copy-prop',
  'tree-dce',  'tree-dse', 'tree-forwprop',
  'tree-fre', 'tree-sink', 'tree-slsr',
  'tree-sra', 'tree-pta', 'tree-ter', 
  'unit-at-a-time', 'omit-frame-pointer',
  'tree-phiprop',  
  'tree-dominator-opts',  
  'ssa-backprop',
  'ssa-phiopt',
  'shrink-wrap-separate',
  #------------------------------------
  # O2
  'thread-jumps', 'align-functions', 'align-labels',
  'align-labels', 'align-loops', 'caller-saves',
  'crossjumping', 'cse-follow-jumps', 'cse-skip-blocks',
  'delete-null-pointer-checks', 'devirtualize', 'devirtualize-speculatively',
  'expensive-optimizations', 'gcse', 'gcse-lm',
  'hoist-adjacent-loads', 'inline-small-functions', 'indirect-inlining',
  'ipa-cp', 'ipa-sra', 'ipa-icf',
  'isolate-erroneous-paths-dereference', 'lra-remat', 'optimize-sibling-calls',
  'optimize-strlen', 'partial-inlining', 'peephole2',
  'reorder-blocks-and-partition', 'reorder-functions', 'rerun-cse-after-loop',
  'sched-interblock', 'sched-spec', 'schedule-insns', 
  'strict-aliasing', 'strict-overflow', 'tree-builtin-call-dce',
  'tree-switch-conversion', 'tree-tail-merge',
  'tree-pre', 'tree-vrp', 'ipa-ra',
  'reorder-blocks',  
  'schedule-insns2',
  'code-hoisting',
  'store-merging', 
  'reorder-blocks-algorithm', #simple, stc
  'ipa-bit-cp',
  'ipa-vrp',
  #------------------------------------
  # O3
  'inline-functions', 'unswitch-loops', 'predictive-commoning',
  'gcse-after-reload', 'tree-loop-vectorize', 'tree-loop-distribute-patterns',
  'tree-slp-vectorize', 'vect-cost-model', 'tree-partial-pre',
  'peel-loops', 'ipa-cp-clone',
  'split-paths', 
  'tree-vectorize',
]


# (name, min, max)
GCC_PARAMS = [
  ('early-inlining-insns', 0, 1000),
  ('gcse-cost-distance-ratio', 0, 100),
  ('iv-max-considered-uses', 0, 1000),
  # ... (145 total)
]

GlobalOpt = 0


def Baseline_UTA():
    gcc_cmd = 'gcc -O0  -DSPEC_CPU -DNDEBUG    benchmarks/bzip2.c    -lm    -o O0.bin'
    os.popen(gcc_cmd)
	
class GccFlagsTuner(MeasurementInterface):

  def manipulator(self):
    """
    Define the search space by creating a
    ConfigurationManipulator
    """

    manipulator = ConfigurationManipulator()
    manipulator.add_parameter(
      IntegerParameter('opt_level', 0, 3))
    for flag in GCC_FLAGS:
      manipulator.add_parameter(
        EnumParameter(flag,
                      ['on', 'off'])) 
    for param, min, max in GCC_PARAMS:
      manipulator.add_parameter(
        IntegerParameter(param, min, max))
    return manipulator
  

  def compile(self, cfg, id):
    """
    Compile a given configuration in parallel
    """   
      
    gcc_cmd = 'gcc benchmarks/bzip2.c -lm -o ./tmp{0}.bin'.format(id)
    
    gcc_cmd += ' -O{0}'.format(cfg['opt_level'])
    OptLevel = ' -O{0}'.format(cfg['opt_level'])
    print "--- BinTuner ---"
    #print cfg['opt_level']
    global GlobalOptLevel 
    GlobalOptLevel = OptLevel
    Default_seq = ''
    for flag in GCC_FLAGS:
      if flag != 'reorder-blocks-algorithm':
        if cfg[flag] == 'on':
          gcc_cmd += ' -f{0}'.format(flag)
        elif cfg[flag] == 'off':
          gcc_cmd += ' -fno-{0}'.format(flag)
        elif cfg[flag] == 'default':
          Default_seq += ' -f{0}'.format(flag) +'\n'
      else:
        if cfg[flag] == 'on':
          gcc_cmd += ' -f{0}'.format(flag) + '=simple'
        elif cfg[flag] == 'off':
          gcc_cmd += ' -f{0}'.format(flag) + '=simple'
    
    for param, min, max in GCC_PARAMS:
      temp = ' --param {0}={1}'.format( param, cfg[param])
      gcc_cmd += ' --param {0}={1}'.format(
        param, cfg[param])

    
    print "--- CMD---:"
    global VC_GlobalCMD
    VC_GlobalCMD = gcc_cmd
    print VC_GlobalCMD
    #print gcc_cmd

    return self.call_program(gcc_cmd)
  
  def run_precompiled(self, desired_result, input, limit, compile_result, id):
    """
    Run a compile_result from compile() sequentially and return NCD
    """

    assert compile_result['returncode'] == 0

    try:    

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

  
 
        global VC_GlobalCMD
		
        #NCP = 0
        #NCD = 0
        #print ("--NCP:%s" % NCP)
        print ("--NCD:%s" % ncd)

        global maximumValue
        global currentValue
        global countValue
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
                       if countValue >100:
                         print "---over-1--"
                  else:
                    countValue = 0
            else:
                countValue +=1
                print "---+1 2--"
                if countValue >100:
                   print "---over-2--"
            
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
    return 
    """
    cfg = desired_result.configuration.data
    compile_result = self.compile(cfg, 0)
    return self.run_precompiled(desired_result, input, limit, compile_result, 0)


  def cfg_to_flags(self, cfg):
    flags = ['-O%d' % cfg['opt_level']]
    for flag in GCC_FLAGS:
      if cfg[flag] == 'on':
        eachflag = '-f' + flag
        flags.append(eachflag)
      elif cfg[flag] == 'off':
        eachflag = '-fno-' + flag
        flags.append(eachflag)

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

  VC_GlobalCMD  = []
  maximumValue = 0
  currentValue = 0
  countValue = 0

  GccFlagsTuner.main(args)
  

  
  
