#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
# Manage word segment error by using faked POS tags.

使用假的 POS-tag 修改分词错误问题的自动脚本。

# 输入
```
./mg_ws_err.py <input_filename> <output_filename>
```
文件格式Conll如下：
13	谢	_	MR	nh	_	28	SBV	_	_


# 功能性词性类型

需要在标注时注意如下标注方法，将此类词性标注在第4字段(index=3)。
句法应该按照处理后的词进行标注，标注MR，ML时不要在被MERGE的词上标子节点。
增加的词性类型如下，基本可以涵盖大量错误：

- MR：将右边的词结合到此词中。
- ML：将左边的词结合到此词中。
- M1R：将右边的词的第1个字结合到此词中。
- M1L：将左边的词的最后1个字结合到此词中。
- M2R：将右边的词的第2个字结合到此词中。
- M2L：将左边的词的最后2个字结合到此词中。

# 举例

- 1
```
error:  谢   超杰  家   底薄  。
correct:谢超杰 家底  薄  。
```

则应该如下标注：
```
谢   超杰  家   底薄  。
MR   _    M1R  _    _
```
'''

import os
import sys
import codecs

SPLIT_CHAR = '\t'
FUNC_LIST = ['MR', 'ML', 'M1R', 'M1L', 'M2R', 'M2L']

class Word(object):
    __idx_index = 0
    __word_index = 1
    __func_index = 3
    __parent_index = 6

    def __init__(self, line):
        self.line = line
        self.index = int(line[self.__idx_index]) if self.__idx_index < len(line) else None
        self.word = line[self.__word_index] if self.__word_index < len(line) else None
        self.parent = int(line[self.__parent_index]) if self.__parent_index < len(line) else None
        self.func = line[self.__func_index] if self.__func_index < len(line) else None
        self.next = None
        self.pre = None
        self.children = []

    def MR(self):
        assert not self.next is None
        assert len(self.next.children) == 0
        self.func = '_'
        self.word += self.next.word
        if self.next in self.children:
            self.children.remove(self.next)
        self.next = self.next.next

    def ML(self):
        assert not self.pre is None
        assert len(self.pre.children) == 0
        self.func = '_'
        self.word = self.pre.word + self.word
        if self.pre in self.children:
            self.children.remove(self.pre)
        self.pre = self.pre.pre

    def MxR(self, x):
        assert not self.next is None
        assert len(self.next.word) > x
        self.func = '_'
        self.word += self.next.word[:x]
        self.next.word = self.next.word[x:]

    def MxL(self, x):
        assert not self.pre is None
        assert len(self.pre.word) > x
        self.func = '_'
        self.word = self.pre.word[-x:] + self.word
        self.pre.word = self.pre.word[:-x]

    def M1R(self):
        self.MxR(1)

    def M2R(self):
        self.MxR(2)

    def M1L(self):
        self.MxL(1)

    def M2L(self):
        self.MxL(2)

    def __str__(self):
        if self.parent is None: # skip root
            return ''
        self.line[self.__idx_index] = str(self.index)
        self.line[self.__word_index] = self.word
        self.line[self.__parent_index] = str(self.parent.index)
        self.line[self.__func_index] = '_'
        return SPLIT_CHAR.join(self.line) + '\n'

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

    def manage(self):
        cur = self.root
        while cur is not None:
            if cur.func in FUNC_LIST:
                cur.__getattribute__(cur.func)()
                self.re_index()
                return self.manage()
            cur = cur.next
        return None

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

    def __str__(self):
        return ''.join([str(i) for i in self.iter_item()])


def convert(in_file, out_file):
    with codecs.open(in_file, encoding='utf8') as fi:
        with codecs.open(out_file, 'w', encoding='utf8') as fo:
            lines = []
            for i in fi:
                i = i.strip()
                if i == '' and len(lines):
                    stn = Sentence()
                    stn.init(lines)
                    stn.manage()
                    fo.write(str(stn) + '\n')
                    lines = []
                else:
                    lines.append(i.split('\t'))

if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2])


