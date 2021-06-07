BinTuner
---------------------
BinTuner is a cost-efficient auto-tuning framework, which can deliver a near-optimal binary code that reveals much more differences than -Ox settings. it also can assist the binary code analysis research in generating more diversified datasets for training and testing.

Since the experiment lasted several months, including extensive testing with multiple compilers, we got more than a hundred thousand binary intermediate files, we could imagine that how big the files would be, so we are trying to find other ways to upload and share the intermediate files and experimental results.

The architecture of BinTuner:
---------------------
![image](https://github.com/BinTuner/Dev/blob/main/Results/Images/BinTuner.png)



The core on the server-side is a metaheuristic search engine (e.g., the genetic algorithm), which directs iterative compilation towards maximizing the effect of binary code differences. 

The client-side runs different compilers (GCC, LLVM ...) and the calculation of the fitness function. 

Both sides communicate valid optimization options, fitness function scores, and compiled binaries to each other, and these data are stored in a database for future exploration. When BinTuner reaches a termination condition, we select the iterations showing the highest fitness function score and output the corresponding binary code as the final outcomes.

System dependencies
--------------------

A list of system dependencies can be found in [packages-deps](https://github.com/BinTuner/Dev/blob/main/packages-deps) which are primarily python 2.6+ (not 3.x) and sqlite3.

On Ubuntu/Debian there can be installed with:
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install `cat packages-deps | tr '\n' ' '`
```
Installation
--------------------

Running it out of a git checkout, a list of python dependencies can be found in requirements.txt these can be installed system-wide with pip.
```
sudo apt-get install python-pip
sudo pip install -r requirements.txt
```

If you encounter an error message like this:

```
Could not find a version that satisfies the requirement fn>=0.2.12 (from -r requirements.txt (line 2)) (from versions:)
No matching distribution found for fn>=0.2.12 (from -r requirements.tet (line 2))
```
Please try again or install each manually

```
pip install fn>=0.2.12
...
pip install numpy>=1.8.0
...
```

If you encounter an error message like this:

```
ImportError: No module named lzma
```
Please install lzma
```
sudo apt-get install python-lzma
```



Install Compiler
--------------------
GCC

Check to see if the compiler is installed

e.g. 
```
gcc -v  shows that
gcc version 7.5.0 (Ubuntu 7.5.0-3ubuntu1~18.04)
```

Please note that there have different optimization options in different versions of compilers. 

If you use the optimization options that are not included in this version of the compiler, the program can not run and report an error.

It is strongly recommended to confirm that the optimization options are in the official instructions of GCC or LLVM before using them.

e.g.
[GCC version 10.2.0](https://gcc.gnu.org/onlinedocs/gcc-10.2.0/gcc/Optimize-Options.html#Optimize-Options).

You can also use the command to display all options in terminal
```
gcc --help=optimizers


The following options control optimizations:
  -O<number>                  Set optimization level to <number>.
  -Ofast                      Optimize for speed disregarding exact standards
                              compliance.
  -Og                         Optimize for debugging experience rather than
                              speed or size.
  -Os                         Optimize for space rather than speed.
  -faggressive-loop-optimizations Aggressively optimize loops using language
                              constraints.
  -falign-functions           Align the start of functions.
  -falign-jumps               Align labels which are only reached by jumping.
  -falign-labels              Align all labels.
  -falign-loops               Align the start of loops.
  ...

```
LLVM

```
clang -v
```


Check how to install LLVM here 

https://apt.llvm.org/    

https://clang.llvm.org/get_started.html









[//]: <> (Checking Installation)


[//]: <> (Paper)



First-order formulas
--------------------

We manually generate first-order formulas after understanding the compiler manual. The knowledge we learned is easy to move between the same compiler series---we only need to consider the different optimization options introduced by the new version. 

We use Z3 Prover to analyze all generated optimization option sequences for conflicts and make changes to conflicting options for greater compiling success.

For more details, please refer  [Z3Prover](https://github.com/BinTuner/Dev/blob/main/BinTuner/main/search/Z3Prover.py).

Setting for Genetic Algorithm
--------------------
The genetic algorithm is a metaheuristic inspired by the process of natural selection that belongs to the larger class of evolutionary algorithms. Genetic algorithms are commonly used to generate high-quality solutions to optimization and search problems by relying on biologically inspired operators such as mutation, crossover, and selection.

We tune four parameters for the genetic algorithm, including `mutation_rate`,  `crossover_rate`, `must_mutate_count`, `crossover_strength`.  

For more details, please refer [globalGA](https://github.com/BinTuner/Dev/blob/main/BinTuner/main/search/globalGA-old.py).

Future Work
--------------------
We are studying constructing custom optimization sequences that present the best tradeoffs between multiple objective functions (e.g., execution speed & NCD). To further reduce the total iterations of BinTuner, an exciting direction is to develop machine learning methods that correlate C language features with particular optimization options. In this way, we can predict program-specific optimization strategies that achieve the expected binary code differences.





