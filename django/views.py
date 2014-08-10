from django.shortcuts import render
from django.db.models import Q
from django.shortcuts import render_to_response
from search.engine.search import dosearch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import string
import sys
from search.engine.query_process import query_parser_no_stopwords, lower_letters
from search.engine.spelling_correct import correctch
import os
import json
import codecs
import pickle
module_dir = os.path.dirname(__file__)
file_path = os.path.join(module_dir, r'engine/data/')

f_path_color = file_path + "color.dat"
f = open(f_path_color)
color = pickle.load(f)
f.close()

f_path_suggest = file_path + "autocomplete.dat"
f = open(f_path_suggest)
autocomplete_list = pickle.load(f)
f.close()


def is_eng_word(word):
    val = True
    include = set(string.letters + string.digits)
    for ch in word:
        if ch not in include:
            val = False
            break
    return val


def tag_filter(word_list):
    exclude = set(string.punctuation + u" ")
    res_list = []
    for word in word_list:
        word = ''.join(ch for ch in word if ch not in exclude)
        if is_eng_word(word) is False:
            if len(word) < 5 and len(word) > 1:
                res_list.append(word)
        else:
            if len(word) < 8 and len(word) > 1:
                res_list.append(word)
    if u" " in res_list:
        res_list.remove(u" ")
    return res_list


def search(request):
    query = request.GET.get('q', '')
    sensitive_words = [u"\u4e60\u8fd1\u5e73", u"\u674e\u514b\u5f3a",
                       u"\u80e1\u9526\u6d9b", u"\u6e29\u5bb6\u5b9d"]
    chn = 1
    if query in sensitive_words:
        chn = 0
    res = dosearch(query)
    terms = query_parser_no_stopwords(query)
    if query not in terms:
        terms.append(query)
    sug_flag = 0
    sug_query_list = []
    sug_str = ""
    query_cor = correctch(lower_letters(query))

    if query_cor == lower_letters(query):
        for t in terms:
            if t != query:
                t_cor = correctch(t)
                if t_cor != t:
                    word_flag = 1
                    sug_flag = 1
                else:
                    word_flag = 0
                sug_query_list.append((word_flag, t_cor))
                sug_str = sug_str + t_cor
                if is_eng_word(t_cor):
                    sug_str = sug_str + u" "
    else:
        sug_flag = 1
        sug_query_list.append((1, query_cor))
        sug_str = query_cor

    album = []
    singer = []
    play_count_num = []
    title = []
    share_count = []
    lrc = []
    title_color = {}
    singer_color = {}
    result = []
    if res:
        for i in res:
            path = file_path + i + '.json'
            f = codecs.open(path.decode('utf-8'), 'r')
            j = json.load(f)
            f.close()
            tag_list = tag_filter(j["tag"])
            r = int(color[j["title"]][1:3], 16)
            g = int(color[j["title"]][3:5], 16)
            b = int(color[j["title"]][5:7], 16)
            L = 0.2126 * (float(r) / 255) ** 2.2 + 0.7152 * \
                (float(g) / 255) ** 2.2 + 0.0722 * (float(b) / 255) ** 2.2
            if L > 0.5:
                title_color[j["title"]] = "#000000"
                singer_color[j["title"]] = "#444444"
            else:
                title_color[j["title"]] = "#ffffff"
                singer_color[j["title"]] = "#dddddd"

            if len(tag_list) >= 3:
                result.append((j["title"], j["singer"], j["album"], j["ID"], color[j["title"]], title_color[
                              j["title"]], singer_color[j["title"]], j["play_count_num"], tag_list[0], tag_list[1], tag_list[2]))
            elif len(tag_list) == 2:
                result.append((j["title"], j["singer"], j["album"], j["ID"], color[j["title"]], title_color[
                              j["title"]], singer_color[j["title"]], j["play_count_num"], tag_list[0], tag_list[1]))
            elif len(tag_list) == 1:
                result.append((j["title"], j["singer"], j["album"], j["ID"], color[j["title"]], title_color[
                              j["title"]], singer_color[j["title"]], j["play_count_num"], tag_list[0]))
            else:
                result.append((j["title"], j["singer"], j["album"], j["ID"], color[
                              j["title"]], title_color[j["title"]], singer_color[j["title"]], j["play_count_num"]))
    else:
        res = []
        result = []
    paginator = Paginator(result, 10)
    page = request.GET.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    return render_to_response("search.html", {
        "query": query,
        "res": results,
        "sug_flag": sug_flag,
        "sug_query_list": sug_query_list,
        "sug_str": sug_str,
        "autocomplete_list": autocomplete_list,
        "chn": chn,
    })
