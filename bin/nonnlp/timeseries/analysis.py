import pandas as pd
from scipy.signal import find_peaks
from scipy.stats import gaussian_kde

import preprocessing


def analyse(df: pd.DataFrame, minimum_reviews=4, min_peak_level=2):
    df, average_rating, average_occurrences = preprocessing.preprocess(df, minimum_reviews)
    peaks = df[['occurrences']]
    peaks = peaks.groupby(level=0).apply(peak_finder, average_occurrences=average_occurrences, min_peak_level=min_peak_level)
    df = df.loc[peaks.index]
    rating = df[['overall']]
    rating = rating.groupby(level=0).apply(rating_finder, average_rating=average_rating)
    df = df.loc[rating.index]
    return df


def peak_finder(x: pd.DataFrame, average_occurrences: pd.DataFrame, min_peak_level):
    average_occurrences = average_occurrences.loc[x.index.values[0][0]][0]
    index, _ = find_peaks(x.values.flatten())
    x = x.iloc[index]
    x = x.droplevel('asin')
    x = x.drop(x[x['occurrences'] < average_occurrences].index)
    x = x.drop(x[x['occurrences'] < min_peak_level].index)
    return x


def rating_finder(x: pd.DataFrame, average_rating):
    average_rating = average_rating.loc[x.index.values[0][0]][0]
    x = x.droplevel('asin')
    x = x.drop(x[x['overall'] < average_rating].index)
    return x

#Attempt at smoothing with KDE, not done because of bias at the boundry:
#def smooth(df: pd.DataFrame):
#    size = df.size
#    offset = size * (-1. / (1 + 4))
#    zeros = pd.Series(0, index=range(offset))#Trying to combat Boundry-Bias by inserting zeros at the edges
#    df = pd.concat([zeros, df, zeros])
#    df = gaussian_kde(df).evaluate(range(0, df.size + 2 * offset))
#    df = df[range(offset, size + offset)]
#    return df
