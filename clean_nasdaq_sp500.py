import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy

# connection to database
engine = create_engine('postgresql://postgres:postgres@localhost:5432/bitcoin_test')

print('Tables in database:', engine.table_names())
con = engine.connect()

tables = ['nasdaq', 'sp500']

for table in tables:
    rs = con.execute('SELECT * FROM {}'.format(table))
    df = pd.DataFrame(rs.fetchall())
    df.columns = rs.keys()

    print(df.head())

    # clean two columns in tables 'sp500' and 'nasdaq'
    # clean % from change_percentage column and rescale it from [0 100] to [0 1]
    df['change_percentage'] = pd.to_numeric(df['change_percentage'].str.strip('%')) / 100

    # repalce M (millions) and B (billions) by numbers in vol column
    def replace_M_or_B(value):
        if 'M' in value:
            value = float(value.strip('M')) * 1E6
        elif 'B' in value:
            value = float(value.strip('B')) * 1E6
        else:
            value = float(value)

        return value

    # if nasdaq process volume, else ignore
    if table == 'nasdaq':
        df['vol'] = df['vol'].apply(replace_M_or_B)
    else:
        df.drop(columns='vol', inplace=True)

    # rename column to perc_price
    df.rename(columns={'change_percentage':'perc_price', 'vol':'volume_currency'}, inplace=True)

    # check for nans
    print('Missing values in columns:')
    print(df.isnull().any())

    data_types = {"date_":sqlalchemy.types.TIMESTAMP,
                  "price":sqlalchemy.types.FLOAT,
                  "open":sqlalchemy.types.FLOAT,
                  "high":sqlalchemy.types.FLOAT,
                  "low":sqlalchemy.types.FLOAT,
                  "volume_currency":sqlalchemy.types.FLOAT,
                  "perc_price":sqlalchemy.types.FLOAT}

    df.to_sql('{}_clean'.format(table), con=con, if_exists='replace', dtype=data_types, index=False)

con.close()

