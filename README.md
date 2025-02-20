[![Python 3.10.1](https://img.shields.io/badge/Python-3.10.1-blue)](https://www.python.org/downloads/release/python-3101/)

# SF-FSA-VI

Code base for the paper [Planning with a Learned Policy Basis to Optimally Solve Complex Tasks](https://arxiv.org/abs/2403.15301) publisheed at ICAPS 2024.

**Authors:** 

- **Guillermo Infante [^*], Anders Jonsson and Vicenç Gómez** (AI&ML research group, Universitat Pompeu Fabra)
- **David Kuric [^*] and Herke van Hoof** (AMLab University of Amsterdam)


## *Abstract*

> Conventional reinforcement learning (RL) methods can successfully solve a wide range of sequential decision problems. However, learning policies that can generalize predictably across multiple tasks in a setting with non-Markovian reward specifications is a challenging problem. We propose to use successor features to learn a policy basis so that each (sub)policy in it solves a well-defined subproblem. In a task described by a finite state automaton (FSA) that involves the same set of subproblems, the combination of these (sub)policies can then be used to generate an optimal solution without additional learning.  In contrast to other methods that combine (sub)policies via planning, our method asymptotically attains global optimality, even in stochastic environments.


### Citing us
If you cite our paper in your research please use the following BibTeX entry:
```BibTeX
@article{Kuric_Infante_2024,
title={Planning with a Learned Policy Basis to Optimally Solve Complex Tasks},
journal={Proceedings of the International Conference on Automated Planning and Scheduling},
author={Kuric, David and Infante, Guillermo and Gómez, Vicenç and Jonsson, Anders and van Hoof, Herke},
year={2024},
month={May},
volume={34},
number={1}, 
pages={333-341},
url={https://ojs.aaai.org/index.php/ICAPS/article/view/31492},
DOI={10.1609/icaps.v34i1.31492},
}
```



[^*]: Contributed equally.
