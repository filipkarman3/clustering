# -*- coding: utf-8 -*-
"""
Created on Tue May  6 09:23:29 2025

@author: jemi6917
"""

# -*- coding: utf-8 -*-
"""
Created on Thu May  1 22:24:02 2025

@author: jmd01
"""

#from RawInput import RawInput, RawInputLazy, ProbabilisticGrammar
from Learner import LearnerConfig
from Population import Population
from grammars import create_stimuliNVN, create_stimuliRCP,create_stimuliMD
import matplotlib.pyplot as plt

from datetime import datetime


if __name__ == '__main__':
    
    print('Learner initialization')
    # Configure and initialize learner
    n_trial =5000
    alpha = 0.06
    alpha_v = 1.
    beta = 1.5
    chaining = True
    RW = True
    configChaining = LearnerConfig(n_trials=n_trial,
                           border = 'cont',
                           initial_value_chunking=-1.,
                           initial_value_border=1.,
                           alpha= alpha,
                           alpha_v=alpha_v,
                           beta= beta,
                           positive_reinforcement = 25,
                           negative_reinforcement = -10,
                           RW=RW,
                           chaining = chaining)
    
    configNoChaining = LearnerConfig(n_trials=n_trial,
                           border = 'cont',
                           initial_value_chunking=-1.,
                           initial_value_border=1.,
                           alpha= alpha,
                           alpha_v=alpha_v,
                           beta= beta,
                           positive_reinforcement = 25,
                           negative_reinforcement = -10,
                           RW=RW,
                           chaining = False)
    

    
    print('Testing on population')
    labels = ['Chaining','NoChaining']
    config = [configChaining,configNoChaining]
    # Shared input
    start = datetime.now()
    curves = []

    
    for conf,label in zip(config,labels):
        print('Running '+label)
        pop = Population(n_learners=10, config=conf, stimuli_factory=create_stimuliMD)
        
        pop.train_all(use_multiprocessing=False)
        curves.append(pop.plot_average_learning_curve(window=10,show=False))
         
    end  = datetime.now()
    
    for curve, label in zip(curves,labels):
        plt.plot(curve, label = label)
    
    plt.title("Learning Curves Comparison")
    plt.xlabel("Trial")
    plt.ylabel("Moving Average Success")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    print('Duration: {}'.format(end - start))