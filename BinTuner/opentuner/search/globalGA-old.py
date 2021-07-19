import abc
import copy
import random
import Z3Prover
from technique import SearchTechnique
from opentuner.search import technique

class GlobalEvolutionaryTechnique(SearchTechnique):
  countNumber = 0
  def __init__(self,
               mutation_rate = 0.1,
               crossover_rate = 0.0,
               must_mutate_count = 1,
	             crossover_strength = 0.1,
               *pargs, **kwargs):
    super(GlobalEvolutionaryTechnique, self).__init__(*pargs, **kwargs)
    self.mutation_rate = mutation_rate
    self.crossover_rate = crossover_rate
    self.must_mutate_count = must_mutate_count
    self.crossover_strength = crossover_strength
  
  @classmethod
  def get_hyper_parameters(cls):
    return ['mutation_rate', 'crossover_rate', 'must_mutate_count', 'crossover_strength']


  def desired_configuration(self):

    """
    return a (cfg, priority) that we should test,
    through random mutation and crossover
    """
    #TODO: set limit value
    #print "globalGA"
    parents = self.selection()
    parents = map(copy.deepcopy, parents)
    parent_hashes = map(self.manipulator.hash_config, parents)

    if len(parents) > 1:
      cfg = self.crossover(parents)
      #print parents
      #print '--------------------'
    else:
      cfg = parents[0]
    print "beformutation"
    for z in xrange(10): #retries
      # while (true)  ------------------------for z3
      self.mutation(cfg)  # The final step to generate cfg

      copycfg = cfg  
      copycfg = self.convertDefault(copycfg)

      #Invoking the Z3 Prover() Xiaolei 080817
      optionsDic = {'ftreeCpp':copycfg['tree-ccp'],'ftreeBitCpp':copycfg['tree-bit-ccp'],'fEPathsDereference':copycfg['isolate-erroneous-paths-dereference'],'fNPointerChecks':copycfg['delete-null-pointer-checks'],'fpartialInlining':copycfg['partial-inlining'],'finlineFuntions':copycfg['inline-functions'],'fSmallFuntions':copycfg['inline-small-functions']}
      
      z3first,z3second,z3third = Z3Prover.z3function(options = optionsDic)  
     
      print "[ Z3 return Results = %s %s %s ]" %(z3first,z3second,z3third) 
    
      if z3first == False:
          cfg['tree-ccp'] = 'on'
	  print 'Changed "tree-ccp" value'
      if z3second == False:
          cfg['delete-null-pointer-checks'] = 'on'
          print 'Changed "delete-null-pointer-checks" value'
      #if z3third == False:
      if z3third == True:
	  rchoice = random.choice(['inline-functions','inline-small-functions'])
	  print '------------------------------'
	  print rchoice
          cfg[rchoice] = 'on'
	  print 'Change' ,rchoice,'value'

      #----------------------------------------for z3  the end of while      
      if self.manipulator.hash_config(cfg) in parent_hashes:
        continue # try again
      return cfg
  
  def convertDefault(self, cfg):
    OptLevel = ' -O{0}'.format(cfg['opt_level']) 
    items = cfg.iteritems()
    for flag,value in items:
      if OptLevel == ' -O0':
         if flag == 'tree-ccp' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'tree-bit-ccp' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'isolate-erroneous-paths-dereference' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'delete-null-pointer-checks' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'partial-inlining' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'inline-functions' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'inline-small-functions' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         #--7.0 new rule interface
         if flag == 'shrink-wrap-separate' and cfg[flag] == 'default':  
            cfg[flag] = 'on'
         if flag == 'ipa-bit-cp' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'ipa-vrp' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'split-paths' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'tree-vectorize' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'tree-loop-vectorize' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'tree-slp-vectorize' and cfg[flag] == 'default':
            cfg[flag] = 'off'
      if OptLevel == ' -O1':
         if flag == 'tree-ccp' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'tree-bit-ccp' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'isolate-erroneous-paths-dereference' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'delete-null-pointer-checks' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'partial-inlining' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'inline-functions' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'inline-small-functions' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'shrink-wrap-separate' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'ipa-bit-cp' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'ipa-vrp' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'split-paths' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'tree-vectorize' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'tree-loop-vectorize' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'tree-slp-vectorize' and cfg[flag] == 'default':
            cfg[flag] = 'off'
      if OptLevel == ' -O2':
         if flag == 'tree-ccp' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'tree-bit-ccp' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'isolate-erroneous-paths-dereference' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'delete-null-pointer-checks' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'partial-inlining' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'inline-functions' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'inline-small-functions' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'shrink-wrap-separate' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'ipa-bit-cp' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'ipa-vrp' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'split-paths' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'tree-vectorize' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'tree-loop-vectorize' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'tree-slp-vectorize' and cfg[flag] == 'default':
            cfg[flag] = 'off'
      if OptLevel == ' -O3':
         if flag == 'tree-ccp' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'tree-bit-ccp' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'isolate-erroneous-paths-dereference' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'delete-null-pointer-checks' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'partial-inlining' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'inline-functions' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'inline-small-functions' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'shrink-wrap-separate' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'ipa-bit-cp' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'ipa-vrp' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'split-paths' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'tree-vectorize' and cfg[flag] == 'default':
            cfg[flag] = 'off'
         if flag == 'tree-loop-vectorize' and cfg[flag] == 'default':
            cfg[flag] = 'on'
         if flag == 'tree-slp-vectorize' and cfg[flag] == 'default':
            cfg[flag] = 'on'
    return cfg         
      
  def mutation(self, cfg):
    
    """
    mutate cfg in place
    """
    params = self.manipulator.parameters(cfg)
    random.shuffle(params)
    for param in params[:self.must_mutate_count]:
      self.mutate_param(cfg, param)
    for param in params[self.must_mutate_count:]:
      if random.random() < self.mutation_rate:
        self.mutate_param(cfg, param)

  def mutate_param(self, cfg, param):
    """
    mutate single parameter of cfg in place
    """
    param.op1_randomize(cfg)

  def crossover(self, cfgs):
    cfg1, cfg2, = cfgs
    new = self.manipulator.copy(cfg1)

    params = self.manipulator.parameters(cfg1)
    random.shuffle(params)
    #print list(cfg1)
    #print list(new)
    d = int(self.crossover_strength*len(params))
    #print cfg1
    #print self.crossover_strength
    for param in params[:d]:
      #print param.name  
      param.set_value(new, param.get_value(cfg2))
    return new

  def selection(self):
    """return a list of parent configurations to use"""
    if random.random() < self.crossover_rate:
      return [self.select(),
              self.select()]
    else:
      return [self.select()]

  @abc.abstractmethod
  def select(self):
    """return a single random parent configuration"""
    return None

class GreedySelectionMixin(object):
  """
  EvolutionaryTechnique mixin for greedily selecting the best known
  configuration
  """
  def select(self):
    """return a single random parent configuration"""
    if (self.driver.best_result is not None and
        self.driver.best_result.state == 'OK'):
      return self.driver.best_result.configuration.data
    else:
      return self.manipulator.random()

class NormalMutationMixin(object):
  """
  Mutate primitive parameters according to normal distribution
  """

  def __init__(self, sigma = 0.1, *pargs, **kwargs):
    super(NormalMutationMixin, self).__init__(*pargs, **kwargs)
    self.sigma = sigma

  def mutate_param(self, cfg, param):
    """
    mutate single parameter of cfg in place
    """
    if param.is_primitive():
      param.op1_normal_mutation(cfg, self.sigma)
    else:
      random.choice(param.manipulators(cfg))(cfg)


class UniformGreedyMutation(GreedySelectionMixin, GlobalEvolutionaryTechnique):
  pass

class NormalGreedyMutation(NormalMutationMixin, GreedySelectionMixin, GlobalEvolutionaryTechnique):
  pass

technique.register(NormalGreedyMutation( crossover_rate=0.5, crossover_strength=0.2, name='GGA'))
