import keras
import pandas as pd
from bin.util import DatabaseAdapter as Da
from bin.nonnlp.ann import preprocessing as pp
import pickle
from keras import callbacks
from bin.util.Config import AnnTraining, AnnPrediction

global model


def predict():
    global model
    load_model()
    engine = Da.get_engine()

    ctr = 0
    for i in range(0, AnnPrediction.Iterations.value):
        query = "SELECT everythingid, helpful, not_helpful, review_text_length, bnb_class, sgd_class, nb_class, lr_class, class FROM TrainingDataBig LIMIT {batch} OFFSET {offs}"

        query = query.format(batch=AnnPrediction.ChunkSize.value, offs=i * AnnPrediction.ChunkSize.value)

        df = pd.read_sql(query, engine)
        everything_ids = list(df['everythingid'].values)
        df_pre = df
        predictors = list(set(list(df_pre.columns)))
        # 2. normalize data
        df_pre[predictors] = df_pre[predictors] / df_pre[predictors].max()

        df['ann_class'] = model.predict(df_pre[['helpful', 'not_helpful', 'review_text_length', 'nb_class', 'bnb_class', 'sgd_class', 'lr_class']])
        print('Inserting...')
        # [nb, perc, svm, lr]

        for index, row in df.iterrows():
            sql = """
                   INSERT INTO verificationdataresults (id, verificationid, bnb_class, sgd_class, nb_class, lr_class, ann_class, class)
                   VALUES ({}, {}, {}, {}, {}, {}, {}, {})
                   """.format(ctr, everything_ids[index], row['bnb_class'], row['sgd_class'],
                              row['nb_class'], row['lr_class'], row['ann_class'], row['class'])
            ctr += 1

            # print('Inserting nr. ' + str(index) + 'of batch: ' + str(i))

            engine.execute(sql)

        print('Commiting changes.')


def load_model():
    global model
    with open('ann.pkl', 'rb') as f:
        model = pickle.load(f)