import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sqlalchemy
from sklearn import linear_model
from sqlalchemy import create_engine

sns.set()


# define regression model to fill weekend values
def regression_with_past(col: pd.Series):
    # find nans with valid values on right side
    nan_left_idx = []

    for idx_, value in enumerate(col):
        if idx_ != len(col) - 1:
            if (not np.isnan(col[idx_ + 1])) & (np.isnan(value)):
                nan_left_idx.append(idx_)

    # how many days to look back in regression
    days_look_back = 5

    # regression interactively
    for idx_ in nan_left_idx:
        # find data of training (non_nan) and test (nan)
        if idx_ < days_look_back:
            interval_use = list(range(idx_ + 1))
            nan_idx = np.argwhere(np.isnan(col[interval_use]))
            non_nan_idx = np.argwhere(col[interval_use].notnull())
        else:
            interval_use = list(range(idx_ - days_look_back, idx_ + 1))
            nan_idx = np.argwhere(np.isnan(col[interval_use])) + idx_ - days_look_back
            non_nan_idx = np.argwhere(col[interval_use].notnull()) + idx_ - days_look_back

        # train model
        regr = linear_model.LinearRegression()
        regr.fit(non_nan_idx, col[non_nan_idx])

        # fill values with results
        col[nan_idx] = regr.predict(nan_idx)

    return col


# connection to database
engine = create_engine('postgresql://postgres:postgres@localhost:5432/bitcoin_test')

print('Tables in database:', engine.table_names())
con = engine.connect()

tables = ['nasdaq_clean', 'sp500_clean']

# check if I wnat a plot
plotit = True
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
    # lets regress linearly and then take a look

    df_resample_regression = pd.DataFrame().reindex_like(df_resample)

    # only nasdaq has volume column
    if idx == 0:
        df_resample_regression[['price', 'open', 'high', 'low', 'volume_currency']] = \
            df_resample[['price', 'open', 'high', 'low', 'volume_currency']].apply(regression_with_past)

    else:
        df_resample_regression[['price', 'open', 'high', 'low']] = \
            df_resample[['price', 'open', 'high', 'low']].apply(regression_with_past)

    # recalculate the percentage changed in price if non existent
    df_resample_regression['perc_price'] = [(x - y) / x if np.isnan(price) else perc_price
                                            for x, y, price, perc_price
                                            in zip(df_resample_regression['price'],
                                                   df_resample_regression['price'].shift(1),
                                                   df_resample['price'],
                                                   df_resample['perc_price'])]

    if plotit:
        # plot some results
        df_resample_regression.loc['2014-01-01':'2014-01-31', 'price'].plot(marker='.', linestyle='none',
                                                                            ax=axes[idx], label='regression')

        df_resample.loc['2014-01-01':'2014-01-31', 'price'].plot(marker='.', linestyle='none',
                                                                 ax=axes[idx], label='real_data')

        axes[idx].set_title('{} price data'.format(table))

    # resend tables as table_regression
    data_types = {"date_": sqlalchemy.types.TIMESTAMP,
                  "price": sqlalchemy.types.FLOAT,
                  "open": sqlalchemy.types.FLOAT,
                  "high": sqlalchemy.types.FLOAT,
                  "low": sqlalchemy.types.FLOAT,
                  "volume_currency": sqlalchemy.types.FLOAT,
                  "perc_price": sqlalchemy.types.FLOAT}

    df_resample_regression.reset_index(inplace=True)
    df_resample_regression.to_sql('{}_regression'.format(table), con=con, if_exists='replace', dtype=data_types,
                                  index=False)

    print(df_resample.head(10))
    print(df_resample_regression.head(10))

if plotit:
    # get legend right
    h1, l1 = axes[0].get_legend_handles_labels()
    h2, l2 = axes[1].get_legend_handles_labels()
    axes[0].legend(h1, l1)
    axes[1].legend(h2, l2)

    axes[0].get_xaxis().set_visible(False)
    axes[0].tick_params(bottom=False, labelbottom=False)
    fig.subplots_adjust(bottom=0.2)
    plt.show()

con.close()
