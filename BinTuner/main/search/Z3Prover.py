# Copyright (c) 

from z3 import *

def z3function(options):
    p, q, w, first, second, third, four, five = Bools('p q w first second third four five')

    print "************************ Z3 ************************"

    s = Solver()

    #"----O1----"
    if options['ftreeBitCpp'] == 'on':
	if options['ftreeCpp'] == 'on':
	    first = True
	    print "1- Result--> Available"
	else:
	    first = False
	    print "1- Result--> Unavailable"
    #-------
    s.push()
    s.add(And(p,q) == True)
    if options['fShrinkWrapSeparate'] == 'on':
       s.add(p == True)
       if options['fShrinkWrap'] == 'on':
	   s.add(q == True)
       else:
	   s.add(q == False)
       if s.check() == sat:
	   print "5- Result--> Available"
	   five = True
       else:
	   print "5- Result--> Unavailable"
	   five = False
    s.pop()

    # "----O2----"
    s.push()
    s.add(And(p,q) == True)
    if options['fEPathsDereference'] == 'on':
       s.add(p == True)
       if options['fNPointerChecks'] == 'on':
	   s.add(q == True)
       else:
	   s.add(q == False)
       if s.check() == sat:
	   print "2- Result--> Available"
	   second = True
       else:
	   print "2- Result--> Unavailable"
	   second = False
    s.pop()
    #-------
    s.push()
    s.add(And(p,q) == True)

    if (options['fpartialInlining'] == 'on' or options['findirectInlining'] == 'on'):
	s.add(p == True)
        if options['finlineFuntions'] == 'off':
	    if options['fSmallFuntions'] == 'off':
		s.add(q == False)
	    else:
		s.add(q == True)
	else:
	    s.add(q == True)
	if s.check() == sat:
	    print "3- Result--> Available"
	    third = True
	else:
	     print "3- Result--> Unavailable"
	     third = False
    s.pop()
    # "----O3----"

    s.push()
    s.add(And(p,q) == True)

    if (options['fTreeLoopVectorize'] == 'on' or options['fSlpVectorize'] == 'on'):
	s.add(p == True)
        if options['fTreeVectorize'] == 'off':
	    s.add(q == False)
	else:
	    s.add(q == True)
	if s.check() == sat:
	    print "4- Result--> Available"
	    four = True
	else:
	     print "4- Result--> Unavailable"
	     four = False
    s.pop()
    
    return first, second, third, four, five
    print "--- --- Z3 Done --- ---"
