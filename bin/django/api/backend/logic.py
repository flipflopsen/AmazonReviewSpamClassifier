import os
import pickle
import sys

from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import string
import pandas as pd
from .models import ReviewData

global nlp_classifiers
global tfidf_vectorizer
global ann


def predict(review_data: ReviewData):
    global nlp_classifiers
    global tfidf_vectorizer
    load_vectorizer()

    load_nlp_classifiers()

    review_text = preprocess_text(review_data.review_text)

    vectorized_text = tfidf_vectorizer.transform([review_text])

    predictions = []
    for i in range(0, 4):
        if type(nlp_classifiers[i]).__name__ == 'LogisticRegression':
            predictions.append(nlp_classifiers[i].predict(vectorized_text).round(2))
        else:
            predictions.append(nlp_classifiers[i].predict_proba(vectorized_text)[:, 1].round(2))

    print(review_data.stars)
    if (review_data.stars and review_data.not_helpful and review_data.helpful) is not None:
        if ann is None:
            load_ann()
        df = pd.DataFrame(
            data=[review_data.helpful, review_data.not_helpful, len(review_text), predictions[0], predictions[1],
                  predictions[2], predictions[3]],
            columns=['helpful', 'not_helpful', 'review_text_length', 'bnb_class', 'sgd_class', 'nb_class', 'lr_class'])
        print('Wanted ann pred')
        return ann.predict(df.values)
    else:
        if predictions[0] >= 0.5 and predictions[3] >= 0.5:
            return 1
        else:
            return 0


def preprocess_text(text):
    text = text.lower().replace('[^\w\s]', '')
    text = "".join([char for char in text if char not in string.punctuation])
    return text


def load_nlp_classifiers():
    global nlp_classifiers
    nlp_classifiers = []

    for i in range(0, 4):
        with open('backend/classifiers/nlp-classifier-' + str(i) + '.pkl', 'rb') as f:
            nlp_classifiers.append(pickle.load(f))


def load_ann():
    global ann
    with open('backend/classifiers/ann.pkl', 'rb') as f:
        ann = pickle.load(f)


def load_vectorizer():
    global tfidf_vectorizer

    print(os.getcwd())

    with open('backend/vectorizer/vectorizer.pkl', 'rb') as f:
        tfidf_vectorizer = pickle.load(f)
