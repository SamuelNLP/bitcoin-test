import csv
import json
import time

import psycopg2


# helper function to send csv data into a postgresql database
def csv_to_postgresql(csv_file, json_column_file, user, password, schema, table_name, time_it=True, log=True,
                      host='localhost', dbname='postgres', port='5432', delimiter=',', header=True, log_ite=1000):
    start = time.time()
    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}"
                            .format(host, dbname, user, password, port))
    cur = conn.cursor()

    with open(json_column_file, 'r') as json_file:
        json_data = json.load(json_file)

    info_table = ', '.join([name_column + ' ' + value[1]
                            for name_column, value
                            in json_data.items()])

    query = """
    DROP TABLE IF EXISTS {a}.{b};
    CREATE TABLE {a}.{b}({c});
    """.format(a=schema, b=table_name, c=info_table)

    cur.execute(query)

    with open(csv_file, 'r') as f:
        reader = csv.reader(f, delimiter=delimiter)

        if header:
            next(reader)

        for idx, row in enumerate(reader):

            query = """
                    INSERT INTO {}.{}.{} VALUES {};
                    """.format(dbname, schema, table_name, tuple(row))

            cur.execute(query)

            conn.commit()

            if log and idx % log_ite == 0:
                print("{}, iteration: {}".format(csv_file, idx + 1), flush=True)

    end = time.time()
    if time_it:
        print('total time: ', end - start, 'seconds')

if __name__ == "__main__":
    print('Importing data to Postgresql')

    # importing data from NASDAQ Composite Historical Data
    csv_to_postgresql('data/NASDAQ Composite Historical Data.csv', 'data/stocks_dtypes.json', 'postgres',
                      'postgres', 'public', 'nasdaq', dbname='bitcoin_test', log_ite=1000)

    # importing data from S&P 500 Historical Data
    csv_to_postgresql('data/S&P 500 Historical Data.csv', 'data/stocks_dtypes.json', 'postgres',
                      'postgres', 'public', 'sp500', dbname='bitcoin_test', log_ite=1000)

    # importing data from BTC_USD
    csv_to_postgresql('data/BTC_USD.csv', 'data/BTC_USD_dtypes.json', 'postgres',
                      'postgres', 'public', 'btc_usd', dbname='bitcoin_test', log_ite=1000000)
