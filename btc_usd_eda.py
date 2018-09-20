import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pyauto import visualization_helper as plt_helper
from sqlalchemy import create_engine

from functions.visual_helper import hist_ecdf

sns.set()

# connection to btc_usdbase
engine = create_engine('postgresql://postgres:postgres@localhost:5432/bitcoin_test')

con = engine.connect()

# get btc_usd_by_day_agg
rs = con.execute('SELECT * FROM btc_usd_by_day_agg')
btc_usd = pd.DataFrame(rs.fetchall())
btc_usd.columns = [name.replace('weighted_price', 'value') for name in rs.keys()]

# date aggregations
btc_usd['weekday'] = btc_usd['date_'].dt.weekday
btc_usd['day_of_month'] = btc_usd['date_'].dt.day
btc_usd['month'] = btc_usd['date_'].dt.month
btc_usd['year'] = btc_usd['date_'].dt.year
btc_usd['weekend'] = btc_usd['date_'].dt.weekday > 4
btc_usd['month_area'] = pd.cut(btc_usd['day_of_month'], bins=4, labels=[0.25, 0.5, 0.75, 1])
btc_usd['year_area'] = pd.cut(btc_usd['month'], bins=4, labels=[0.25, 0.5, 0.75, 1])

# sort by date_ and assign date_ as index
btc_usd.set_index('date_', inplace=True)
btc_usd.sort_index(inplace=True)

# prepare target variables
btc_usd.dropna(inplace=True)

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

btc_usd = btc_usd.merge(nasdaq, how='left', on='date_', suffixes=('', ''))
btc_usd = btc_usd.merge(sp500, how='left', on='date_', suffixes=('', ''))
btc_usd = btc_usd.merge(btc_hacks, how='left', on='date_', suffixes=('', ''))

# columns for values and related to date
measures = ['perc_close_open', 'perc_high_low', 'perc_value', 'volume_btc', 'value', 'days_without_hacks']
aggregations = ['weekday', 'month_area', 'year_area', 'year', 'weekend']

# plot type
draw_plots = False
draw_pair = False
draw_join = False
draw_ecdf = True
draw_box = False
draw_heatmap = True
threshold_heat = 0.3
draw_swarm = False

# -----------------Plots----------------------#
fig, ax1 = plt.subplots()
btc_usd.set_index('date_', inplace=True)
btc_usd_m = btc_usd.resample('W').mean()

data2 = btc_usd_m['volume_btc']
y_label2 = 'volume_btc'

data1 = btc_usd['loss_usd']
y_label1 = 'hacks'

color = 'tab:red'
ax1.set_ylabel(y_label1, color=color)
ax1.plot(data1, 'rd')
ax1.tick_params(axis='y', labelcolor=color)

plt.yscale('log')

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel(y_label2, color=color)  # we already handled the x-label with ax1
ax2.plot(data2, color=color)
ax2.tick_params(axis='y', labelcolor=color)

plt.yscale('log')

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.savefig('images/volume_btc_hacks.png')

# --------------------------------------------#

# plt.figure()
# btc_usd_m[['volume_currency', 'n_volume_currency']].plot()
# plt.savefig('images/volumes.png')

# -----------------Pairplot-------------------#
if draw_pair:
    plt.figure()
    sns.pairplot(btc_usd[measures], hue='change_volume_bool', diag_kind='kde', height=2)
    sns.pairplot(btc_usd[aggregations], hue='change_volume_bool', diag_kind='kde', height=2)

plt.close()
# --------------------------------------------#

# -----------------Joinplots------------------#
if draw_join:
    plt.figure()
    sns.set_style('white')
    ax = sns.jointplot(btc_usd['change_volume'], btc_usd['weekday'], xlim=[-0.06, 0.06])
    ax.ax_joint.set_xlabel('BTC Volume change')
    ax.ax_joint.set_ylabel('Week days')
    ax.ax_joint.set_yticks([0, 1, 2, 3, 4, 5, 6])
    ax.ax_joint.set_yticklabels(labels=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    ax.fig.suptitle('BTC change vs Weekdays')

plt.close()
# --------------------------------------------#

# ------------------ECDF----------------------#
if draw_ecdf:
    # compute ECDF and histogram of perc_value
    for name in btc_usd.columns:
        # no need to plot binary features
        if len(btc_usd[name].unique()) > 2:
            hist_ecdf(btc_usd[name], name=name, ecdf_theor=False)

    # hist_ecdf(btc_usd['perc_value'], name='perc_value', ecdf_theor=True)
    hist_ecdf(btc_usd['value'], name='value', ecdf_theor=False, xlog_scale=False)

plt.close()
# --------------------------------------------#

# ------------------Box plots-----------------#
if draw_box:
    for measure in measures:
        for aggregation in aggregations:
            plt.figure()
            sns.boxplot(x=aggregation, y=measure, data=btc_usd, showfliers=False, whis=2.5)
            plt.title('Boxplot of ' + measure + ' vs ' + aggregation)
            plt.savefig('images/' + measure + '_vs_' + aggregation + '_boxplot.png')

            plt.figure()
            sns.boxplot(x=aggregation, y=measure, data=btc_usd, showfliers=True)
            plt.title('Boxplot of ' + measure + ' vs ' + aggregation + ' with outliers')
            plt.savefig('images/' + measure + '_vs_' + aggregation + '_boxplot_outliers.png')

plt.close()
# --------------------------------------------#

# ------------------Heatmap corr--------------#
if draw_heatmap:
    # calculate the correlation matrix
    corr = btc_usd.corr().round(decimals=2)

    # plot the heatmap
    plt.figure(figsize=(15, 10))
    sns.heatmap(corr, xticklabels=corr.columns, yticklabels=corr.columns, annot=True, cbar=False)
    plt_helper.rotate_axis(90, xy_axis='x', bottom_pad=0.2)
    plt.title('Correlation between variables')
    plt.savefig('images/correlation.png')

    if threshold_heat is not None:
        corr_threshold = corr[(corr >= threshold_heat) | (corr <= - threshold_heat)]

        plt.figure(figsize=(15, 10))
        sns.heatmap(corr_threshold, xticklabels=corr_threshold.columns, yticklabels=corr_threshold.columns, annot=True,
                    cbar=False)
        plt_helper.rotate_axis(90, xy_axis='x', bottom_pad=0.2)
        plt.title('Correlation between variables')
        plt.savefig('images/correlation_threshold_{}.png'.format(threshold_heat))

plt.close()
# --------------------------------------------#

# ------------------Swarnplots----------------#
if draw_swarm:
    for measure in measures:
        for aggregation in aggregations:
            plt.figure()
            sns.swarmplot(x=aggregation, y=measure, data=btc_usd, size=2)
            plt.title('Swarmplot of ' + measure + ' vs ' + aggregation)
            plt.savefig('images/' + measure + '_vs_' + aggregation + '_swarm.png')

plt.close()
# --------------------------------------------#

# plt.show()
print(btc_usd.head())
