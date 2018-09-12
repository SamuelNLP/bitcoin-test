import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import sqlalchemy

import matplotlib.pyplot as plt
import seaborn as sns

sns.set()

# connection to database
engine = create_engine('postgresql://postgres:postgres@localhost:5432/bitcoin_test')

print('Tables in database:', engine.table_names())
con = engine.connect()

tables = ['nasdaq_clean', 'sp500_clean']

# check if I wnat a plot
plotit = False

if plotit:
    fig, axes = plt.subplots(nrows=2, ncols=1)

for idx, table in enumerate(tables):
    rs = con.execute('SELECT * FROM {}'.format(table))
    df = pd.DataFrame(rs.fetchall())
    df.columns = rs.keys()

    print(df.head())

    df.set_index('date_', inplace=True)

    df_resample = df.resample('D').mean()

    # count days with no data
    df_resample.info()
    print(len(df_resample))

    # print(df_resample.head(30))
    # looks like we don't have data from weekends, the stock market is closed
    # lets interpolate linearly and then take a look

    df_resample_interpolate = pd.DataFrame().reindex_like(df_resample)

    # only nasdaq has volume column
    if idx == 0:
        df_resample_interpolate[['price', 'open', 'high', 'low', 'volume_currency']] = \
            df_resample[['price', 'open', 'high', 'low', 'volume_currency']].interpolate()
    else:
        df_resample_interpolate[['price', 'open', 'high', 'low']] = \
            df_resample[['price', 'open', 'high', 'low']].interpolate()

    # recalculate the percentage changed in price if non existent
    df_resample_interpolate['perc_price'] = [(x - y) / x if np.isnan(price) else perc_price
                                             for x, y, price, perc_price
                                             in zip(df_resample_interpolate['price'],
                                             df_resample_interpolate['price'].shift(1),
                                             df_resample['price'],
                                             df_resample['perc_price'])]

    if plotit:
        # plot some results
        df_resample_interpolate.loc['2014-01-01':'2014-01-31', 'price'].plot(marker='.', linestyle='none',
                                                                             ax=axes[idx], label='interpolated')

        df_resample.loc['2014-01-01':'2014-01-31', 'price'].plot(marker='.', linestyle='none',
                                                                 ax=axes[idx], label='real_data')

        axes[idx].set_title('{} price data'.format(table))

    # resend tables as table_interpolate
    data_types = {"date_":sqlalchemy.types.TIMESTAMP,
                  "price":sqlalchemy.types.FLOAT,
                  "open":sqlalchemy.types.FLOAT,
                  "high":sqlalchemy.types.FLOAT,
                  "low":sqlalchemy.types.FLOAT,
                  "volume_currency":sqlalchemy.types.FLOAT,
                  "perc_price":sqlalchemy.types.FLOAT}

    df_resample_interpolate.reset_index(inplace=True)
    df_resample_interpolate.to_sql('{}_interpolate'.format(table), con=con, if_exists='replace', dtype=data_types, index=False)

    print(df_resample.head(10))
    print(df_resample_interpolate.head(10))

if plotit:
    # get legend right
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    axes[0].legend(h1 , l1)
    axes[1].legend(h2 , l2)

    axes[0].get_xaxis().set_visible(False)
    axes[0].tick_params(bottom=False, labelbottom=False)
    fig.subplots_adjust(bottom=0.2)
    plt.show()

con.close()

