import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sqlalchemy import create_engine
from pyauto import visualization_helper as plt_helper

from functions.visual_helper import ecdf, hist_ecdf

sns.set()

# connection to btc_usdbase
engine = create_engine('postgresql://postgres:postgres@localhost:5432/bitcoin_test')

# print('Tables in btc_usdbase:', engine.table_names())
con = engine.connect()

# get all necessary tables
# get btc_usd_by_day_agg
rs = con.execute('SELECT * FROM btc_usd_by_day_agg')
btc_usd = pd.DataFrame(rs.fetchall())
btc_usd.columns = [name.replace('weighted_price', 'value') for name in rs.keys()]

btc_usd['weekday'] = btc_usd['date_'].dt.weekday
btc_usd['day_of_month'] = btc_usd['date_'].dt.day
btc_usd['month'] = btc_usd['date_'].dt.month
btc_usd['year'] = btc_usd['date_'].dt.year
btc_usd['weekend'] = btc_usd['date_'].dt.weekday > 4

# sort by date_ and assign date_ as index
btc_usd.set_index('date_', inplace=True)
btc_usd.sort_index(inplace=True)

btc_usd['perc_value'] = btc_usd['perc_value'].shift(-1)
btc_usd['change_value'] = ['positive' if x > 0 else 'negative' for x in btc_usd['perc_value']]
btc_usd['month_area'] = pd.cut(btc_usd['day_of_month'], bins=4, labels=[0.25, 0.5, 0.75, 1])
btc_usd['year_area'] = pd.cut(btc_usd['month'], bins=4, labels=[0.25, 0.5, 0.75, 1])

# btc_usd.plot(y = 'value')
# plt.show()

# columns for values and related to date
measures = ['perc_close_open', 'perc_high_low', 'perc_value', 'volume_btc', 'value']
aggregations = ['weekday', 'month_area', 'year_area', 'year', 'weekend']

# sns.pairplot(btc_usd[measures + ['change_value']], hue='change_value', diag_kind='kde', height=2)
# sns.pairplot(btc_usd[aggregations + ['change_value']], hue='change_value', diag_kind='kde', height=2)

# # sns.set_style('white')
# ax = sns.jointplot(btc_usd['perc_value'], btc_usd['weekday'], xlim=[-0.06, 0.06])
# ax.ax_joint.set_xlabel('BTC Value change')
# ax.ax_joint.set_ylabel('Week days')
# ax.ax_joint.set_yticks([0, 1, 2, 3, 4, 5, 6])
# ax.ax_joint.set_yticklabels(labels=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
# ax.fig.suptitle('BTC change vs Weekdays')

#-----------------------ECDF-----------------------#
# # compute ECDF and histogram of perc_value
# for name in btc_usd.columns:
#     # no need to plot binary features
#     if len(btc_usd[name].unique()) > 2:
#         hist_ecdf(btc_usd[name], name=name, ecdf_theor=False)

# hist_ecdf(btc_usd['perc_value'], name='perc_value', ecdf_theor=True)
# hist_ecdf(btc_usd['value'], name='value', ecdf_theor=False, xlog_scale=True)
#----------------------------------------------------#

#--------------------Box plots-----------------------#
# for measure in measures:
#     for aggregation in aggregations:
#         plt.figure()
#         sns.boxplot(x=aggregation, y=measure, data=btc_usd, showfliers=False, whis=2.5)
#         plt.title('Boxplot of ' + measure + ' vs ' + aggregation)
#         plt.savefig('images/' + measure + '_vs_' + aggregation + '_boxplot.png')
#
#         # plt.figure()
#         # sns.boxplot(x=aggregation, y=measure, data=btc_usd, showfliers=True)
#         # plt.title('Boxplot of ' + measure + ' vs ' + aggregation + ' with outliers')
#         # plt.savefig('images/' + measure + '_vs_' + aggregation + '_boxplot_outliers.png')

#----------------------------------------------------#

#-------------------heatmap corr---------------------#
# calculate the correlation matrix
corr = btc_usd.corr().round(decimals=2)

# plot the heatmap
plt.figure(figsize=(15, 10))
sns.heatmap(corr, xticklabels=corr.columns, yticklabels=corr.columns, annot=True, cbar=False)
plt_helper.rotate_axis(90, xy_axis='x', bottom_pad=0.2)
plt.title('Correlation between variables')
plt.savefig('images/correlation.png')

#---------------------------------------------------#

# plt.show()
print(btc_usd.head())
