from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import confusion_matrix
import numpy as np
from bin.util import DatabaseAdapter as Da
from bin.util import Vocabulator as Vocab
from bin.util import Config
import pandas as pd
import pickle
from bin.nonnlp.ann import training_db as TrainingDb
import string


global nb_classifier
global count_vectorizer
global classifiers
global tfidf_vectorizer
global loaded_tfidf


def create_classifiers():
    global classifiers
    nb = MultinomialNB()
    perc = SGDClassifier(loss='perceptron')
    sgd = SGDClassifier(loss='hinge')  # SVM
    lr = SGDClassifier(loss='log')  # Logistic Regression
    classifiers = [nb, perc, sgd, lr]


def train_nb():
    global loaded_tfidf
    global tfidf_vectorizer
    global classifiers

    loaded_tfidf = False
    create_classifiers()

    if Config.NlpTraining.CreateVectorizer.value:
        vocab = Vocab.retrieve_vocab()
        tfidf_vectorizer = TfidfVectorizer(
            vocabulary=vocab,
            stop_words='english',
            max_features=Config.NlpTraining.TfidfFeatureSize.value,
            lowercase=True)
    else:
        load_vectorizer()

    engine = Da.get_engine()

    print('Starting to train Naive Bayes')

    for i in range(0, Config.NlpTraining.Iterations.value):
        # Get a chunk of data
        if i == 0 and not loaded_tfidf:
            print('Fitting vectorizer')
            print('Fetching data-chunk')
            query_ham = "SELECT reviewtext, class FROM EverythingDataHam LIMIT 500000"
            query_spam = "SELECT reviewtext, class FROM EverythingDataSpam LIMIT 150000"

            df1 = pd.read_sql(query_ham, engine)
            df2 = pd.read_sql(query_spam, engine)
            df = pd.concat([df1, df2])
            df['reviewtext'] = df['reviewtext'].apply(lambda x: no_punct(x))
            x = df['reviewtext']
            y = df['class']
            print('Creating training and test set')
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
            tfidf_vectorizer.fit(x_train.values)
            save_vectorizer()
            df = []

        print('Fetching data-chunk')
        query_ham = "SELECT reviewtext, class FROM EverythingDataHam LIMIT {batch} OFFSET {offs}"
        query_spam = "SELECT reviewtext, class FROM EverythingDataSpam LIMIT {batch} OFFSET {offs}"

        query_ham = query_ham.format(batch=Config.NlpTraining.HamBatchSize.value, offs=i * Config.NlpTraining.HamBatchSize.value)
        query_spam = query_spam.format(batch=Config.NlpTraining.SpamBatchSize.value, offs=i * Config.NlpTraining.SpamBatchSize.value)

        df1 = pd.read_sql(query_ham, engine)
        df2 = pd.read_sql(query_spam, engine)
        df = pd.concat([df1, df2])

        df['reviewtext'] = df['reviewtext'].apply(lambda x: no_punct(x))

        x = df['reviewtext']
        y = df['class']

        print('Creating training and test set')
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)


        print('Transforming input with Tfidf-Vectorizer')
        count_train = tfidf_vectorizer.transform(x_train.values)
        count_test = tfidf_vectorizer.transform(x_test.values)

        print('Fitting Classifiers')
        for idx, classifier in enumerate(classifiers):
            if i == 0:
                classifiers[idx] = classifier.partial_fit(count_train, y_train, classes=[0, 1])
            else:
                if not (i == Config.NlpTraining.Iterations.value - 1 or i == Config.NlpTraining.Iterations.value) and classifier.__class__.__name__ == 'SGDClassifier':
                    classifiers[idx] = classifier.partial_fit(count_train, y_train)

            if i == Config.NlpTraining.Iterations.value - 1 and classifier.__class__.__name__ == 'SGDClassifier':
                # Wrap a CalibratedClassifierCV around the SGDClassifier to be able to call predict_proba
                print('Wrapping CV')
                calibrator = CalibratedClassifierCV(classifier, cv='prefit')
                classifier = calibrator.fit(count_train, y_train)
                classifiers[idx] = classifier

            analyze_accuracy(classifier, count_test, y_test)

        print('Trained Epoch: ' + str(i))

    print('Training done!')


def no_punct(text):
    text = "".join([char for char in text if char not in string.punctuation])
    return text


def measure_accuracy():
    global tfidf_vectorizer

    engine = Da.get_engine()
    query_ham = "SELECT reviewtext, class FROM VerificationData WHERE class = 1 LIMIT 500000"
    query_spam = "SELECT reviewtext, class FROM VerificationData WHERE class = 0 LIMIT 500000"

    df1 = pd.read_sql(query_ham, engine)
    df2 = pd.read_sql(query_spam, engine)
    df = pd.concat([df1, df2])

    x = df['reviewtext']
    y = df['class']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.8)

    count_train = tfidf_vectorizer.transform(x_train.values)
    count_test = tfidf_vectorizer.transform(x_test.values)

    for classifier in classifiers:
        analyze_accuracy(classifier, count_test, y_test)


def analyze_accuracy(classifier, count_test, y_test):
    predictions = classifier.predict(count_test)
    TN, FP, FN, TP = confusion_matrix(y_test, predictions).ravel()
    print(classifier.__class__.__name__)
    print('True Positive(TP)  = ', TP, np.round(TP / (TP + FP + TN + FN) * 100, 2))
    print('False Positive(FP) = ', FP, np.round(FP / (TP + FP + TN + FN) * 100, 2))
    print('True Negative(TN)  = ', TN, np.round(TN / (TP + FP + TN + FN) * 100, 2))
    print('False Negative(FN) = ', FN, np.round(FN / (TP + FP + TN + FN) * 100, 2))
    accuracy = (TP + TN) / (TP + FP + TN + FN)
    print('Accuracy of the binary classification = {:0.3f}'.format(accuracy))
    print('')


def predict():
    global tfidf_vectorizer
    global classifiers
    
    db_conn, cursor = Da.get_conn_and_cursor()

    ctr = 0
    ptr = 0
    for i in range(0, Config.NlpPrediction.Iterations.value):
        # Get a chunk of data
        query = "SELECT id, helpful, reviewtext, class FROM verificationdata LIMIT {batch} OFFSET {offs}"

        query = query.format(batch=Config.NlpPrediction.BatchSize.value, offs=i * Config.NlpPrediction.BatchSize.value)

        df = pd.read_sql(query, db_conn)

        count_df = tfidf_vectorizer.transform(df['reviewtext'])
        ptr = 0
        for classifier in classifiers:
            pred_df = classifier.predict_proba(count_df)
            df['predclass-' + str(ptr)] = 1
            df['predclass-' + str(ptr)].iloc[0:len(pred_df)] = pred_df[:, 1].round(2)

            ptr += 1

        print('Inserting...')
        for index, row in df.iterrows():
            sql = """
            INSERT INTO VerificationDataResults (id, verificationid, nb_class, bnb_class, sgd_class, lr_class, class)
            VALUES ({}, {}, {}, {}, {}, {}, {})
            """.format(ctr, row['id'], row['predclass-0'], row['predclass-1'], row['predclass-2'], row['predclass-3'], row['class'])

            cursor.execute(sql)
            ctr += 1

        TrainingDb.helpful_not_helpful_rtl(df, ctr, len(df.index))
        print('Commiting changes.')

        db_conn.commit()
    print('Predicitons done!')


def save_model():
    ctr = 0
    for classifier in classifiers:
        with open('nlp-classifier-' + str(ctr) + '.pkl', 'wb') as f:
            pickle.dump(classifier, f)
        ctr += 1

    save_vectorizer()


def save_vectorizer():
    with open('tfidf-vectorizer.pkl', 'wb') as f:
        pickle.dump(tfidf_vectorizer, f)


def load_model():
    global classifiers
    classifiers = []

    for i in range(0, 4):
        with open('nlp-classifier-'+str(i)+'.pkl', 'rb') as f:
            classifiers.append(pickle.load(f))

    load_vectorizer()


def load_vectorizer():
    global tfidf_vectorizer
    global loaded_tfidf

    with open('tfidf-vectorizer.pkl', 'rb') as f:
        tfidf_vectorizer = pickle.load(f)

    loaded_tfidf = True
