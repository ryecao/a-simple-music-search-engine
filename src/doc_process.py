# encoding=utf-8
import jieba
import string
import codecs
import re
import os
import glob
import pickle
import json
from get_domi_color import get_domi_color
from query_process import lower_letters, words_filter
from pypinyin import pinyin, lazy_pinyin
import pypinyin
from collections import Counter


def build_dict_for_spell_check(t_inverted_index):
    sumsum = 0
    data = {}
    for term in t_inverted_index:
        if (type(term) is not str):
            term = term.decode("utf-8")
        for docID in t_inverted_index[term]:
            sumsum += t_inverted_index[term][docID]
        term = lower_letters(term)
        if (type(term) is not str):
            print type(term)
            term = term.decode("utf-8")
            print "fuck"
            print term
            print type(term)
        data[term] = sumsum
        sumsum = 0
    f = open('./data/spell.dat', 'wb')
    pickle.dump(data, f)
    f.close()


def is_eng_word(word):
    val = True
    include = set(string.letters + string.digits + string.punctuation + u" ")
    for ch in word:
        if ch not in include:
            val = False
            break
    return val


def add_pinyin_to_dict(term):
    if is_eng_word(term) is False:
        exclude = set(
            string.letters + string.digits + string.punctuation + u" ")
        term_origin = term
        term = ''.join(ch for ch in term if ch not in exclude)
        lp = lazy_pinyin(term)
        strlp = ''.join(lp)
        py_inits = pinyin(term, style=pypinyin.INITIALS)
        strlp_inits = ''.join(i[0] for i in py_inits)
        if strlp_inits not in t_inverted_index:
            t_inverted_index[strlp_inits] = t_inverted_index[term_origin]
        else:
            a = Counter(t_inverted_index[strlp_inits])
            b = Counter(t_inverted_index[term_origin])
            t_inverted_index[strlp_inits] = a + b
        if strlp not in t_inverted_index:
            t_inverted_index[strlp] = t_inverted_index[term_origin]
        else:
            a = Counter(t_inverted_index[strlp])
            b = Counter(t_inverted_index[term_origin])
            t_inverted_index[strlp] = a + b

t_dict = {}
t_inverted_index = {}
doc_id_list = {}
doc_id = 0
id_info_list = {}
play_and_share = {}
color = {}
auto_complete_list = []
for file_name in glob.glob(ur'./data/*.json'):
    f = codecs.open(file_name, 'r', 'utf-8')
    j = json.load(f)
    content = j["title"] + j["singer"] + j["album"] + j["lrc"]
    for tag in j["tag"]:
        content = content + tag
    color[j["title"]] = get_domi_color(j["title"])
    play_and_share[doc_id] = [j["play_count_num"], j["share"]]
    doc_id_list[doc_id] = file_name.encode("utf-8")
    seg_list = list(jieba.cut_for_search(content))
    seg_list = words_filter(seg_list)
    seg_list.append(lower_letters(j["title"]))
    seg_list.append(lower_letters(j["singer"]))
    seg_list.append(lower_letters(j["album"]))
    for tag in j["tag"]:
        seg_list.append(tag)
    auto_complete_list.append(j["title"])
    auto_complete_list.append(j["singer"])
    auto_complete_list.append(j["album"])
    term = list(set(seg_list))
    exclude = set(string.punctuation)
    info_str = j["title"] + " " + j["singer"] + " " + j["album"]
    info_str = lower_letters(info_str)
    info = ''.join(ch for ch in info_str if ch not in exclude)
    id_info_list[doc_id] = info
    if u" " in term:
        term.remove(u" ")
    for t in term:
        if t not in t_inverted_index:
            t_inverted_index[t] = {doc_id: seg_list.count(t)}
        else:
            t_inverted_index[t].update({doc_id: seg_list.count(t)})

    add_pinyin_to_dict(lower_letters(j["title"]))
    add_pinyin_to_dict(lower_letters(j["singer"]))
    add_pinyin_to_dict(lower_letters(j["album"]))

    f.close()
    doc_id = doc_id + 1
doc_N = doc_id

build_dict_for_spell_check(t_inverted_index)
auto_complete_list = list(set(auto_complete_list))

f = open('./data/docidlist.dat', 'wb')
pickle.dump(doc_id_list, f)
f.close()

f = open('./data/playandshare.dat', 'wb')
pickle.dump(play_and_share, f)
f.close()

f = open('./data/invertedindex.dat', 'wb')
pickle.dump(t_inverted_index, f)
f.close()

f = open('./data/docn.dat', 'wb')
pickle.dump(doc_N, f)
f.close()

f = open('./data/idinfolist.dat', 'wb')
pickle.dump(id_info_list, f)
f.close()

f = open('./data/color.dat', 'wb')
pickle.dump(color, f)
f.close()

f = open('./data/autocomplete.dat', 'wb')
pickle.dump(auto_complete_list, f)
f.close()
