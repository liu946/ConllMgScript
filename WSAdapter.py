#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Copyright (C) 2018 Liu Yang <mkliuyang@gmail.com> All rights reserved.
"""
    句法分词适配器
    usage:
        WSAdapter.py file.conll goldseg.conll outputfile.conll
"""
import sys
from functools import reduce
from collections import Counter
from structure.word import SentenceAsTree, SentenceAsList, PlainWord, WordWithRel
import codecs


class Rule(object):
    """

    """

    def __init__(self):
        pass

    def adapt(self, source_olist, tar_olist):
        """

        :param source_olist:
        :param tar_olist:
        :return: True if this rule function has already managed the fix and will not return true when next adapting.
        """
        return NotImplementedError(self.__class__.__name__ + ' not implement.')

    @staticmethod
    def find_head(word_list):
        """
        find which is the head word of the subtree
        :param word_list: a list of WordWithRel
        :return: index of head word or -1 if the list is not in a subtree.
        """
        parent_outside = [0 if w.parent in word_list else 1 for w in word_list]
        if sum(parent_outside) == 1:
            return parent_outside.index(1)
        else:
            return -1

    @staticmethod
    def suture_word_wise(word1, word2):
        if not word2 is None:
            word2.pre = word1
        if not word1 is None:
            word1.next = word2

    @staticmethod
    def suture_parent(parent, child_list):
        parent.children = child_list
        for c in child_list:
            c.parent = parent


class MergeRule(Rule):
    """
    AB C D => ABCD
    """

    def adapt(self, source_olist, tar_olist):
        if len(tar_olist) == 1 and not (self.find_head(source_olist) == -1):
            core = source_olist[self.find_head(source_olist)]
            new_word = WordWithRel.construct_with_args(0, tar_olist[0].word, core.parent, core.rel)
            self.suture_word_wise(source_olist[0].pre, new_word)
            self.suture_word_wise(new_word, source_olist[-1].next)
            self.suture_parent(new_word, reduce(lambda x, y: x + y, [w.children for w in source_olist]))
            return True
        return False


class SplitRule(Rule):
    """
    ABCD => AB C D
    """

    def adapt(self, source_olist, tar_olist):
        if len(source_olist) == 1 and not (self.find_head(tar_olist) == -1):
            core_index = self.find_head(tar_olist)
            new_words = [WordWithRel.construct_with_args(0, w.word, None, w.rel) for w in tar_olist]
            for i, w in enumerate(new_words):
                if not i == 0:
                    self.suture_word_wise(new_words[i - 1], w)
                if i == core_index:
                    w.parent = source_olist[0].parent
                    w.rel = source_olist[0].rel
                    self.suture_parent(w, source_olist[0].children)
                else:
                    w.parent = new_words[tar_olist.index(tar_olist[i].parent)]
            self.suture_word_wise(source_olist[0].pre, new_words[0])
            self.suture_word_wise(new_words[-1], source_olist[0].next)
            return True
        return False


class Adapter(object):
    def __init__(self, rules):
        self.rules = []
        [self.add_rule(rule) for rule in rules]
        self.counter = Counter()

    def add_rule(self, rule):
        if not isinstance(rule, Rule):
            raise ValueError('Input rule mast a instance of Rule.')
        self.rules.append(rule)

    def set_sentence(self, source, target_split):
        self.source = source
        self.target = target_split
        if not self.check_same():
            raise ValueError('Not Same sentence input. [' + self.source.plain() + '] and [' + self.target.plain() + ']')

    def check_same(self):
        return self.source.plain() == self.target.plain()

    def get_overlap(self, source_begin, tar_begin):
        if source_begin is None and tar_begin is None:
            # return None at the end of each sentence
            return None, None
        if not (isinstance(source_begin, PlainWord) and isinstance(tar_begin, PlainWord)):
            raise ValueError('Input begins mast a instance of PlainWord.')
        elif source_begin.word == tar_begin.word:
            return self.get_overlap(source_begin.next, tar_begin.next)
        else:
            # overlap
            source_list = [source_begin]
            tar_list = [tar_begin]
            while not ''.join([w.word for w in source_list]) == ''.join([w.word for w in tar_list]):
                s_str = ''.join([w.word for w in source_list])
                t_str = ''.join([w.word for w in tar_list])
                short_list = tar_list if len(s_str) > len(t_str) else source_list
                short_list.append(short_list[-1].next)
            return source_list, tar_list

    def adapt(self, source_begin=None, tar_begin=None, deep=0):
        if deep == 0:
            source_begin = self.source.root.next
            tar_begin = self.target.root.next
        source_list, tar_list = self.get_overlap(source_begin, tar_begin)
        if source_list is None and tar_list is None:
            if deep == 0:
                # 第一次找而且没找到任何错误
                self.counter.update(['no_overlap'])
            elif source_begin == self.source.root.next and tar_begin == self.target.root.next:
                # 从头开始找的，而且没有找到
                self.counter.update(['managed'])
            elif not source_begin == self.source.root.next:
                # 不是从头开始找的，而且没找到，意味着之前有没能处理的overlap
                self.counter.update(['unmanged'])
            return
        else:
            for i, r in enumerate(self.rules):
                if r.adapt(source_list, tar_list):
                    self.source.re_index()
                    self.counter.update([r.__class__.__name__])
                    return self.adapt(self.source.root.next, self.target.root.next, deep + 1)
            else:
                return self.adapt(source_list[-1].next, tar_list[-1].next, deep + 1)


def conll_sentence_iter(filename):
    with codecs.open(filename, encoding='utf8') as fi:
        lines = []
        for i in fi:
            i = i.strip()
            if (i == '' or i.startswith('#')) and len(lines):
                yield lines
                lines = []
            elif not (i == '' or i.startswith('#')):
                lines.append(i.split('\t'))
        if len(lines):
            yield lines


def ws_sentence_iter(filename):
    with codecs.open(filename, encoding='utf8') as fi:
        for i in fi:
            i = i.strip()
            if not i == '':
                yield i.split('\t')


if __name__ == '__main__':
    source = conll_sentence_iter(sys.argv[1])
    tar = conll_sentence_iter(sys.argv[2])
    adp = Adapter([MergeRule(), SplitRule()])
    try:
        with codecs.open(sys.argv[3], 'w', encoding='utf8') as fo:
            with codecs.open(sys.argv[3] + '.checkout', 'w', encoding='utf8') as fck:
                while True:
                    s, t = SentenceAsTree(next(source)), SentenceAsTree(next(tar))
                    fck.write(s.conll_str() + '\n')
                    adp.set_sentence(s, t)
                    adp.adapt()
                    # print(s.conll_str())
                    fo.write(s.conll_str() + '\n')
                    fck.write(s.conll_str() + '\n')
    except StopIteration:
        print(adp.counter)
        exit(0)
