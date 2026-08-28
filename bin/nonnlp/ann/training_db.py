from bin.util import DatabaseAdapter as Da
import pandas as pd

batch_size = 1000
steps = 1
# batch_site * steps_per_epoch = 25m


def create_training_table():
    Da.create_training_table_big()


def fill_training_table():
    helpful_not_helpful_rtl()
    #eval_reviews_per_reviewer()


def helpful_not_helpful_rtl(df, ctr, size):
    db_conn, cursor = Da.get_conn_and_cursor()

    ctr = 0
    for i in range(0, steps):
        # Get a chunk of data
        # for df in pd.read_sql_query("SELECT identifier, category, helpful, reviewText FROM everythingdata", db_conn, chunksize=batch_size):
        #print('Fetching batch')
        #query = "SELECT id, category, helpful, reviewText, class FROM everythingdatabalanced LIMIT {batch} OFFSET {offs}"
        #query = query.format(batch=batch_size, offs=i * batch_size)
        #df = pd.read_sql_query(query, db_conn)

        print('Processing Dataframe')
        df["review_text_length"] = df["reviewtext"].apply(lambda x: len(x))

        df[["helpful_c", "not_helpful"]] = df["helpful"].astype(str).str.split(",", expand=True)

        df[["helpful_c", "not_helpful"]] = df[["helpful_c", "not_helpful"]].astype(int)

        df.drop(columns=['helpful'], inplace=True)
        df.drop(columns=['reviewtext'], inplace=True)

        df.rename(columns={'helpful_c': 'helpful'}, inplace=True)

        for index, row in df.iterrows():
            sql = """
                        INSERT INTO trainingdatabig(id, everything_id, review_text_length, helpful, not_helpful, nb_class, bnb_class, sgd_class, lr_class, class)
                        VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
                        """.format(ctr, int(row['id']), int(row['review_text_length']),
                                   row['helpful'], row['not_helpful'],
                                   row['predclass-0'], row['predclass-1'], row['predclass-2'], row['predclass-3'],
                                   row['class'],)
            cursor.execute(sql)

            ctr += 1

            #print('Processed Row nr.:' + str(index))

        db_conn.commit()
        print('Finished batch nr. ' + str(i))


def eval_reviews_per_reviewer():
    db_conn, cursor = Da.get_conn_and_cursor()
    query = """
            UPDATE trainingdatabig
            SET review_count_of_reviewer = sub.count
            FROM (
                SELECT id, COUNT(reviewerid) as count
                FROM everythingdatabalanced
                LEFT JOIN trainingdatabig ON everythingdatabalanced.id = trainingdatabig.everything_id
                GROUP BY everythingdatabalanced.id
                ) sub
            WHERE sub.id = trainingdatabig.everything_id;
            """
    cursor.execute(query)
    db_conn.commit()

