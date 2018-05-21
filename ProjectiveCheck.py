#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Copyright (C) 2018 Liu Yang <mkliuyang@gmail.com> All rights reserved.

import os
import sys
import codecs

SPLIT_CHAR = '\t'

class Word(object):
    __idx_index = 0
    __word_index = 1
    __parent_index = 6
    def __init__(self, line):
        self.line = line
        self.index = int(line[self.__idx_index]) if self.__idx_index < len(line) else None
        self.word = line[self.__word_index] if self.__word_index < len(line) else None
        self.parent = int(line[self.__parent_index]) if self.__parent_index < len(line) else None
        self.next = None
        self.pre = None
        self.children = []
        self.left_children = []
        self.right_children = []

    def __str__(self):
        if self.parent is None: # skip root
            return ''
        self.line[self.__idx_index] = str(self.index)
        self.line[self.__word_index] = self.word
        self.line[self.__parent_index] = str(self.parent.index)
        return SPLIT_CHAR.join(self.line) + '\n'

    def reach_and_reach_children(self, reach, maxdeep, depth=0):
        reach[self.index] = True
        if depth > maxdeep:
            raise RuntimeError('circle in tree.')
        for word in self.children:
            word.reach_and_reach_children(reach, maxdeep, depth + 1)

    def check_projective(self):
        if self.parent.index < self.index:
            min = self.parent.index
            max = self.index
            next = 'pre'
        else:
            min = self.index
            max = self.parent.index
            next = 'next'
        cur = self.__getattribute__(next)
        while not (cur.index == self.parent.index):
            if cur.parent.index < min or cur.parent.index > max:
                return False
            cur = cur.__getattribute__(next)
        return True

class Sentence(object):

    def __init__(self):
        self.root = Word(['0', '<ROOT>'])

    def init(self, stn):
        words = [self.root]
        for i in stn:
            words.append(Word(i))
        # manage parents
        for i in words:
            i.parent = words[i.parent] if i.parent is not None else None
        # manage pre next children
        for i in words:
            i.next = words[i.index + 1] if i.index + 1 < len(words) else None
            i.pre = words[i.index - 1] if i.index - 1 >= 0 else None
            if not i.parent is None:
                i.parent.children.append(i)

    def re_index(self):
        i = 0
        for w in self.iter_item():
            w.index = i
            i += 1

    def iter_item(self):
        cur = self.root
        while cur is not None:
            yield cur
            cur = cur.next

    def check_tree(self):
        l = len(self)
        reach = [False] * l
        self.root.reach_and_reach_children(reach, l)
        return all(reach)

    def check_projective(self):
        for w in self.iter_item():
            if w.word == '<ROOT>':
                continue
            if not w.check_projective():
                return False
        return True

    def __len__(self):
        return len([1 for i in self.iter_item()])

    def __str__(self):
        return ''.join([str(i) for i in self.iter_item()])

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