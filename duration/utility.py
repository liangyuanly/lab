#!/usr/bin/python

import cPickle as p;
import sys
import string


def hour(a):
    # a:"%Y-%m-%d %H:%M:%S";
    s1 = a.split(' ');
    s2 = s1[1].split(':')
    hour = string.atoi(s2[0]) + 1;
    return hour;

def date(a):
    # a:"%Y-%m-%d %H:%M:%S";
    s1 = a.split(' ');
    s2 = s1[0].split('-')
    date = s2[0]+s2[1]+s2[2];
    return string.atoi(date);


