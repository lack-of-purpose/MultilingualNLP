#!/usr/bin/env python3
#coding: utf-8

import sys
from collections import defaultdict, Counter

conllu, para = sys.argv[1:]

lexicon = defaultdict(Counter)
with open(para, encoding="utf8") as translations:
    for line in translations:
        linesplit = line.split()
        if len(linesplit) == 2:
            lexicon[linesplit[0]][linesplit[1]] += 1

with open(conllu, encoding="utf8") as treebank, open('output.conllu', 'w', encoding="utf8") as out:
    for line in treebank:
        line = line.strip()
        fields = line.split('\t')
        if fields[0].isdigit():
            word = fields[1]
            translation = word
            if word in lexicon:
                translation = lexicon[word].most_common(1)[0][0]
            fields[1] = translation
            out.write('\t'.join(fields))
            out.write('\n')
            #print(*fields, sep='\t')
        else:
            out.write(line)
            out.write('\n')
            #print(line)