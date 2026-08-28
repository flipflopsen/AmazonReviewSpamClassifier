from datetime import date
from sqlite3 import Error
import pandas as pd
from enum import Enum
import psycopg2
from sqlalchemy import create_engine


class Tables(Enum):
    CellPhonesData = 'CellPhonesAndAccessories'
    ClothingShoesJewelryData = 'ClothingShoesAndJewelry'
    ElectronicsData = 'Electronics'
    HomeKitchenData = 'HomeAndKitchen'
    SportsOutdoorsData = 'SportsAndOutdoors'
    ToysGamesData = 'ToysAndGames'


def join_nlp_training():
    db_conn, cursor = get_conn_and_cursor()
    sql = """
            UPDATE trainingdatabig
            SET trainingdatabig.bnb_class = tmp_training_nlp.bnb_class, trainingdatabig.nb_class = tmp_training_nlp.nb_class,
             trainingdatabig.sgd_class = tmp_training_nlp.sgd_class, trainingdatabig.lr_class = tmp_training_nlp.lr_class
            FROM tmp_training_nlp
            WHERE trainingdatabig.everything_id = tmp_training_nlp.everything_id AND
            trainingdatabig.overall = tmp_training_nlp.overall AND
            trainingdatabig.label = tmp_training_nlp.label
        """
    cursor.execute(sql)
    db_conn.commit()


def restore_table():
    print('Starting to delete the tmp_table and renaming it to the original')
    db_conne, cursor = get_conn_and_cursor()
    cursor.execute('DROP TABLE trainingdatabig; ALTER TABLE tmp_trainingdatabig RENAME TO trainingdatabig')
    db_conn.commit()


# class declaration
def get_conn_and_cursor():
    global db_conn

    db_conn = psycopg2.connect(
        host='127.0.0.1',
        port='5432',
        dbname="reviews",
        user='pyadapter',
        password='Lol123456!asd#'
    )

    cursor = db_conn.cursor()

    return db_conn, cursor


def get_engine():
    return create_engine("postgresql://pyadapter:Lol123456!asd#@127.0.0.1:5432/reviews")


def create_everything_table():
    conn = psycopg2.connect(
        host='127.0.0.1',
        port='5432',
        dbname="reviews",
        user='pyadapter',
        password='Lol123456!asd#'
    )

    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS EverythingData")
    conn.commit()

    cur.execute("""
    CREATE TABLE Everythingdata(
            id serial PRIMARY KEY,
            asin VARCHAR(255),
            reviewerName VARCHAR(255),
            helpful VARCHAR(255),
            reviewText VARCHAR(50000),
            overall numeric,
            summary VARCHAR(5000),
            reviewTime date,
            category varchar(255),
            class numeric
        );
    """)

    conn.commit()

    cur.execute("""
        INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
        SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from cellphonesandaccessoriesdata;
        
        INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
        SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from electronicsdata;
        
        INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
        SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from homeandkitchendata;
        
        INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
        SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from clothingshoesandjewelrydata;
        
        INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
        SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from homeandkitchendata;
        
        INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
        SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from sportsandoutdoorsdata;
        
        INSERT INTO everythingdata(asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
        SELECT asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class from toysandgamesdata;
        """)

    conn.commit()
    cur.close()
    conn.close()


def create_ham_and_spam():
    conn = psycopg2.connect(
        host='85.214.89.199',
        port='5432',
        dbname="reviews",
        user='pyadapter',
        password='Lol123456!asd#'
    )

    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS EverythingDataHam; DROP TABLE IF EXISTS EverythingDataSpam;")
    conn.commit()

    cur.execute("""
       CREATE TABLE EverythingdataSpam(
            id serial PRIMARY KEY,
            everythingid serial,
            asin VARCHAR(255),
            reviewerName VARCHAR(255),
            helpful VARCHAR(255),
            reviewText VARCHAR(50000),
            overall numeric,
            summary VARCHAR(5000),
            reviewTime date,
            category varchar(255),
            class numeric
        );
        CREATE TABLE EverythingdataHam(
            id serial PRIMARY KEY,
            everythingid serial,
            asin VARCHAR(255),
            reviewerName VARCHAR(255),
            helpful VARCHAR(255),
            reviewText VARCHAR(50000),
            overall numeric,
            summary VARCHAR(5000),
            reviewTime date,
            category varchar(255),
            class numeric
        );
       """)

    conn.commit()

    cur.execute("""
        INSERT INTO EverythingdataSpam(everythingid, asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
        SELECT * FROM EverythingData
        WHERE class = 1
        ORDER BY everythingdata.id
        LIMIT 5000000;
        
        
        INSERT INTO EverythingdataHam(everythingid, asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
        SELECT * FROM EverythingData
        WHERE class = 0
        ORDER BY everythingdata.id
        LIMIT 5000000;
    """)

    conn.commit()

    cur.close()
    conn.close()


def create_verification_table():
    conn = psycopg2.connect(
        host='85.214.89.199',
        port='5432',
        dbname="reviews",
        user='pyadapter',
        password='Lol123456!asd#'
    )

    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS VerificationData;")
    conn.commit()

    cur.execute("""
           CREATE TABLE VerificationData(
            id serial PRIMARY KEY,
            everythingid integer,
            asin VARCHAR(255),
            reviewerName VARCHAR(255),
            helpful VARCHAR(255),
            reviewText VARCHAR(50000),
            overall numeric,
            summary VARCHAR(5000),
            reviewTime date,
            category varchar(255),
            class numeric
        );
        """)

    conn.commit()

    cur.execute("""
        INSERT INTO VerificationData(everythingid, asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
        SELECT * FROM EverythingData
        WHERE class = 1
        ORDER BY everythingdata.id
        OFFSET 5000000;
        
        INSERT INTO VerificationData(everythingid, asin, reviewername, helpful, reviewtext, overall, summary, reviewtime, category, class)
        SELECT * FROM EverythingData
        WHERE class = 0
        ORDER BY everythingdata.id
        OFFSET 5000000;
    """)

    conn.commit()
    cur.close()
    conn.close()


class Database:
    global db_conn

    def __init__(self, path):
        self.path = path

    def create_db(self):
        global db_conn
        try:
            db_conn = psycopg2.connect(
                host='85.214.89.199',
                port='5432',
                dbname="reviews",
                user='pyadapter',
                password='Lol123456!asd#'
            )

        except Error as e:
            print("Failed to write/access dbFile!")

        finally:
            if db_conn:
                c = db_conn.cursor()

                # Get Name from Path "..\\database\\CellPhonesAndAccessoriesDB.db" => "CellPhonesAndAccessories"
                # '../../database/' + table_name.value + 'DB.db'
                data_set_name = self.path.split('/')[3].split('.')[0][:-2]
                print('Evaluated Dataset name: ' + data_set_name)

                data_table = data_set_name + 'Data'

                query = "DROP TABLE IF EXISTS {tableName}"

                c.execute(query.format(tableName=data_table))
                db_conn.commit()

                query = '''
                            CREATE TABLE {tableName}
                            (
                                Identifier VARCHAR(255) PRIMARY KEY,
                                reviewerID VARCHAR(255),
                                asin VARCHAR(255),
                                reviewerName VARCHAR(255),
                                helpful VARCHAR(255),
                                reviewText VARCHAR(50000),
                                overall NUMERIC,
                                summary VARCHAR(5000),
                                reviewTime DATE,
                                category VARCHAR(255),
                                class NUMERIC
                            )
                        '''

                c.execute(query.format(tableName=data_table))
                db_conn.commit()
                db_conn.close()

    def save_into_db(self, json_data, table_name):
        global ctr, db_conn, vals
        try:
            db_conn = psycopg2.connect(
                host='85.214.89.199',
                port='5432',
                dbname="reviews",
                user='pyadapter',
                password='Lol123456!asd#'
            )

        except Error as e:
            print("Failed to write/access dbFile!")

        finally:
            if db_conn:
                try:
                    c = db_conn.cursor()

                    statement_template = ('''
                            INSERT INTO {dbName} (Identifier, reviewerID, asin, reviewerName, helpful, reviewText, overall, summary, reviewTime, category, class)
                                VALUES
                                    {vals}
                            ''')
                    values_template = ('''
                        ({ident}, {revId}, {asin}, {revName}, {helpful}, {revText}, {overall}, {summ}, {revTime}, {cat}, {clazz})
                    ''')

                    self.insert_vals(db_conn, c, json_data, table_name, statement_template, values_template, 10_000)
                    db_conn.commit()

                except Error as e:
                    print(e)
                    print(e.__cause__)

                finally:
                    if db_conn:
                        db_conn.close()
                    else:
                        print('hi')

    # Call method with limit = 0 to load the whole table.
    def retrieve_dataframe(self, table_name, limit):
        global dataframe, db_conn

        try:
            db_conn = psycopg2.connect(
                host='85.214.89.199',
                port='5432',
                dbname="reviews",
                user='pyadapter',
                password='Lol123456!asd#'
            )
            if limit != 0:
                dataframe = pd.read_sql_query("SELECT * FROM " + table_name + 'Data' + ' LIMIT ' + str(limit), db_conn)
            else:
                dataframe = pd.read_sql_query("SELECT * FROM " + table_name + 'Data')
            # print(dataframe.head())

        except Error as e:
            print(e)

        finally:
            db_conn.close()
            return dataframe

    def insert_vals(self, conn, cursor,  json, table_name, statement_template, values_template, batch):
        ctr = 0
        vals = []
        for idx, entry in enumerate(json):
            # Get Date
            entry_date = entry[8].split('.')
            time = date(int(entry_date[2]), int(entry_date[0]), int(entry_date[1]))

            stmt = values_template.format(ident=str(ctr),
                                          revId=str('\'' + str(entry[0]) + '\''),
                                          asin=str('\'' + str(entry[1]) + '\''),
                                          revName=str('\'' + str(entry[2]) + '\''),
                                          helpful=str('\'' + str(entry[3]) + ',' + str(entry[4]) + '\''),
                                          revText=str('\'' + str(entry[5]) + '\''),
                                          overall=str('\'' + str(float(entry[6])) + '\''),
                                          summ=str('\'' + str(entry[7]) + '\''),
                                          revTime=str('\'' + str(time) + '\''),
                                          cat=str('\'' + str(entry[9]) + '\''),
                                          clazz=str('\'' + str(float(entry[10]))) + '\'')
            vals.append(stmt + ',')

            if ctr != 0 and ctr % batch == 0:
                stmt = statement_template.format(dbName=table_name + 'Data', vals="".join(vals)[:-1])
                cursor.execute(str(stmt))
                print('Executing insert for batch, clearing ram..')
                vals = []
            ctr += 1

        stmt = statement_template.format(dbName=table_name + 'Data', vals="".join(vals)[:-1])
        print('Executing last insert, clearing ram..')
        cursor.execute(str(stmt))
        vals = []
        print('Done concatenating')


