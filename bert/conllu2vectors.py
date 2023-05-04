#!/usr/bin/env python3
#coding: utf-8

import sys

import logging
logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

ID = 0
FORM = 1
LEMMA = 2
UPOS = 3
XPOS = 4
FEATS = 5
HEAD = 6
DEPREL = 7

from transformers import BertModel, BertTokenizer, DistilBertModel, DistilBertTokenizer
import torch

model = sys.argv[1] if len(sys.argv) == 2 else 'bert-base-multilingual-uncased'
# Some valid options:
# bert-base-uncased
# bert-base-cased
# bert-large-cased
# bert-base-multilingual-uncased
# bert-base-multilingual-cased

tokenizer = BertTokenizer.from_pretrained(model)
model = BertModel.from_pretrained(model)

# Trying to join wordpieces to tokens so that they match the original UD
# tokens and map the UPOS labels to them.
# TODO This method is very stupid an should be improved.
def combine(ids, output):
    result = []
    tokens = tokenizer.convert_ids_to_tokens(ids)
    # initialize with first token
    current = output[1].tolist()  # contextual embedding
    token = [tokens[1]]  # token
    # skip [CLS] and [SEP]; and first token is already added
    for i in range(2, len(output)-1):
        if tokens[i].startswith('##'):
            # continuation token
            # add up the contextual embeddings
            current = [c+o for c, o in zip(current, output[i].tolist()) ]
            # add the token without the continuatoin mark
            token.append(tokens[i][2:])
        else:
            # new token
            # concatenate the token parts, average the contextual embeddings
            result.append(( ''.join(token),
                [x/len(token) for x in current] ))
            # start new
            current = output[i].tolist()
            token = [tokens[i]]
    # end
    result.append(( ''.join(token),
        [x/len(token) for x in current] ))
    return result

tokens = []
tags = []
#for line in sys.stdin:
test = open('cs_pud-ud-test.conllu', 'r', encoding='utf-8')
out = open('cs_pud.mbert', 'w', encoding='utf-8')
lines = test.readlines()
for line in lines:
    if line == '\n':
        # end of sentence
        ids = tokenizer.encode(' '.join(tokens))
        t = torch.tensor([ids])
        output = model(t)[0][0]
        embeddings = combine(ids, output)
        if len(embeddings) == len(tokens):
            # TODO should check that these are the same tokens
            for tag, emb in zip (tags, embeddings):
                # emb[0] is the token
                # emb[1] is a list of floats constituting the contextual embedding
                #print(emb[0], tag, *emb[1], sep='\t')
                out.write(tag)
                for num in emb[1]:
                    out.write('\t')
                    out.write(str(num))
                #print(tag, *emb[1], sep='\t')
                out.write('\n')
            #print()
        else:
            # TODO should try harder to match the tokens
            logging.warn(
                'Different tokenization of sentence): {}'.format(
                ' '.join(tokens)))
            logging.warn(
                'UD number of tokens: {}'.format(len(tokens)))
            logging.warn(
                'BERT number of tokens: {}'.format(len(embeddings)))
        tokens = []
        tags = []
    elif line.startswith('#'):
        pass
    else:
        fields = line.split('\t')
        if fields[ID].isdigit():
            # standard token
            tokens.append(fields[FORM])
            tags.append(fields[UPOS])
        # else pass

