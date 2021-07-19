

from z3 import *

def z3function(options):
    p, q, w = Bools('p q w')

    print "--- Z3 Begin -- The Optimization Options Check ---"

    #solve(And(p,q) == True, p == True, q == True)
    s = Solver()

    print "----1----"
    s.push()
    s.add(And(p,q) == True)
    if options['ftreeCpp'] == 'on':
	s.add(p == True)
    else:
	s.add(p == False)
    #s.add(p == a)

    if options['ftreeBitCpp'] == 'on':
	s.add(q == True)
    else:
	s.add(q == False)
    #s.add(q == b)

    if s.check() == sat:
     	print "Result--> Available"
    else:
     	print "Result--> Unavailable"

    print "[ -ftree-cpp     = %s ]" % options['ftreeCpp']
    print "[ -ftree-bit-cpp = %s ]" % options['ftreeBitCpp']
    s.pop()

    print "----2----"
    s.push()
    s.add(And(p,q) == True)
    if options['fEPathsDereference'] == 'on':
	s.add(p == True)
    else:
	s.add(p == False)

    if options['fNPointerChecks'] == 'on':
	s.add(p == True)
    else:
	s.add(p == False)

    if s.check() == sat:
     	print "Result--> Available"
    else:
     	print "Result--> Unavailable"

    print "[ -fisolate-erroneous-paths-dereference = %s ]" % options['fEPathsDereference']
    print "[ -fdelete-null-pointer-checks          = %s ]" % options['fNPointerChecks']
    s.pop()

    print "----3----"
    s.push()
    s.add(And(p,q,w) == True)

    if options['fpartialInlining'] == 'on':
	s.add(p == True)
    else:
	s.add(p == False)

    if options['finlineFuntions'] == 'on':
	s.add(p == True)
    else:
	s.add(p == False)

    if options['fSmallFuntions'] == 'on':
	s.add(p == True)
    else:
	s.add(p == False)

    if s.check() == sat:
     	print "Result--> Available"
    else:
     	print "Result--> Unavailable"

    print "[ -fpartial-inlining       = %s ]" % options['fpartialInlining']
    print "[ -finline-functions       = %s ]" % options['finlineFuntions']
    print "[ -finline-small-functions = %s ]" % options['fSmallFuntions']
    s.pop()
    print "--- --- Z3 Done --- ---"
