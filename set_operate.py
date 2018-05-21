#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Copyright (C) 2018 Liu Yang <mkliuyang@gmail.com> All rights reserved.

import argparse
import codecs
from collections import Counter

from structure.word import SentenceAsTree
from structure.data_iter import *


class SubCommand(object):
    def __init__(self, sub_parser):
        pass

    @staticmethod
    def process(argv):
        raise NotImplementedError()

    @classmethod
    def get_help(cls):
        return cls.__name__ + ' help'


class Filter(SubCommand):
    @classmethod
    def get_help(cls):
        return '''Only output the sentences of input_file that contains in the filter_file.'''

    def __init__(self, sub_parser):
        super().__init__(sub_parser)
        sub_parser.add_argument('input_file', help='conll file to be filtered.')
        sub_parser.add_argument('filter_file', help='only in this file will be output.')
        sub_parser.add_argument('output_file', help='output path.')
        sub_parser.add_argument('--remain_file', default=None, help='output source sentence not in filter file.')
        sub_parser.add_argument('--not_fit_filters', default=None, help='output filter sentence not in source file.')

    @staticmethod
    def process(argv):
        source_string = {}
        counter = Counter()
        not_fit_filters = []
        for stn in conll_sentence_iter(argv.input_file):
            sentence = SentenceAsTree(stn)
            source_string[sentence.plain_hash()] = sentence
            counter.update(['source_sentence'])
        with codecs.open(argv.output_file, 'w', encoding='utf8') as fo:
            for filter_stn in conll_sentence_iter(argv.filter_file):
                sentence = SentenceAsTree(filter_stn)
                key = sentence.plain_hash()
                counter.update(['filter_sentence'])
                if key in source_string:
                    fo.write(source_string[key].conll_str() + '\n')
                    del source_string[key]
                    counter.update(['in_filter_sentence'])
                else:
                    not_fit_filters.append(sentence)
                    counter.update(['not_in_filter_sentence'])
        if argv.remain_file is not None:
            with codecs.open(argv.remain_file, 'w', encoding='utf8') as fremain:
                for stn in source_string.values():
                    fremain.write(stn.conll_str() + '\n')
        if argv.not_fit_filters is not None:
            with codecs.open(argv.not_fit_filters, 'w', encoding='utf8') as ffilters:
                for stn in not_fit_filters:
                    ffilters.write(stn.conll_str() + '\n')
        print(counter)


if __name__ == '__main__':
    enabled_command_classes = [Filter]
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='''The operator of the method to run on the corpus.''')
    for C in enabled_command_classes:
        process_name = C.__name__.lower()
        subparser = subparsers.add_parser(process_name, help=C.get_help())
        subparser.set_defaults(process_obj=C(subparser))
    args = parser.parse_args()
    process_obj = args.process_obj
    del args.process_obj
    process_obj.process(args)
