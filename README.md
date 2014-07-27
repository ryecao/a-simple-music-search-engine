#A simple music search engine built with python

##doc_process.py
Build inverted index and other data needed, including dictionary for speel check, store the dominant color of the cover of alubms, etc.

##get_domi_color.py
Calculate the dominant color of album art.

##query_process.py
Process query,including 
- segmentation for chinese
- elimnating stop words
- removing case sensitivity

##search.py
Calculating td-idf, then using vector space model to calc cosine similarities, and ranking the results with customized rules

##spell_check.py
For auto-correction function.

##Screenshot
![screenshot-of-the-site](https://github.com/ryecao/a-simple-music-search-engine/blob/master/media/images/screenshot.png)