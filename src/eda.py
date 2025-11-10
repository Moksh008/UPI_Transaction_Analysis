import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, '..', 'data')
OUT_DIR = os.path.join(HERE, '..', 'outputs', 'plots')
os.makedirs(OUT_DIR, exist_ok=True)

print('Data dir:', DATA_DIR)

for path in sorted(glob.glob(os.path.join(DATA_DIR, '*.csv'))):
    print('\n---', path, '---')
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print('Failed to read', path, e)
        continue

    print('shape:', df.shape)
    print('columns:', list(df.columns))
    print('\nhead:')
    print(df.head(3).to_string(index=False))

    print('\nmissing per column:')
    print(df.isna().sum())

    num = df.select_dtypes(include=[np.number])
    if not num.empty:
        print('\nnumeric summary:')
        print(num.describe().T)
    else:
        print('\nno numeric columns detected')

    # Attempt to find a date column
    date_cols = [c for c in df.columns if 'date' in c.lower() or 'year' in c.lower() or 'month' in c.lower()]
    if date_cols:
        date_col = date_cols[0]
        print('\nDetected date-like column:', date_col)
        try:
            df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
            if df[date_col].notna().sum() > 0:
                # Resample monthly on first numeric column
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    ts = df.set_index(date_col)[numeric_cols].resample('M').sum()
                    if not ts.empty:
                        col = numeric_cols[0]
                        plt.figure(figsize=(10,4))
                        plt.plot(ts.index, ts[col])
                        plt.title(f"Monthly series from {os.path.basename(path)} - {col}")
                        plt.xlabel('Month')
                        plt.ylabel(col)
                        plt.tight_layout()
                        out = os.path.join(OUT_DIR, os.path.basename(path).replace('.csv','_timeseries.png'))
                        plt.savefig(out)
                        plt.close()
                        print('Saved timeseries plot to', out)
            else:
                print('Date column parsing produced no valid datetimes')
        except Exception as e:
            print('Failed to parse date column', e)

    # Attempt to find a geographic column (state/district/pin)
    geo_cols = [c for c in df.columns if any(k in c.lower() for k in ('state', 'district', 'pin', 'pincode'))]
    if geo_cols:
        geo = geo_cols[0]
        print('\nDetected geo column:', geo)
        # find numeric candidate for aggregation
        candidates = [c for c in df.columns if any(k in c.lower() for k in ('trans', 'txn', 'transaction', 'value', 'amount', 'user')) and c != geo]
        if not candidates:
            candidates = df.select_dtypes(include=[np.number]).columns.tolist()
        if candidates:
            aggcol = candidates[0]
            grp = df.groupby(geo, as_index=False)[aggcol].sum().sort_values(by=aggcol, ascending=False).head(10)
            plt.figure(figsize=(10,5))
            plt.bar(grp[geo].astype(str), grp[aggcol])
            plt.title(f'Top 10 {geo} by {aggcol} ({os.path.basename(path)})')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            out = os.path.join(OUT_DIR, os.path.basename(path).replace('.csv','_top_geo.png'))
            plt.savefig(out)
            plt.close()
            print('Saved top-geo plot to', out)
        else:
            print('No numeric column found to aggregate by geo')

print('\nDone.')
