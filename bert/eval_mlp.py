#!/usr/bin/env python3

import sys

# Filename of model to load
filename = sys.argv[1] if len(sys.argv) == 2 else 'mlp.mbert.model'

# Evaluation data
embeddings = list()
tags = list()
test = open('cs_pud.mbert', 'r', encoding='utf-8')
lines = test.readlines()
for line in lines:
    if line != '\n':
        fields = line.split()
        tags.append(fields[0])
        embeddings.append([float(x) for x in fields[1:]])

from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
# Load the model
import pickle
classifier = pickle.load(open(filename, 'rb'))

# Evaluate the classifier
score = classifier.score(embeddings, tags)
print(score)
