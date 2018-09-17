import numpy as np
import pandas as pd
import seaborn as sns
import sqlalchemy
from sqlalchemy import create_engine

sns.set()

# connection to database
engine = create_engine('postgresql://postgres:postgres@localhost:5432/bitcoin_test')

# print('Tables in database:', engine.table_names())
con = engine.connect()

# choose table to change and columns to use
table = 'btc_hacks'
columns_keep = ['date_', 'loss_usd']

rs = con.execute('SELECT * FROM {}'.format(table))
df = pd.DataFrame(rs.fetchall())
df.columns = rs.keys()
print(df.head())

# get min and max dates
rs = con.execute("""SELECT date_trunc( 'day', min(date_)) AS min_, 
                           date_trunc( 'day', max(date_)) AS max_ FROM btc_usd""")

df_dates = pd.DataFrame(rs.fetchall())
df_dates.columns = rs.keys()
df_dates = df_dates.T
df_dates.columns = ['date_']

df = df[columns_keep]
df = df.append(df_dates, ignore_index=True, sort=False)
df.set_index('date_', inplace=True)

# process lost_usd to drop the dollar sign and convert to numerical
df['loss_usd'] = pd.to_numeric(df['loss_usd'].str.replace(pat='\$|,', repl='', regex=True))

df_resample = df.resample('D').mean()

# add new columns
df_resample = df_resample.assign(lost_by_days_without_hacks=0, days_without_hacks=0)

days_no_hacks = 0
last_loss_hack = 0

for label, row in df_resample.iterrows():
    if not np.isnan(row['loss_usd']):
        days_no_hacks = 0
        last_loss_hack = row['loss_usd']

        df_resample.loc[label, 'days_without_hacks'] = days_no_hacks

    else:
        days_no_hacks += 1

        df_resample.loc[label, 'days_without_hacks'] = days_no_hacks

    df_resample.loc[label, 'lost_by_days_without_hacks'] = last_loss_hack / (days_no_hacks + 1)

df_resample.reset_index(inplace=True)

# send table as table btc_clean_resample
data_types = {"date_": sqlalchemy.types.TIMESTAMP,
              "loss_usd": sqlalchemy.types.FLOAT,
              "lost_by_days_without_hacks": sqlalchemy.types.FLOAT,
              "days_without_hacks": sqlalchemy.types.FLOAT}

df_resample.to_sql('{}_clean_resample'.format(table), con=con, if_exists='replace', dtype=data_types,
                   index=False)

con.close()
