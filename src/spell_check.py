# encoding: utf-8
import re
import collections
from Levenshtein import distance
import time
import pickle
import os
import codecs
import sys
import string

module_dir = os.path.dirname(__file__)
file_path = os.path.join(module_dir, 'data/')

f = open(file_path + 'spell.dat')
data = pickle.load(f)
f.close()


def is_eng_word(word):
    val = True
    include = set(string.letters + string.digits + string.punctuation + u" ")
    for ch in word:
        if ch not in include:
            val = False
            break
    return val


def edit1(word):
    if is_eng_word(word):
        dis = 2
    else:
        dis = 1
    return set(term for term in data if (distance(term, word) <= dis))


def known_edit2(word):
    return set(e2 for e1 in edit1(word) for e2 in edit1(e1) if e2 in data)


def known(words):
    return set(w for w in words if w in data)


def correctch(word):
    candidates = known([word]) or known(
        edit1(word)) or known_edit2(word) or [word]
    return max(candidates, key=data.get)
