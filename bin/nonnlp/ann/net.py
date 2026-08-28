import keras.losses
import keras as ks
from keras import metrics
from bin.util.Config import AnnParameters as Params
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
import keras
from sklearn.model_selection import train_test_split
from bin.util import DatabaseAdapter as Da
import pandas as pd
from keras.layers import Dense,LSTM, Embedding, Dropout, Activation, Bidirectional

import matplotlib.pyplot as plt
plt.style.use('ggplot')


global classifier
global keras_model


def create_model_keras():
    global keras_model

    keras_model = ks.Sequential()

    # Input layer size of 7, labels doesn't go into the ann
    # helpful, not_helpful, review_text_length, bnb_class, sgd_class, nb_class, lr_class (label)

    activation_function = Params.ReLu.value
    # First hidden Layer with 500 Neurons
    keras_model.add(Dense(Params.FirstHiddenSize.value, activation=activation_function, input_dim=7))

    # two more hidden layers with both relu
    keras_model.add(Dense(Params.SecondHiddenSize.value, activation=activation_function))
    keras_model.add(Dense(Params.ThirdHiddenSize.value, activation=activation_function))

    # output layer with 1 neuron and sigmoid activation
    keras_model.add(Dense(1, activation='sigmoid'))

    keras_model.compile(
        # Adam to not specify learning rate
        optimizer=Params.Optimizer.value,

        # Binary Cross Entropy for loss measurement
        loss=keras.losses.BinaryCrossentropy(
            label_smoothing=0.2,
            # df feature-axis
            # axis=-1
            reduction=ks.losses.losses_utils.ReductionV2.AUTO,
            name='binary_crossentropy'
        ),

        # And we want to measure the accuracy
        metrics=[metrics.binary_accuracy]
    )

    keras_model.summary()
    return keras_model


def full_aio_model_keras():
    engine = Da.get_engine()

    query_ham = "SELECT reviewtext, class FROM EverythingDataHam LIMIT 1300000"
    query_spam = "SELECT reviewtext, class FROM EverythingDataSpam LIMIT 300000"

    df1 = pd.read_sql(query_ham, engine)
    df2 = pd.read_sql(query_spam, engine)
    df = pd.concat([df1, df2])

    predictors = list(set(list(df.columns)) - set('class'))

    # 3. create x_train, x_test, y_train, y_test from dataframe
    x_train, x_test, y_train, y_test = train_test_split(
        df[predictors].values,
        df['class'].values,
        test_size=0.2
    )

    tokenizer = Tokenizer(num_words=50000)
    tokenizer.fit_on_texts(df['reviewtext'])
    x_train_features = tokenizer.texts_to_sequences(x_train)
    x_test_features = tokenizer.texts_to_sequences(x_test)
    max_length = max([len(seq) for seq in x_train_features + x_test_features])
    x_train_features = pad_sequences(x_train_features, maxlen=max_length)
    x_test_features = pad_sequences(x_test_features, maxlen=max_length)
    le = LabelEncoder()

    embedding_vector_length = 32
    model = keras.Sequential()
    model.add(Embedding(50000, embedding_vector_length, input_length=max_length))
    model.add(Bidirectional(keras.layers.LSTM(64)))
    model.add(Dense(16, activation='relu'))
    model.add(Dropout(0.1))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())

    model.fit(x_train_features, y_train, batch_size=256, epochs=30, validation_data=(x_test_features, y_train),
              verbose=1)

    y_predict = [1 if o > 0.5 else 0 for o in model.predict(x_test_features)]

    cf_matrix = confusion_matrix(y_test, y_predict)
    tn, fp, fn, tp = confusion_matrix(y_test, y_predict).ravel()
    print("Precision: {:.2f}%".format(100 * precision_score(y_test, y_predict)))
    print("Recall: {:.2f}%".format(100 * recall_score(y_test, y_predict)))
    print("F1 Score: {:.2f}%".format(100 * f1_score(y_test, y_predict)))

