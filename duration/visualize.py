#!/usr/bin/pythoni
# -*- coding: utf-8 -*-
import os, datetime, gzip, cjson, json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import epoch2num, date2num
import dateutil.parser
import fnmatch
import numpy as np
import operator
import string
import math
simplejson = json
import ast
import random

def histDuration(filename):
    infile = file(filename);
    user_dura = json.load(infile);
    infile.close();

    list = [];
    for user, dura in user_dura.iteritems():
        list.append(dura);

