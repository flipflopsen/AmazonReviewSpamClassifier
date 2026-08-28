import pandas as pd

from bin.util import DatabaseAdapter

batch_size = 10_000
steps_per_epoch = 1000


def get_conn_and_Dataframe_from_DB():
    conn, cursor = DatabaseAdapter.get_conn_and_cursor()

    for i in range(0, steps_per_epoch):
        cursor.execute("""
        SELECT ev.reviewerid, ev.id, category, ev.helpful FROM everythingdata ev, trainingdatabig td WHERE ev.category = td.category AND  ev.id = td.id AND ev.reviewerid = td.id LIMIT 1500
        """, (batch_size, i * batch_size)
                       )

    data = cursor.fetchall()
    df = pd.DataFrame(data)

    get_helpful(df)
    calc_reviews_per_reviewer(df)


def get_helpful(df):
    df.filter(
        [
            'helpful'
            'id',
            'category',
            'helpful_DB',
            'not_helpful_DB'
        ],
        axis=1
    )
    df['helpful_DB'] = df.helpful.apply(lambda x: x[0])
    df['not_helpful_DB'] = df.helpful.apply(lambda y: y[1])

    load_data_to_helpful(df)


def calc_reviews_per_reviewer(df):
    df.groupby('reviewerID').count()['id'].put('review_per_reviewer').filter(
        [
            'reviewerID',
            'id',
            'category',
            'review_per_reviewer'
        ],
        axis=1
    )
    load_data_to_review_count_of_reviewer(df)


def load_data_to_review_count_of_reviewer(df):
    conn, cursor = DatabaseAdapter.get_conn_and_cursor()

#    df_review_count = df[('review_per_reviewer')]
#   df_review_count.to_sql('trainigdatabig', conn, if_exists='append', index=False)
#   conn.commit
#   conn.close

    for i in range(0, steps_per_epoch):
       cursor.execute("""
        INSERT INTO trainingdatabig (review_count_of_reviewer) VALUES (df[review_count_of_reviewer])
       """, (batch_size, i * batch_size)
                       )


def load_data_to_helpful(df):
    conn, cursor = DatabaseAdapter.get_conn_and_cursor()

#    df_review_count = df[('review_per_reviewer')]
#    df_review_count.to_sql('trainigdatabig', conn, if_exists='append', index=False)
#    conn.commit
#    conn.close

    for i in range(0, steps_per_epoch):
        cursor.execute("""
             INSERT INTO trainingdatabig  (helpful, not_helpful) VALUES (df['review_count_of_reviewer'], df['not_helpful'])
             WHERE (SELECT id, id FROM everythingdata ev WHERE id = ev.id ) 
             """, (batch_size, i * batch_size)
                       )


def preprocess(dataframe):
    print('In TimeSeries preprocessing..')
    # [Identifier], [reviewerID] , [reviewerName], [helpful] , [reviewText], [overall], [summary] , [reviewTime] , [category] , [class]

    # Create a more slim dataframe for analysis
    # with assign
    # df = pd.DataFrame().assign(
    #    ReviewerID=dataframe['reviewerID'],
    #    Helpful=dataframe['helpful'],
    #    ReviewTime=dataframe['reviewTime'],
    #    Class=dataframe['class']
    # )

    # or with filter
    df = dataframe.filter(
        [
            'reviewerID',
            'helpful',
            'reviewTime',
            'class'
        ],
        axis=1
    )

    return df
