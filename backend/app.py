from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
import os
from typing import Optional

app = FastAPI(title='UPI Analysis API')

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_csv(name: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return pd.read_csv(path)


@app.get('/api/summary')
def summary(year: Optional[int] = None):
    try:
        df = load_csv('agg_trans.csv')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='agg_trans.csv not found')
    total_tx = int(df['Transaction_count'].sum())
    total_val = float(df['Transaction_amount'].sum())
    return {'total_transactions': total_tx, 'total_value': total_val}


@app.get('/api/states')
def states():
    try:
        df = load_csv('agg_trans.csv')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='agg_trans.csv not found')
    s = df.groupby('State', as_index=False).agg({'Transaction_count':'sum','Transaction_amount':'sum'})
    return JSONResponse(content=s.to_dict(orient='records'))


@app.get('/api/types')
def types():
    try:
        df = load_csv('agg_trans.csv')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='agg_trans.csv not found')
    t = df.groupby('Transaction_type', as_index=False).agg({'Transaction_count':'sum','Transaction_amount':'sum'})
    return JSONResponse(content=t.to_dict(orient='records'))


@app.get('/api/export')
def export(format: Optional[str] = 'csv'):
    try:
        df = load_csv('agg_trans.csv')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='agg_trans.csv not found')
    out = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'exports')
    os.makedirs(out, exist_ok=True)
    if format == 'csv':
        fp = os.path.join(out, 'agg_trans_export.csv')
        df.to_csv(fp, index=False)
        return FileResponse(fp, filename='agg_trans_export.csv')
    else:
        return JSONResponse(content=df.to_dict(orient='records'))


@app.get('/api/forecast')
def forecast(horizon: Optional[int] = 4):
    try:
        df = load_csv('agg_trans.csv')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='agg_trans.csv not found')
    # build national quarterly series
    if 'Year' in df.columns and 'Quarter' in df.columns:
        df['date'] = df.apply(lambda r: pd.Timestamp(year=int(r['Year']), month={1:3,2:6,3:9,4:12}.get(int(r['Quarter']),12), day=1) + pd.offsets.MonthEnd(0), axis=1)
    nat = df.groupby('date', as_index=True)['Transaction_count'].sum().sort_index().resample('Q').sum()
    if len(nat) == 0:
        raise HTTPException(status_code=400, detail='Not enough data for forecast')
    last = nat.iloc[-1]
    idx = pd.date_range(start=nat.index[-1] + pd.offsets.MonthEnd(3), periods=horizon, freq='Q')
    fc = pd.Series([last]*horizon, index=idx)
    return JSONResponse(content={'forecast': [{'date': str(d.date()), 'value': int(v)} for d,v in zip(fc.index, fc.values)]})
