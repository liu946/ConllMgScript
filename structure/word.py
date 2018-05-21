#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Copyright (C) 2018 Liu Yang <mkliuyang@gmail.com> All rights reserved.
import math
import copy

SPLIT_CHAR = '\t'


class PlainWord(object):
    def __init__(self, word):
        self.word = word
        self.next = None
        self.pre = None

    def __len__(self):
        return len(self.word)

    def __str__(self):
        return self.word


class WordWithPos(PlainWord):

    def __init__(self, word, pos):
        super().__init__(word)
        self.pos = pos


class WordWithRel(PlainWord):
    __idx_index = 0
    __word_index = 1
    __parent_index = 6
    __rel_index = 7

    @classmethod
    def construct_with_line(cls, line):
        return WordWithRel(line)

    @classmethod
    def construct_with_args(cls, index, word, parent, rel):
        return WordWithRel(index, word, parent, rel)

    def __init__(self, *args):
        if len(args) == 1:
            self.__init_with_line(*args)
        elif len(args) == 4:
            self.__init_with_args(*args)
        else:
            raise ValueError("Error input.")

    def __init_with_line(self, line):
        if line[self.__word_index] == '<ROOT>':
            self.__init_with_args(0, '<ROOT>', None, None)
            return
        length_check = max([self.__idx_index, self.__word_index, self.__parent_index, self.__rel_index])
        if len(line) <= length_check:
            raise ValueError('Input line mast longer than %d' % length_check)
        self.__init_with_args(
            int(line[self.__idx_index]),
            line[self.__word_index],
            int(line[self.__parent_index]),
            line[self.__rel_index])
        self.line = copy.deepcopy(line)

    def __init_with_args(self, index, word, parent, rel):
        super().__init__(word)
        self.line = None
        self.index = index
        self.parent = parent
        self.rel = rel
        self.children = []

    def __str__(self):
        if self.parent is None: # skip root
            return ''
        return '%d %s %d %s\n' % (self.index, self.word, self.parent.index, self.rel)

    def conll_str(self):
        if self.line is None:
            self.line = ['_'] * 10
        if self.parent is None: # skip root
            return ''
        self.line[self.__idx_index] = str(self.index)
        self.line[self.__word_index] = self.word
        self.line[self.__parent_index] = str(self.parent.index)
        self.line[self.__rel_index] = self.rel
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

    def iter_item(self):
        raise NotImplementedError()

    def plain(self):
        return ''.join([str(w) for w in self.iter_item()])

    def plain_hash(self):
        return hash(self.plain())


class SentenceAsTree(Sentence):

    def __init__(self, stn):
        self.root = WordWithRel(['0', '<ROOT>'])
        words = [self.root]
        for i in stn:
            words.append(WordWithRel(i))
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

    def plain(self):
        return ''.join([w.word for w in self.iter_item() if not w.word == '<ROOT>'])

    def __len__(self):
        return len([1 for i in self.iter_item()])

    def __str__(self):
        return ''.join([str(i) for i in self.iter_item()])

    def conll_str(self):
        return ''.join([i.conll_str() for i in self.iter_item()])


class SentenceAsList(Sentence):
    def __init__(self, stn):
        self.stn = [PlainWord(w) for w in stn]
        for i, w in enumerate(self.stn):
            w.next = self.stn[i + 1] if i + 1 < len(self.stn) else None
            w.pre = self.stn[i - 1] if i - 1 >= 0 else None
        self.first = self.stn[0]

    def iter_item(self):
        cur = self.first
        while cur is not None:
            yield cur
            cur = cur.next

    def __str__(self):
        return ' '.join([str(w) for w in self.iter_item()])

    def __len__(self):
        return len([1 for i in self.iter_item()])
