import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt
from statsmodels.tsa.holtwinters import ExponentialSmoothing

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'plots')
os.makedirs(OUT_DIR, exist_ok=True)

# Load agg_trans and create quarterly time series of Transaction_count
path = os.path.join(DATA_DIR, 'agg_trans.csv')
if not os.path.exists(path):
    raise FileNotFoundError(path)

df = pd.read_csv(path)
if 'Year' in df.columns and 'Quarter' in df.columns:
    # build quarter-end date
    df['date'] = df.apply(lambda r: pd.Timestamp(year=int(r['Year']), month={1:3,2:6,3:9,4:12}.get(int(r['Quarter']),12), day=1) + pd.offsets.MonthEnd(0), axis=1)
else:
    # fallback: try parse any date-like column
    date_cols = [c for c in df.columns if 'date' in c.lower() or 'month' in c.lower()]
    if date_cols:
        df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], dayfirst=True, errors='coerce')
        df = df.rename(columns={date_cols[0]: 'date'})
    else:
        raise ValueError('No date information found')

# national aggregate
if 'Transaction_count' not in df.columns:
    raise ValueError('Transaction_count column not found')

nat = df.groupby('date', as_index=True)['Transaction_count'].sum().sort_index()
# resample to quarters ensuring regular frequency
nat = nat.resample('Q').sum()

# train/test split: last 4 quarters as test
h = 4
train = nat.iloc[:-h]
test = nat.iloc[-h:]

# Baseline: naive (last value) forecast
naive_forecast = np.repeat(train.iloc[-1], h)

# Holt-Winters (additive trend, no seasonal because short history), try multiplicative seasonality if needed
model = ExponentialSmoothing(train, trend='add', seasonal=None, initialization_method='estimated')
fit = model.fit(optimized=True)
hw_forecast = fit.forecast(h)

# Metrics
def mape(a, f):
    a = np.array(a)
    f = np.array(f)
    return np.mean(np.abs((a - f) / np.where(a==0, 1, a))) * 100

metrics = {
    'naive_MAE': mean_absolute_error(test, naive_forecast),
    'naive_RMSE': sqrt(mean_squared_error(test, naive_forecast)),
    'naive_MAPE': mape(test, naive_forecast),
    'hw_MAE': mean_absolute_error(test, hw_forecast),
    'hw_RMSE': sqrt(mean_squared_error(test, hw_forecast)),
    'hw_MAPE': mape(test, hw_forecast),
}

print('Metrics:')
for k,v in metrics.items():
    print(k, round(v,3))

# save forecast plot
plt.figure(figsize=(10,5))
plt.plot(train.index, train.values, label='train')
plt.plot(test.index, test.values, label='test', marker='o')
plt.plot(test.index, naive_forecast, label='naive_forecast', linestyle='--')
plt.plot(test.index, hw_forecast, label='holt_winters', linestyle='--')
plt.legend()
plt.title('Quarterly Transaction Count Forecast')
out = os.path.join(OUT_DIR, 'forecast_transactions.png')
plt.tight_layout()
plt.savefig(out)
print('Saved forecast plot to', out)
