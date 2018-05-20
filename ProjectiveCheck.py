#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Copyright (C) 2018 Liu Yang <mkliuyang@gmail.com> All rights reserved.

import os
import sys
import codecs
from structure.word import Word, Sentence

def convert(in_file, out_file):
    with codecs.open(in_file, encoding='utf8') as fi:
        with codecs.open(out_file, 'w', encoding='utf8') as fo:
            lines = []
            for i in fi:
                i = i.strip()
                if (i == '' or i.startswith('#')) and len(lines):
                    try:
                        stn = Sentence()
                        stn.init(lines)
                        if not (stn.check_tree() and stn.check_projective()):
                            fo.write('*****\n')
                            fo.write('\n'.join(['\t'.join(i) for i in lines]) + '\n')
                    except:
                        fo.write('*****\n')
                        fo.write('\n'.join(['\t'.join(i) for i in lines]) + '\n')
                    lines = []
                elif not (i == '' or i.startswith('#')):
                    lines.append(i.split('\t'))

if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2])