# encoding=utf-8
import jieba
import string


def lower_letters(word):
    include = set(string.uppercase)
    res_word = u""
    for ch in word:
        if ch in include:
            res_word = res_word + ch.lower()
        else:
            res_word = res_word + ch
    return res_word


def words_filter(word_list):
    exclude = set(string.punctuation + u" ")
    res_list = []
    for word in word_list:
        word = ''.join(ch for ch in word if ch not in exclude)
        word = lower_letters(word)
        res_list.append(word)
    return res_list


def query_parser(query):
    term_list = list(jieba.cut_for_search(query))
    stop_words_eng = ["a", "able", "about", "across", "after", "all",
                      "almost", "also", "am", "among", "an", "and", "any",
                      "are", "as", "at", "be", "because", "been", "but", "by",
                      "can", "cannot", "could", "dear", "did", "do", "does",
                      "either", "else", "ever", "every", "for", "from", "get",
                      "got", "had", "has", "have", "he", "her", "hers", "him",
                      "his", "how", "however", "i", "if", "in", "into", "is",
                      "it", "its", "just", "least", "let", "like", "likely",
                      "may", "me", "might", "most", "must", "my", "neither",
                      "no", "nor", "not", "of", "off", "often", "on", "only",
                      "or", "other", "our", "own", "rather", "said", "say", "says",
                      "she", "should", "since", "so", "some", "than", "that", "the",
                      "their", "them", "then", "there", "these", "they", "this",
                      "tis", "to", "too", "twas", "us", "wants", "was", "we", "were",
                      "what", "when", "where", "which", "while", "who", "whom", "why",
                                      "will", "with", "would", "yet", "you", "your"]
    stop_words_chn = [u"的", u"得", u"地", u"你", u"我", u"他", u"和", u"当", u"了"]
    term_list = [
        w for w in term_list if w not in stop_words_eng + stop_words_chn]
    term_list = words_filter(term_list)
    return term_list


def query_parser_no_stopwords(query):
    term_list = list(jieba.cut_for_search(query))
    term_list = words_filter(term_list)
    return term_list
