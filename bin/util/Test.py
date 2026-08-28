import pickle
import keras
from keras.preprocessing.text import Tokenizer
import tensorflow as tf
from tensorflow import keras as ks
from keras import callbacks
from keras.utils import pad_sequences
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import pandas as pd
import psycopg2


def ann():
    global model
    conn = psycopg2.connect(
        host='127.0.0.1',
        port='5432',
        dbname="reviews",
        user='pyadapter',
        password='Lol123456!asd#'
    )

    cur = conn.cursor()
    query_ham = "SELECT reviewtext, class FROM EverythingDataHam LIMIT 500000"
    query_spam = "SELECT reviewtext, class FROM EverythingDataSpam LIMIT 100000"

    df1 = pd.read_sql(query_ham, conn)
    df2 = pd.read_sql(query_spam, conn)
    df = pd.concat([df1, df2])

    conn.close()

    x_train, x_test, y_train, y_test = train_test_split(
        df['reviewtext'].values,
        df['class'].values,
        test_size=0.2
    )

    tokenizer = Tokenizer(num_words=50000)
    tokenizer.fit_on_texts(x_train)
    x_train_features = tokenizer.texts_to_sequences(x_train)
    x_test_features = tokenizer.texts_to_sequences(x_test)
    max_length = max([len(seq) for seq in x_train_features + x_test_features])
    x_train_features = pad_sequences(x_train_features, maxlen=max_length)
    x_test_features = pad_sequences(x_test_features, maxlen=max_length)

    tensorboard_callback = keras.callbacks.TensorBoard(
        log_dir="./logs",
        histogram_freq=1,
        write_graph=True,
        write_images=False,
        write_steps_per_second=False,
        update_freq="epoch",
        profile_batch=(0,100),
        embeddings_freq=1,
        embeddings_metadata=None
    )


    embedding_vector_length = 32
    model = ks.Sequential()
    model.add(ks.layers.Embedding(50000, embedding_vector_length, input_length=max_length))
    model.add(ks.layers.Bidirectional(ks.layers.LSTM(64)))
    model.add(ks.layers.Dense(16, activation='relu'))
    model.add(ks.layers.Dropout(0.1))
    model.add(ks.layers.Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    print(model.summary())

    model.fit(x_train_features, y_train,
        batch_size=256, epochs=30,
        validation_data=(x_test_features, y_train),
        verbose=1,
        callbacks=[tensorboard_callback])

    y_predict = model.predict(x_test_features)

    cf_matrix = confusion_matrix(y_test, y_predict)
    tn, fp, fn, tp = confusion_matrix(y_test, y_predict).ravel()

    print("Precision: {:.2f}%".format(100 * precision_score(y_test, y_predict)))
    print("Recall: {:.2f}%".format(100 * recall_score(y_test, y_predict)))
    print("F1 Score: {:.2f}%".format(100 * f1_score(y_test, y_predict)))

    save_model()
    print('Model saved, thank you Tim! :)')


def save_model():
    global model
    with open('ann-nlp-lstm.pkl', 'wb') as f:
        pickle.dump(model, f)


if __name__ == '__main__':
    print('Starting to train etc.')
    ann()
