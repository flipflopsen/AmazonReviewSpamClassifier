import pandas
import pickle
from bin.util import DatabaseAdapter as Da
from bin.util.Config import NlpTraining
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from concurrent.futures import ProcessPoolExecutor

global vocab


def retrieve_vocab():
    global vocab
    batch_size = 1_000_000
    iterations = 20
    vocab = set()
    engine = Da.get_engine()

    if NlpTraining.LoadVocabulary.value:
        with open('vobabulary.pkl', 'rb') as f:
            voca = pickle.load(f)
            return voca

    for i in range(0, iterations):
        print('Vocab-Iter nr. ' + str(i))
        query = "SELECT reviewtext FROM EverythingData LIMIT {batch} OFFSET {offs}"
        query = query.format(batch=batch_size, offs=i * batch_size)

        df = pandas.read_sql(query, engine)
        print('Got SQL')
        for text in df['reviewtext'].values:
            words = text.split(' ')
            for word in words:
                vocab.add(word)

    print('Vocab-Size: ' + str(len(vocab)) + ', Iteration: ' + str(i))

    if NlpTraining.SaveVocabulary.value:
        with open('vobabulary.pkl', 'wb') as f:
            pickle.dump(vocab, f)

    return vocab



