from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import numpy as np


def preprocess_df(dataframe):
    # Create Arrays for the Features and normalize data
    print('In ANN-Preprocessing...')

    x_train, x_test, y_train, y_test = preprocess_dataframe_keras(dataframe)
    # x_train, x_test, y_train, y_test = preprocess_dataframe_scikit(dataframe)

    return x_train, x_test, y_train, y_test


# rpr_approx = reviews per reviewer
# rtl = review text length
def create_train_test_data(timeseries_classification, rpr, review_count_of_reviewer, helpful, not_helpful, rtl, labels):
    print('In ANN-Preprocessing...')

    x = np.column_stack(
            (
                timeseries_classification,
                review_count_of_reviewer,
                rpr,
                helpful,
                not_helpful,
                rtl
            )
    )

    scaler = MinMaxScaler()
    x_norm = scaler.fit_transform(x)

    x_train, x_test, y_train, y_test = train_test_split(
        x_norm,
        labels,
        test_size=0.2,
        random_state=42
    )

    return x_train, x_test, y_train, y_test


def preprocess_dataframe_keras(dataframe):
    # 1. remove the label/class
    predictors = list(set(list(dataframe.columns)) - set('label'))

    # 2. normalize data
    dataframe[predictors] = dataframe[predictors] / dataframe[predictors].max()
    df = dataframe[predictors]
    df.drop('label', axis=1, inplace=True)

    print(df)
    # 3. create x_train, x_test, y_train, y_test from dataframe
    x_train, x_test, y_train, y_test = train_test_split(
        df.values,
        dataframe['label'].values,
        test_size=0.2,
        random_state=42
    )

    # 4. show me
    dataframe.describe()
    print(x_train.shape)
    print(x_test.shape)

    # 5. return it
    return x_train, x_test, y_train, y_test
