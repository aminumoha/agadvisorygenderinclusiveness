# Pdf to Text Conversion 

import os
import shutil
import sys
from logging import exception

from flask import app
from pdfminer.high_level import extract_text
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# articels
article = []
all_docs = []
all_docs_tokenized = []
all_docs_final = []
all_docs_paths = []
# for the new doc uploaded by user
newarticle = []
new_docs = []
new_docs_tokenized = []
new_docs_final = []
new_docs_paths = []
# gender Files
all_gen_docs = []
all_gen_docs_tokenized = []
all_gen_docs_final = []
all_gen_docs_paths = []


def extract_articels():
    for root, dirs, files in os.walk('/experimentation/total_articles'):

        for file in files:
            filepath = os.path.join(root, file)  # --path concatenation
            # print('writing file:'+filepath)
            txtPath = '/experimentation/all_articles/' + file.rpartition('.')[0] + '.txt'
            if not (os.path.exists(txtPath)):
                try:
                    f = open(txtPath, 'w+', errors='ignore')
                    text = extract_text(filepath)
                    f.write(text)
                    article.append(text)
                except:
                    continue


def extract_article(file):
    basepath = os.path.basename(file)
    txtPath = os.getcwd() + "/experimentation/all_articles/" + basepath.rpartition('.')[0] + ".txt"
    if not (os.path.exists(txtPath)):
        try:
            f = open(txtPath, 'w+', errors='ignore')
            myfilepath = file
            text = extract_text(myfilepath)
            f.write(text)
            newarticle.append(text)
            return txtPath
        except Exception as e:
            return 'file cannot be extracted:' + e.__class__
    else:
        return txtPath


# Pdf to Text Conversion
def extract_genderfiles():
    for root, dirs, files in os.getcwd() + "/experimentation/gender_pdf_articles":
        genderarticles = []
        for file in files:
            filepath = os.path.join(root, file)  # this was the problem --path concatenation
            # print('writing file:'+filepath)
            txtPath = '/experimentation/gender_files/' + file.rpartition('.')[
                0] + '.txt'
            if not (os.path.exists(txtPath)):
                try:
                    f = open(txtPath, 'w+', errors='ignore')
                    text = extract_text(filepath)
                    f.write(text)
                    genderarticles.append(text)
                except:
                    continue
            else:
                print('file exists')


# Main Steps of the pre processing
# 1.Prepare the Docs
def perprocess_articles():
    for root, dirs, files in os.walk('/experimentation/all_articles/'):
        for file in files:
            filepath = os.path.join(root, file)
            with open(filepath) as f:
                txt_file_as_string = f.read()
            all_docs.append(txt_file_as_string)
            all_docs_paths.append(filepath);

    tokenizer = RegexpTokenizer(r'\w+')  # to remove punctuations
    customstopwords = ['doi', 'sci', 'org', 'http', 'https', 'www', 'com']
    stopword = set(stopwords.words('english'))
    for doc in all_docs:
        all_docs_tokenized.append(' '.join(tokenizer.tokenize(doc)))
    for art in all_docs_tokenized:
        Words = []
        for word in art.split():
            if word not in stopword and str.lower(word) not in customstopwords and len(word) >= 3 and word.isalpha():
                Words.append(word)
        all_docs_final.append(' '.join(Words))


# 2.Prepare the gender Docs
def prepprocess_genderfiles():
    for root, dirs, files in os.walk(os.getcwd() + '/experimentation/gender_files/'):
        for file in files:
            filepath = os.path.join(root, file)
            with open(filepath) as f:
                txt_file_as_string = f.read()
            all_gen_docs.append(txt_file_as_string)
            all_gen_docs_paths.append(filepath);

    tokenizer = RegexpTokenizer(r'\w+')  # to remove punctuations
    customstopwords = ['doi', 'sci', 'org', 'http', 'https', 'www', 'com']
    stopword = set(stopwords.words('english'))
    for doc in all_gen_docs:
        all_gen_docs_tokenized.append(' '.join(tokenizer.tokenize(doc)))
    for art in all_gen_docs_tokenized:
        Words = []
        for word in art.split():
            if word not in stopword and str.lower(word) not in customstopwords and len(word) >= 3 and word.isalpha():
                Words.append(word)
        all_gen_docs_final.append(' '.join(Words))


# 3. Pre-process a file
def prepprocess_afile(filepath):
    filepath = filepath
    with open(filepath) as f:
        txt_file_as_string = f.read()
    new_docs.append(txt_file_as_string)
    new_docs_paths.append(filepath);

    tokenizer = RegexpTokenizer(r'\w+')  # to remove punctuations
    customstopwords = ['doi', 'sci', 'org', 'http', 'https', 'www', 'com']
    stopword = set(stopwords.words('english'))
    doc = new_docs[new_docs.__len__() - 1]
    new_docs_tokenized.append(' '.join(tokenizer.tokenize(doc)))
    art = new_docs_tokenized[new_docs_tokenized.__len__() - 1]
    Words = []
    for word in art.split():
        if word not in stopword and str.lower(word) not in customstopwords and len(word) >= 3 and word.isalpha():
            Words.append(word)
    new_docs_final.append(' '.join(Words))


# 4. perform doc similarity comparison
# To make uniformed vectors, both gender documents and articles need to be combined first.
# Note that Gender keywrods are inserted as doc [0] in all_docs_final befor vectorization - and then vectorized together
# prepare for cosine similarity
# merge base documents( Gender Related Docs) with the total articles document
def generate_similarity(path):
    # perprocess_articles()
    prepprocess_genderfiles()
    ext = path.rpartition('.')[2]
    if ext == 'txt':
        prepprocess_afile(path)
    else:
        prepprocess_afile(extract_article(path))
    cos_sims = []
    file_similarity_with_gens = [];
    total_sum_similarity_for_file = 0
    file_is_gen_inclusive = 'false'

    count = 0
    tfidf_vectorizer = TfidfVectorizer(use_idf=True)
    for doc in all_gen_docs_final:
        if count > 0:
            del new_docs_final[0]
        new_docs_final.insert(0, doc)
        count = count + 1

        # vectorise the document collection
        tfidf_vectorizer_vectors = tfidf_vectorizer.fit_transform(new_docs_final)
        cosine_similarities = cosine_similarity(tfidf_vectorizer_vectors[0:1],
                                                tfidf_vectorizer_vectors[1:]).flatten()
        cos_sims.append(cosine_similarities);
        file_similarity_with_gens.append(cosine_similarities[len(cosine_similarities) - 1])
        total_sum_similarity_for_file += cosine_similarities[len(cosine_similarities) - 1]
    cosine_similarities[::-1].sort()

    # take average of cosine_similarities
    if len(file_similarity_with_gens) > 0:
        avgsim = total_sum_similarity_for_file / len(file_similarity_with_gens)
    else:
        avgsim = 0
    # 5.moving gender inclsuive files to a new folder
    if avgsim > 0.2 and not (ext == 'txt'):
        file_is_gen_inclusive = 'true,' + repr(avgsim)
        shutil.copy2(path,
                     os.getcwd() + "/experimentation/gender_inclusive/")  # change your destination dir
    return file_is_gen_inclusive + ',' + repr(avgsim)


def find_files(filename, search_path):
    result = []

    # Walking top-down from the root
    for root, dir, files in os.walk(search_path):
        if filename in files:
            result.append(os.path.join(root, filename))
    return result


def process_review(filename, review_result, message):
    info = ''
    if review_result == 'Not Correct':
        # reverse the decision
        if "NOT" in message:
            # add file to Gender inclusive
            shutil.copy2(filename,
                         os.getcwd() + "/experimentation/gender_inclusive/")
            info = 'Document relocated to appropriate directory'
        else:
            # remove file from the list of Gender inclusives
            # file_path = os.getcwd() + "/experimentation/gender_inclusive/" + filename

            try:
                os.remove(filename)
                info = 'Document relocated to appropriate directory'
            except OSError as e:
                info = "Error: %s : %s" % (filename, e.strerror)

    else:
        info = 'No Action Needed! Correct prediction'
    return info
