#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Copyright (C) 2018 Liu Yang <mkliuyang@gmail.com> All rights reserved.

import sys
import codecs
from WSAdapter import conll_sentence_iter, ws_sentence_iter, SentenceAsTree, SentenceAsList

doc = """
    usage:
        ./mergepos.py <conll_file> <pos_file> <output_conll_file>
        
        conll_file:
        pos_file:
        output_conll_file:
"""

def merge_pos(source, tar):
    s = source.iter_item()
    t = tar.iter_item()
    next(s)
    try:
        while True:
            sw, tw = next(s), next(t)
            if not sw.word == tw.word[:tw.word.rfind('_')]:
                raise ValueError()
            sw.line[3] = tw.word[tw.word.rfind('_') + 1:]
            sw.line[4] = '_'
    except StopIteration:
        return

if __name__ == '__main__':
    source = conll_sentence_iter(sys.argv[1])
    tar = ws_sentence_iter(sys.argv[2])
    try:
        with codecs.open(sys.argv[3], 'w', encoding='utf8') as fo:
            while True:
                s1, t1 = next(source), next(tar)
                try:
                    s, t = SentenceAsTree(s1), SentenceAsList(t1)
                except:
                    print(s1, t1)
                merge_pos(s, t)
                # print(s.conll_str())
                fo.write(s.conll_str() + '\n')
    except StopIteration:
        exit(0)
