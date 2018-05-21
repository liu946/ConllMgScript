#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Copyright (C) 2018 Liu Yang <mkliuyang@gmail.com> All rights reserved.
import codecs


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
