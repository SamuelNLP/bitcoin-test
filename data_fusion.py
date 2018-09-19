import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine

# connection to database
engine = create_engine('postgresql://postgres:postgres@localhost:5432/bitcoin_test')

# print('Tables in database:', engine.table_names())
con = engine.connect()

# get all necessary tables
# get btc_usd_by_day_agg
rs = con.execute('SELECT * FROM btc_usd_by_day_agg')
btc_usd = pd.DataFrame(rs.fetchall())
btc_usd.columns = [name.replace('weighted_price', 'value') for name in rs.keys()]
btc_usd = btc_usd.add_prefix('b_')
btc_usd.rename({'b_date_':'date_'}, inplace=True, axis='columns')

# get nasdaq_agg
rs = con.execute('SELECT * FROM nasdaq_agg')
nasdaq = pd.DataFrame(rs.fetchall())
nasdaq.columns = [name.replace('price', 'value') for name in rs.keys()]
nasdaq = nasdaq.add_prefix('n_')
nasdaq.rename({'n_date_':'date_'}, inplace=True, axis='columns')


# get btc_usd_by_day_agg
rs = con.execute('SELECT * FROM sp500_agg')
sp500 = pd.DataFrame(rs.fetchall())
sp500.columns = [name.replace('price', 'value') for name in rs.keys()]
sp500 = sp500.add_prefix('s_')
sp500.rename({'s_date_':'date_'}, inplace=True, axis='columns')


# get btc_usd_by_day_agg
rs = con.execute('SELECT * FROM btc_hacks_clean_resample')
btc_hacks = pd.DataFrame(rs.fetchall())
btc_hacks.columns = rs.keys()
btc_hacks = btc_hacks.add_prefix('b_')
btc_hacks.rename({'b_date_':'date_'}, inplace=True, axis='columns')


data = btc_usd.merge(nasdaq, how='left', on='date_', suffixes=('', ''))
data = data.merge(sp500, how='left', on='date_', suffixes=('', ''))
data = data.merge(btc_hacks, how='left', on='date_', suffixes=('', ''))

data['weekday'] = data['date_'].dt.weekday
data['day_of_month'] = data['date_'].dt.day
data['month'] = data['date_'].dt.month
data['year'] = data['date_'].dt.year
data['weekend'] = data['date_'].dt.weekday > 4
data['month_area'] = pd.cut(data['day_of_month'], bins=4, labels=[0.25, 0.5, 0.75, 1])
data['year_area'] = pd.cut(data['month'], bins=4, labels=[0.25, 0.5, 0.75, 1])


data.sort_values(by='date_', inplace=True)

# send to sql
data.to_sql('data_fusion', con=con, if_exists='replace', index=False)

con.close()