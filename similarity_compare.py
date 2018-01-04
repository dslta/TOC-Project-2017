import logging
from gensim import corpora, models, similarities
from stop_words import get_stop_words
from collections import defaultdict
from pprint import pprint  # pretty-printer
from six import iteritems
import codecs
import re
import os, sys

def file_read(filename):
    file = codecs.open(filename, 'r', 'iso-8859-1') # using utf-8 might have problem
    content = file.read()
    file.close()
    return content

# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO) # see logging events


def vector_space_convert():

    documents = [] # list for storing documents

    for articles in os.listdir('txt/'):
        tmp = 'txt/' + articles
        documents.append(file_read(tmp))

    # remove common words and tokenize
    stop_words = get_stop_words('english') # getting english stop_words
    texts = [[word for word in document.lower().split() if word not in stop_words]
             for document in documents]

    # remove words that appear only once
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    texts = [[token for token in text if frequency[token] > 1] for text in texts]
    texts = [[re.sub('[^A-Za-z]', ' ', token) for token in text] for text in texts] # regular expression removing non-alphabet character
    # texts = [[filter(None, token) for token in text] for text in texts] # remove empty entry of a list


    dictionary = corpora.Dictionary(texts)
    # print(dictionary)
    once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]
    dictionary.filter_tokens(once_ids)  # remove stop words and words that appear only once
    dictionary.compactify()  # remove gaps in id sequence after words that were removed


    dictionary.save('/tmp/deerwester.dict')  # store the dictionary, for future reference

    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize('/tmp/deerwester.mm', corpus)  # store to disk, for later use

def transformation():

    '''
    transform documents from one vector representation into another.
    This process serves two goals:

    1. To bring out hidden structure in the corpus,
    discover relationships between words and use them to describe the documents in a new and (hopefully) more semantic way.

    2. To make the document representation more compact.
    This both improves efficiency (new representation consumes less resources) and efficacy (marginal data trends are ignored, noise-reduction).

    '''

    if (os.path.exists("/tmp/deerwester.dict")):
        dictionary = corpora.Dictionary.load('/tmp/deerwester.dict')
        corpus = corpora.MmCorpus('/tmp/deerwester.mm')
        print("Used files generated from vecter_space_convert()")
    else:
        print("Please generate data set")

    tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model

    corpus_tfidf = tfidf[corpus] # step 2 -- use the model to transform vectors

    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=2) # initialize an LSI transformation
    corpus_lsi = lsi[corpus_tfidf] # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi

    lsi.save('/tmp/model.lsi') # same for tfidf, lda, ...

def similarity_compare(query):

    dictionary = corpora.Dictionary.load('/tmp/deerwester.dict')
    corpus = corpora.MmCorpus('/tmp/deerwester.mm') # comes from vecter_space_convert.py, "From strings to vectors"

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2)

    doc = query
    vec_bow = dictionary.doc2bow(doc.lower().split())
    vec_lsi = lsi[vec_bow] # convert the query to LSI space

    index = similarities.MatrixSimilarity(lsi[corpus]) # transform corpus to LSI space and index it
    index.save('/tmp/deerwester.index') # save similarity index

    sims = index[vec_lsi] # perform a similarity query against the corpus
    sims = sorted(enumerate(sims), key=lambda item: -item[1]) # calculate sorted similarity
    # print(list(enumerate(sims)))
    
    article_name = []
    for article in os.listdir('pdf/'):
        article_name.append(article)
    print(article_name)

    print(sims) # print sorted (document number, similarity score) 2-tuples

    return sims, article_name
