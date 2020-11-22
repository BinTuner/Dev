BinTuner
---------------------
BinTuner is a cost-efficient auto-tuning framework, which can deliver a near-optimal binary code that reveals much more differences than -Ox settings. it also can assist the binary code analysis research in generating more diversified datasets for training and testing.

Since the experiment lasted several months, including extensive testing with multiple compilers, we got more than a hundred thousand binary intermediate files, we could imagine that how big the files would be, so we are trying to find other ways to upload and share the intermediate files and experimental results.

The architecture of BinTuner:
---------------------
![image](https://github.com/BinTuner/Dev/blob/master/Results/Images/BinTuner.png)


The core on the server-side is a metaheuristic search engine (e.g., the genetic algorithm), which directs iterative compilation towards maximizing the effect of binary code differences. 

The client-side runs different compilers (GCC, LLVM ...) and the calculation of the fitness function. 

Both sides communicate valid optimization options, fitness function scores, and compiled binaries to each other, and these data are stored in a database for future exploration. When BinTuner reaches a termination condition, we select the iterations showing the highest fitness function score and output the corresponding binary code as the final outcomes.



System Prerequisites
--------------------

Operating System: Ubuntu 20.04 LTS,

Compilers: GCC 10.2, LLVM 11.0,

Z3 Theorem Prover,

Some Third-party Libraries and Others:

1. IDA Pro 
2. Diaphora (a diffing plugin for IDA)
3. BinExport (an exporter component of BinDiff as well as BinNavi)
4. Python 2.7
5. argparse >= 1.2.1
6. fn >= 0.2.12
7. numpy >= 1.8.0
8. pysqlite >= 2.6.3
9. SQLAlchemy >= 0.8.2
10. BinHunt
11. Scan-build/intercept-build

https://pypi.org/project/scan-build/

https://clang.llvm.org/docs/JSONCompilationDatabase.html

Benchmarks and Malicious Samples:

(SPECint 2006 and SPECspeed 2017, Coreutils, and OpenSSL) benchmarks

Mirai, LightAidra, BASHLIFE

Future Work
--------------------
We are studying constructing custom optimization sequences that present the best tradeoffs between multiple objective functions (e.g., execution speed & NCD). To further reduce the total iterations of BinTuner, an exciting direction is to develop machine learning methods that correlate C language features with particular optimization options. In this way, we can predict program-specific optimization strategies that achieve the expected binary code differences.





