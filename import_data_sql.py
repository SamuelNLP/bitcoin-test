import csv
import json
import time

import psycopg2

# helper function to send csv data into a postgresql database
def csv_to_postgresql(csv_file, json_column_file, user, password, schema, table_name, time_it=True, log=True,
                      host='localhost', dbname='postgres', port='5432', delimiter=','):

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

        for idx, row in enumerate(reader):

            query = """
                    INSERT INTO {}.{}.{} VALUES {};
                    """.format(dbname, schema, table_name, tuple(row))

            cur.execute(query)

            conn.commit()

            if log and idx % 1000 == 0:
                print("iteration " + str(idx))

    end = time.time()
    if time_it:
        print(end - start)
