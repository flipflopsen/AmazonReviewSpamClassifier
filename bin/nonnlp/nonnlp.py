from bin.util import DatabaseAdapter as Da
from bin.util import ParseJson as pj
from ann import net as ann_net
from ann import training
from ann import prediction
from timeseries import preprocessing as prep_ts
from timeseries import analysis as analysis_ts


global timeseries_preprocessed_data
global timeseries_classification


def read_json_and_create_db(table_name, json_path, lines_to_read, json_keys_filter, json_values_filter):
    print_stmt = 'Starting to read ' + str(lines_to_read) +' lines from JSON: ' + table_name.value
    print(print_stmt)

    json_data = pj.read_json(
        json_path,
        lines_to_read,
        json_keys_filter,
        json_values_filter
    )

    #json_data = pj.read_json_threaded(json_path)

    print('Finished reading JSON!')

    print('Starting to create the database...')

    database_path = str('../../database/' + table_name.value + 'DB.db')
    db = Da.Database(database_path)
    db.create_db()

    print('Database created! Starting to save JSON into Database')

    db.save_into_db(json_data, table_name.value)
    json_data = []
    print('Everything finished!')


def preprocess(data):
    global timeseries_preprocessed_data

    print('Starting to preprocess data for TimeSeries')
    timeseries_preprocessed_data = prep_ts.preprocess(data)


def analyse_timeseries():
    global timeseries_classification

    print('Starting to analyse data with TimeSeries-Analysis')
    timeseries_classification = analysis_ts.analyse(timeseries_preprocessed_data)


def create_and_train_model_keras():
    model = ann_net.create_model_keras()

    trained = training.train_model_keras(model)
    training.save_model(trained)
    prediction.load_model()
    prediction.predict()


def add_datasets():
    to_retrieve = [
        Da.Tables.CellPhonesData,
        Da.Tables.ClothingShoesJewelryData,
        Da.Tables.ElectronicsData,
        Da.Tables.HomeKitchenData,
        Da.Tables.SportsOutdoorsData,
        Da.Tables.ToysGamesData
    ]

    for table in to_retrieve:
        read_json_and_create_db(
            table,
            '../../data/' + table.value + '.json',
            10_000_000_000,
            pj.JsonFilter.Standard_Keys_ASIN_No_ReviewTime,
            pj.JsonFilter.Standard_Values_ASIN_No_ReviewTime
        )


if __name__ == '__main__':
    add_datasets()
    Da.create_everything_table()
    Da.create_ham_and_spam()
    Da.create_verification_table()
    training.fill_training_table()
    create_and_train_model_keras()

