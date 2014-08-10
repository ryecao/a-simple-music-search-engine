import pickle
from math import log10, sqrt
from query_process import query_parser
from query_process import words_filter, lower_letters
import re
import os
import codecs
import operator
import numpy as np
import jieba
import sys
from collections import Counter

module_dir = os.path.dirname(__file__)
file_path = os.path.join(module_dir, 'data/')

f_docidlist = open(file_path + 'docidlist.dat')
f_invertedinex = open(file_path + 'invertedindex.dat')
f_docn = open(file_path + 'docn.dat')
f_id_info_list = open(file_path + 'id_info_list.dat')
f_play_and_share = open(file_path + 'playandshare.dat')

t_inverted_index = pickle.load(f_invertedinex)
doc_N = pickle.load(f_docn)
doc_id_list = pickle.load(f_docidlist)
id_info_list = pickle.load(f_id_info_list)
play_and_share = pickle.load(f_play_and_share)

f_docidlist.close()
f_invertedinex.close()
f_docn.close()
f_id_info_list.close()
f_play_and_share.close()


def tdxidf_weighting(term, doc_id):
    if doc_id in t_inverted_index[term]:
        term_freq = t_inverted_index[term][doc_id]
        doc_freq = len(t_inverted_index[term])
        if term_freq is not 0 and doc_freq is not 0:
            return (1 + log10(term_freq)) * log10(doc_N / float(doc_freq))
    else:
        return 0


def calc_vector_space(query, id_list):
    vector_list = {}
    term_list = list(set(query))
    q_doc_cos_list = {}
    q_vector = []
    for ids in id_list:
        for term in term_list:
            if term in t_inverted_index:
                if ids in vector_list:
                    if ids in t_inverted_index[term]:
                        vector_list[ids].append(tdxidf_weighting(term, ids))
                    else:
                        vector_list[ids].append(0)
                else:
                    if ids in t_inverted_index[term]:
                        vector_list[ids] = [tdxidf_weighting(term, ids)]
                    else:
                        vector_list[ids] = [float(0)]
    for ids in vector_list:
        vector_list[ids] = np.nan_to_num(np.array(vector_list[ids]))

    for term in term_list:
        if term in t_inverted_index:
            q_vector.append((1 + log10(query.count(term))) *
                            log10(doc_N / float(len(t_inverted_index[term]))))

    q_vector = np.nan_to_num(np.array(q_vector))
    for ids in vector_list:
        q_doc_cos_list[ids] = np.dot(q_vector, vector_list[
                                     ids]) / (np.linalg.norm(q_vector, ord=2) * (np.linalg.norm(vector_list[ids], ord=2)))
        play_count = float(play_and_share[ids][0])
        share_count = float(play_and_share[ids][1])
        if play_count == 0:
            play_count = 1
        if share_count == 0:
            share_count = 1
        q_doc_cos_list[ids] = np.nan_to_num(
            q_doc_cos_list[ids]) * log10(sqrt(play_count)) * log10(share_count)
    rank = [(key, value) for key, value in q_doc_cos_list.iteritems()]
    rank = sorted(rank, key=operator.itemgetter(1))
    rank = rank[::-1]
    rank = [key for key, value in rank]

    return rank


def dosearch(query):
    weight = 0
    raw_query = lower_letters(query)
    query = query_parser(query)
    query = query + [raw_query]
    id_list = []
    res_name = []
    weight = {}
    if query:
        for term in query:
            if term in t_inverted_index:
                for key, value in t_inverted_index[term].iteritems():
                    if key not in weight:
                        weight[key] = tdxidf_weighting(term, key)
                    else:
                        weight[key] = weight[key] + tdxidf_weighting(term, key)
                    if key not in id_list:
                        id_list.append(key)

        rank_list = calc_vector_space(query, id_list)
        rank_fin = []
        q = list(set(jieba.cut_for_search(raw_query)))
        if u" " in q:
            q.remove(u" ")
        cnt = []
        for key_index, key in reversed(list(enumerate(rank_list))):
            info_term = list(set(jieba.cut_for_search(id_info_list[key])))
            if u" " in info_term:
                info_term.remove(u" ")
            for term in q:
                if term in info_term:
                    cnt.append(key)

        freq_cnt = Counter(cnt)
        freq_cnt_tuples = freq_cnt.most_common()
        for item, cnt in freq_cnt_tuples:
            rank_fin.append(item)

        for item in rank_list:
            if item not in rank_fin:
                rank_fin.append(item)
        if id_list:
            for ids in rank_fin:
                res = os.path.splitext(doc_id_list[ids])[0]
                res = res[7:]
                res_name.append(res)
        return res_name
