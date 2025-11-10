from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import numpy as np
import os
from datetime import datetime
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt
import io

app = FastAPI(title="UPI Digital Payments API", version="1.0.0")

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_data():
    """Load and prepare all CSV files"""
    agg_trans = pd.read_csv(os.path.join(DATA_DIR, 'agg_trans.csv'))
    agg_user = pd.read_csv(os.path.join(DATA_DIR, 'agg_user.csv'))
    
    # Create date column
    for df in [agg_trans, agg_user]:
        if 'Year' in df.columns and 'Quarter' in df.columns:
            df['date'] = df.apply(
                lambda r: pd.Timestamp(year=int(r['Year']), 
                                     month={1:3,2:6,3:9,4:12}.get(int(r['Quarter']),12), 
                                     day=1) + pd.offsets.MonthEnd(0), 
                axis=1
            )
    
    return agg_trans, agg_user

@app.get("/")
def root():
    return {"message": "UPI Digital Payments API", "version": "1.0.0"}

@app.get("/api/summary")
def get_summary(year: int = None, quarter: int = None):
    """Get summary statistics with optional filters"""
    try:
        agg_trans, _ = load_data()
        
        # Apply filters
        df = agg_trans.copy()
        if year:
            df = df[df['Year'] == year]
        if quarter:
            df = df[df['Quarter'] == quarter]
        
        total_transactions = df['Transaction_count'].sum()
        total_value = df['Transaction_amount'].sum()
        
        # Calculate CAGR (2018-2022)
        yearly = agg_trans.groupby('Year')['Transaction_count'].sum()
        if len(yearly) > 1:
            start_val = yearly.iloc[0]
            end_val = yearly.iloc[-1]
            years = len(yearly) - 1
            cagr = ((end_val / start_val) ** (1/years) - 1) * 100
        else:
            cagr = 0
        
        # YoY growth
        if len(yearly) > 1:
            yoy_growth = ((yearly.iloc[-1] - yearly.iloc[-2]) / yearly.iloc[-2]) * 100
        else:
            yoy_growth = 0
        
        return {
            "total_transactions": int(total_transactions),
            "total_value": float(total_value),
            "cagr": round(cagr, 2),
            "yoy_growth": round(yoy_growth, 2),
            "states_count": df['State'].nunique(),
            "transaction_types": df['Transaction_type'].nunique() if 'Transaction_type' in df.columns else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/states")
def get_states(limit: int = Query(10, ge=1, le=50)):
    """Get state-wise transaction data"""
    try:
        agg_trans, _ = load_data()
        
        state_data = agg_trans.groupby('State').agg({
            'Transaction_count': 'sum',
            'Transaction_amount': 'sum'
        }).reset_index()
        
        state_data = state_data.sort_values('Transaction_count', ascending=False).head(limit)
        
        return {
            "states": state_data.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/state/{state_name}")
def get_state_detail(state_name: str):
    """Get detailed data for a specific state"""
    try:
        agg_trans, _ = load_data()
        
        state_df = agg_trans[agg_trans['State'] == state_name]
        
        if state_df.empty:
            raise HTTPException(status_code=404, detail=f"State '{state_name}' not found")
        
        # Time series data
        time_series = state_df.groupby('date').agg({
            'Transaction_count': 'sum',
            'Transaction_amount': 'sum'
        }).reset_index()
        time_series['date'] = time_series['date'].astype(str)
        
        # By transaction type
        if 'Transaction_type' in state_df.columns:
            by_type = state_df.groupby('Transaction_type').agg({
                'Transaction_count': 'sum',
                'Transaction_amount': 'sum'
            }).reset_index()
        else:
            by_type = []
        
        return {
            "state": state_name,
            "total_transactions": int(state_df['Transaction_count'].sum()),
            "total_value": float(state_df['Transaction_amount'].sum()),
            "time_series": time_series.to_dict('records'),
            "by_type": by_type.to_dict('records') if len(by_type) > 0 else []
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/types")
def get_transaction_types(type: str = None, year: int = None):
    """Get transaction type statistics"""
    try:
        agg_trans, _ = load_data()
        
        if 'Transaction_type' not in agg_trans.columns:
            return {"types": []}
        
        df = agg_trans.copy()
        if type:
            df = df[df['Transaction_type'] == type]
        if year:
            df = df[df['Year'] == year]
        
        type_data = df.groupby('Transaction_type').agg({
            'Transaction_count': 'sum',
            'Transaction_amount': 'sum'
        }).reset_index()
        
        type_data = type_data.sort_values('Transaction_count', ascending=False)
        
        return {
            "types": type_data.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/brands")
def get_brand_market_share():
    """Get brand/app market share data"""
    try:
        _, agg_user = load_data()
        
        if 'Brand' not in agg_user.columns:
            return {"brands": []}
        
        brand_data = agg_user.groupby('Brand').agg({
            'Transaction_count': 'sum'
        }).reset_index()
        
        brand_data = brand_data.sort_values('Transaction_count', ascending=False).head(10)
        
        total = brand_data['Transaction_count'].sum()
        brand_data['percentage'] = (brand_data['Transaction_count'] / total * 100).round(2)
        
        return {
            "brands": brand_data.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forecast")
def get_forecast(horizon: int = Query(4, ge=1, le=12)):
    """Get transaction forecast"""
    try:
        agg_trans, _ = load_data()
        
        # National time series
        nat = agg_trans.groupby('date')['Transaction_count'].sum().sort_index().resample('Q').sum()
        
        # Train model
        model = ExponentialSmoothing(nat, trend='add', seasonal=None, initialization_method='estimated')
        fit = model.fit(optimized=True)
        forecast = fit.forecast(horizon)
        
        # Compute metrics on last 4 quarters
        h = min(4, len(nat)//4)
        train = nat.iloc[:-h]
        test = nat.iloc[-h:]
        
        model_bt = ExponentialSmoothing(train, trend='add', seasonal=None, initialization_method='estimated')
        fit_bt = model_bt.fit(optimized=True)
        forecast_test = fit_bt.forecast(h)
        
        mae = mean_absolute_error(test, forecast_test)
        rmse = sqrt(mean_squared_error(test, forecast_test))
        
        def mape(a, f):
            a = np.array(a)
            f = np.array(f)
            return np.mean(np.abs((a - f) / np.where(a==0, 1, a))) * 100
        
        mape_val = mape(test, forecast_test)
        
        return {
            "historical": [{"date": str(d), "value": int(v)} for d, v in nat.items()],
            "forecast": [{"date": str(d), "value": int(v)} for d, v in forecast.items()],
            "metrics": {
                "mae": round(mae, 2),
                "rmse": round(rmse, 2),
                "mape": round(mape_val, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export")
def export_data(format: str = Query("csv", pattern="^(csv|json)$")):
    """Export data in CSV or JSON format"""
    try:
        agg_trans, _ = load_data()
        
        if format == "csv":
            stream = io.StringIO()
            agg_trans.to_csv(stream, index=False)
            response = StreamingResponse(
                iter([stream.getvalue()]),
                media_type="text/csv"
            )
            response.headers["Content-Disposition"] = "attachment; filename=upi_data.csv"
            return response
        else:
            return {"data": agg_trans.to_dict('records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/timeseries")
def get_timeseries(
    state: str = None,
    transaction_type: str = None,
    granularity: str = Query("Q", pattern="^(M|Q|Y)$")
):
    """Get time series data with optional filters"""
    try:
        agg_trans, _ = load_data()
        
        df = agg_trans.copy()
        if state:
            df = df[df['State'] == state]
        if transaction_type and 'Transaction_type' in df.columns:
            df = df[df['Transaction_type'] == transaction_type]
        
        ts = df.groupby('date')['Transaction_count'].sum().sort_index().resample(granularity).sum()
        
        return {
            "timeseries": [{"date": str(d), "value": int(v)} for d, v in ts.items()]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
