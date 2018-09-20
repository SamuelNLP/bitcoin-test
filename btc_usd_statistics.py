from datetime import timedelta

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew
from sqlalchemy import create_engine

# connection to database
engine = create_engine('postgresql://postgres:postgres@localhost:5432/bitcoin_test')

# print('Tables in database:', engine.table_names())
con = engine.connect()

# get min and max dates
rs = con.execute("""SELECT date_trunc( 'day', min(date_)) AS min_, 
                           date_trunc( 'day', max(date_)) AS max_ FROM btc_usd""")

# drop statistics columns and recreate them
con.execute("""ALTER TABLE btc_usd_by_day
               DROP IF EXISTS median_weighted_price, 
               DROP IF EXISTS mode_weighted_price,
               DROP IF EXISTS kurtosis_weighted_price, 
               DROP IF EXISTS skewness_weighted_price;
               
               ALTER TABLE btc_usd_by_day
               ADD COLUMN median_weighted_price float8, 
               ADD COLUMN mode_weighted_price float8,
               ADD COLUMN kurtosis_weighted_price float8, 
               ADD COLUMN skewness_weighted_price float8;
            """)

df_dates = pd.DataFrame(rs.fetchall())
df_dates.columns = rs.keys()

print(df_dates)

for date_ in pd.date_range(df_dates['min_'].values[0], df_dates['max_'].values[0]):
    # for date_ in pd.date_range('2011-12-31', '2012-01-01'):
    rs = con.execute("""SELECT * FROM btc_usd
                        WHERE date_ BETWEEN '{}' AND '{}'""".format(date_, date_ + timedelta(days=1)))

    df = pd.DataFrame(rs.fetchall())

    if not df.empty:
        df.columns = rs.keys()

        # calculate values
        median_value = np.median(df['weighted_price'])

        # mode
        # cut into 10 factors
        groups = df['weighted_price'].groupby(by=pd.cut(df['weighted_price'], bins=10)).agg('count')
        max_vount_interval = groups.idxmax()
        mode_value = max_vount_interval.mid

        # kustosis and skewness
        kurtosis_value = kurtosis(df['weighted_price'])
        skewness_value = skew(df['weighted_price'])

        con.execute("""UPDATE btc_usd_by_day SET median_weighted_price = {},
                       mode_weighted_price = {}, kurtosis_weighted_price = {}, skewness_weighted_price = {}
                       WHERE date_ = '{}'""".format(median_value, mode_value, kurtosis_value, skewness_value, date_))

    #    print(df)
    print(date_)

con.close()
