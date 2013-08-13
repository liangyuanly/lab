#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
from matplotlib.patches import Polygon 
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import math
import json
from scipy import stats
from numpy import array
import numpy

def precRecall(filename):
    infile = file(filename)
    lines = infile.readlines()

    for i in range(0, len(lines), 2):
        pre_line = lines[i]
        rec_line = lines[i+1]
        x_list = json.loads(rec_line)
        y_list = json.loads(pre_line)
        
        plt.plot(y_list, label = str(i));
    
    plt.xlabel('Time Unit (10 Minutes)')
    plt.ylabel('Count')
    plt.legend();
    plt.show();

precRecall('data/iteration_purity')
 
