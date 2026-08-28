import pandas as pd
import numpy as np


def preprocess(df: pd.DataFrame, minimum_reviews=4, freq='2W'):
    df = df[['asin', 'reviewtime', 'overall']]
    df['occurrences'] = 1
    df['reviewtime'] = pd.to_datetime(df['reviewtime'], format='%Y-%m-%d')
    df = df.set_index(['asin', 'reviewtime'])
    df = df.groupby(level=['asin', 'reviewtime']).agg({'occurrences': 'sum', 'overall': 'mean'})
    df = df.sort_values(['asin', 'reviewtime'])
    minimum = df[['occurrences']]
    minimum = minimum.groupby('asin').sum()
    df = df.drop(minimum[minimum['occurrences'] < minimum_reviews].index)
    df = df.groupby(level=0) \
        .apply(lambda x: x.reset_index(level=0, drop=True)
               .resample(freq).apply({'occurrences': 'sum', 'overall': 'mean'})) \
        .fillna(0).round(decimals=2)
    average_occurrences = df[['occurrences']]
    average_occurrences = average_occurrences.groupby('asin').mean()
    average_rating = df[['overall']]
    average_rating = average_rating.groupby('asin').agg(w_mean, df)
    return df, average_rating, average_occurrences


def w_mean(x, df):
    return np.average(x.values.flatten(), weights=df.loc[x.index, 'occurrences'].values)
