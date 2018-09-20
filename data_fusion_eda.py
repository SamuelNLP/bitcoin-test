import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pyauto import visualization_helper as plt_helper
from sqlalchemy import create_engine

from functions.visual_helper import hist_ecdf

sns.set()

# connection to database
engine = create_engine('postgresql://postgres:postgres@localhost:5432/bitcoin_test')

con = engine.connect()

# get data_fusion
rs = con.execute('SELECT * FROM data_fusion')
df = pd.DataFrame(rs.fetchall())
df.columns = [name.replace('weighted_price', 'value') for name in rs.keys()]

# sort by date_ and assign date_ as index
df.set_index('date_', inplace=True)
df.sort_index(inplace=True)

# prepare target variables
df['b_perc_value'] = df['b_perc_value'].shift(-1)
df['b_change_value'] = [True if x > 0 else False for x in df['b_perc_value']]

print('')
