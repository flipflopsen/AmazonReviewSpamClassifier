import keras
import pandas as pd
from bin.util import DatabaseAdapter as Da
from bin.nonnlp.ann import preprocessing as pp
import pickle
from keras import callbacks
from bin.util.Config import AnnTraining, AnnPrediction

global model


def train_model_keras(keras_model):
    db_conn, cursor = Da.get_conn_and_cursor()
    # overall, helpful, not_helpful, review_text_length, bnb_class, sgd_class, nb_class, label

    tensorboard_callback = keras.callbacks.TensorBoard(
        log_dir="./logs",
        histogram_freq=0,
        write_graph=True,
        write_images=False,
        write_steps_per_second=False,
        update_freq="epoch",
        profile_batch=0,
        embeddings_freq=0,
        embeddings_metadata=None
    )

    for i in range(0, AnnTraining.Iterations.value):
        # Get a chunk of data
        query_ham = "SELECT helpful, not_helpful, review_text_length, bnb_class, sgd_class, nb_class, lr_class, class FROM TrainingDataBig WHERE class = 0 LIMIT {batch} OFFSET {offs}"
        query_spam = "SELECT helpful, not_helpful, review_text_length, bnb_class, sgd_class, nb_class, lr_class, class FROM TrainingDataBig WHERE class = 1 LIMIT {batch} OFFSET {offs}"

        query_ham = query_ham.format(batch=AnnTraining.ChunkSizeHam.value, offs=i * AnnTraining.ChunkSizeHam.value)
        query_spam = query_spam.format(batch=AnnTraining.ChunkSizeSpam.value, offs=i * AnnTraining.ChunkSizeSpam.value)

        df1 = pd.read_sql(query_ham, db_conn)
        df2 = pd.read_sql(query_spam, db_conn)

        df = pd.concat([df1, df2])

        x_train, x_test, y_train, y_test = pp.preprocess_dataframe_keras(df)

        validation_callback = ValidationCallback(x_test, y_test)

        keras_model.fit(
            x_train, y_train,
            batch_size=AnnTraining.BatchSize.value,
            epochs=AnnTraining.Epochs.value,
            callbacks=[
                validation_callback,
                tensorboard_callback
            ],
            verbose=1
        )

    return keras_model


def save_model(trained):
    with open('ann.pkl', 'wb') as f:
        pickle.dump(trained, f)


def evaluate_model_keras(keras_model, x_train, y_train, x_test, y_test):
    pred_train = keras_model.predict(x_train)
    print(pred_train)
    scores = keras_model.evaluate(x_train, y_train, verbose=1)
    print('Accuracy on training data: {}% \n Error on training data: {}'.format(scores[1], 1 - scores[1]))

    pred_test = keras_model.predict(x_test)
    print(pred_test)
    scores2 = keras_model.evaluate(x_test, y_test, verbose=0)
    print('Accuracy on test data: {}% \n Error on test data: {}'.format(scores2[1], 1 - scores2[1]))

    #print(classification_report(pred_test, y_train, target_names=['0', '1']))


class ValidationCallback(callbacks.Callback):
    def __init__(self, x_val, y_val):
        super().__init__()
        self.x_val = x_val
        self.y_val = y_val

    def on_epoch_end(self, epoch, logs={}):
        val_loss, val_acc = self.model.evaluate(self.x_val, self.y_val)
        print("Validation loss: {}, Validation accuracy: {}".format(val_loss, val_acc))