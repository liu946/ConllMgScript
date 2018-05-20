#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Copyright (C) 2018 Liu Yang <mkliuyang@gmail.com> All rights reserved.

import os
import sys
import codecs
import math
import random
from contextlib import ExitStack

doc = '''
usage:
    ./random_split.py <filename> part_max_num1, part_max_num2, ...
    
'''

def rand_index(l):
    '''

    :param l: [2, 4, 4, 10]
    :return: 10% 0 20% 1 20% 2 50% 3
    '''
    max = math.fsum(l)
    sum_c = 0
    sample = random.randint(0, max - 1)
    for i in range(len(l)):
        sum_c += l[i]
        if sample < sum_c:
            return i


def split(file, *split_max):
    split_max = list(split_max)
    suffix = '' if file.rfind('.',) == -1 else file[file.rfind('.'):]
    prefix = file if file.rfind('.') == -1 else file[:file.rfind('.')]
    outfiles = [prefix + '.split' + str(n) + suffix for n in range(len(split_max))]
    with codecs.open(file, encoding='utf8') as fi:
        with ExitStack() as stack:
            fos = [stack.enter_context(codecs.open(f, 'w', encoding='utf8')) for f in outfiles]
            stn = ''
            for line in fi:
                stn += line
                if line == '\n':
                    if any(split_max):
                        index = rand_index(split_max)
                        fo = fos[index]
                        fo.write(stn)
                        stn = ''
                        split_max[index] -= 1
                    else:
                        return

if __name__ == '__main__':
    if sys.argv[1].startswith('-'):
        print(doc)
        exit(0)
    split(sys.argv[1], *[int(i) for i in sys.argv[2:]])