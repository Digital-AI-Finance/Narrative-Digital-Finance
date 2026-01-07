import pandas as pd
from gingado.datasets import load_CB_speeches

speeches = load_CB_speeches(year='all', cache=False)
speeches.set_index('date', inplace=True)
speeches.sort_index(inplace=True)
sdate = speeches.index.min().strftime('%Y%m%d')
edate = speeches.index.max().strftime('%Y%m%d')
speeches.to_csv(f'gingado-cb-speeches_{sdate}-{edate}.csv')