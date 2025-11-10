import streamlit as st
import pandas as pd
import os
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt
import plotly.graph_objects as go
import io


st.set_page_config(page_title='UPI Forecast', layout='wide')
st.title('UPI Digital Payments — Quarterly Forecast')

DATA_DIR = os.path.join('.', 'data')
path = os.path.join(DATA_DIR, 'agg_trans.csv')

if not os.path.exists(path):
    st.error('agg_trans.csv not found in the `data/` folder. Please add the file and reload.')
    st.stop()

df = pd.read_csv(path)
st.sidebar.header('Controls')
st.sidebar.markdown('Quick filters and forecast controls')

# show tabs for data and analyses
tabs = st.tabs(['Data sample', 'By Transaction Type', 'By State', 'Forecast'])

with tabs[0]:
    st.subheader('Data sample')
    st.dataframe(df.head(50))
    st.download_button('Download sample CSV', data=df.head(200).to_csv(index=False).encode(), file_name='agg_trans_sample.csv')

    st.markdown('Data types and missing values:')
    st.dataframe(pd.DataFrame({'dtype': df.dtypes.astype(str), 'missing': df.isna().sum()}))

    if 'Year' in df.columns and 'Quarter' in df.columns:
        df['date'] = df.apply(lambda r: pd.Timestamp(year=int(r['Year']), month={1:3,2:6,3:9,4:12}.get(int(r['Quarter']),12), day=1) + pd.offsets.MonthEnd(0), axis=1)
    else:
        st.warning('Year/Quarter columns not found; some analyses may not be available')

with tabs[1]:
    st.subheader('Analysis by Transaction Type')
    if 'Transaction_type' not in df.columns:
        st.warning('No Transaction_type column in data')
    else:
        # prepare pivot
        grp = df.groupby(['date', 'Transaction_type'], as_index=False).agg({'Transaction_count':'sum', 'Transaction_amount':'sum'})
        pivot_count = grp.pivot(index='date', columns='Transaction_type', values='Transaction_count').fillna(0)
        top_types = pivot_count.sum().sort_values(ascending=False).head(10).index.tolist()

        sel_type = st.selectbox('Select Transaction Type (or All)', ['All'] + top_types)
        if sel_type == 'All':
            fig = go.Figure()
            for t in top_types:
                fig.add_trace(go.Scatter(x=pivot_count.index, y=pivot_count[t], mode='lines+markers', name=str(t)))
            fig.update_layout(title='Quarterly Transaction Count - Top Types', height=450)
            st.plotly_chart(fig, use_container_width=True)
        else:
            series = pivot_count[sel_type]
            fig = go.Figure(go.Scatter(x=series.index, y=series.values, mode='lines+markers'))
            fig.update_layout(title=f'Quarterly Transaction Count - {sel_type}', height=450)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('Top states for selected type')
        latest_date = df['date'].max() if 'date' in df.columns else None
        if sel_type == 'All':
            st.info('Select a single transaction type to see top states')
        else:
            sub = df[df['Transaction_type'] == sel_type]
            overall = sub.groupby('State', as_index=False)['Transaction_count'].sum().sort_values('Transaction_count', ascending=False).head(10)
            fig2 = go.Figure(go.Bar(x=overall['State'].astype(str), y=overall['Transaction_count']))
            fig2.update_layout(title=f'Top 10 States by {sel_type} (overall)', height=400)
            st.plotly_chart(fig2, use_container_width=True)
            if pd.notna(latest_date):
                latest_sub = sub[sub['date'] == latest_date]
                if not latest_sub.empty:
                    latest_states = latest_sub.groupby('State', as_index=False)['Transaction_count'].sum().sort_values('Transaction_count', ascending=False).head(10)
                    fig3 = go.Figure(go.Bar(x=latest_states['State'].astype(str), y=latest_states['Transaction_count']))
                    fig3.update_layout(title=f'Top 10 States by {sel_type} (latest quarter)', height=400)
                    st.plotly_chart(fig3, use_container_width=True)

with tabs[2]:
    st.subheader('Analysis by State')
    if 'State' not in df.columns:
        st.warning('No State column in data')
    else:
        states = sorted(df['State'].dropna().unique().tolist())
        sel_state = st.selectbox('Select State', states)
        st.markdown(f'### Trends for {sel_state}')
        sub = df[df['State'] == sel_state]
        if 'Transaction_type' in sub.columns:
            pivot_state = sub.groupby(['date','Transaction_type'], as_index=False)['Transaction_count'].sum().pivot(index='date', columns='Transaction_type', values='Transaction_count').fillna(0)
            top_types_state = pivot_state.sum().sort_values(ascending=False).head(8).index.tolist()
            fig = go.Figure()
            for t in top_types_state:
                fig.add_trace(go.Scatter(x=pivot_state.index, y=pivot_state[t], mode='lines+markers', name=str(t)))
            fig.update_layout(title=f'Transaction types over time in {sel_state}', height=450)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('Top transaction types (overall)')
            overall_types = sub.groupby('Transaction_type', as_index=False)['Transaction_count'].sum().sort_values('Transaction_count', ascending=False).head(10)
            fig2 = go.Figure(go.Bar(x=overall_types['Transaction_type'].astype(str), y=overall_types['Transaction_count']))
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info('No Transaction_type column available to split trends by type')

with tabs[3]:
    st.subheader('Forecast')
    st.sidebar.subheader('Forecast controls')
    model_choice = st.sidebar.selectbox('Model', ['Naive', 'Holt-Winters'])
    horizon = st.sidebar.slider('Forecast horizon (quarters)', 1, 12, 4)

    # prepare national time series
    if 'date' in df.columns:
        nat = df.groupby('date', as_index=True)['Transaction_count'].sum().sort_index().resample('Q').sum()
    else:
        st.error('No date column to build national series')
        nat = pd.Series(dtype=float)

    if len(nat) > 0:
        st.line_chart(nat)
        h = min(4, max(1, len(nat)//4))
        train = nat.iloc[:-h]
        test = nat.iloc[-h:]
        if model_choice == 'Naive':
            forecast_test = np.repeat(train.iloc[-1], h)
        else:
            model_bt = ExponentialSmoothing(train, trend='add', seasonal=None, initialization_method='estimated')
            fit_bt = model_bt.fit(optimized=True)
            forecast_test = fit_bt.forecast(h)

        mae = mean_absolute_error(test, forecast_test)
        rmse = sqrt(mean_squared_error(test, forecast_test))
        def mape(a,f):
            a = np.array(a); f = np.array(f)
            return np.mean(np.abs((a-f)/np.where(a==0,1,a))) * 100
        mapep = mape(test, forecast_test)
        st.write('Backtest MAE:', round(mae,2), 'RMSE:', round(rmse,2), 'MAPE:', round(mapep,2))

        # full forecast
        if model_choice == 'Naive':
            fc_vals = np.repeat(nat.iloc[-1], horizon)
            idx = pd.date_range(start=nat.index[-1] + pd.offsets.MonthEnd(3), periods=horizon, freq='Q')
            fc_series = pd.Series(fc_vals, index=idx)
        else:
            model_full = ExponentialSmoothing(nat, trend='add', seasonal=None, initialization_method='estimated')
            fit_full = model_full.fit(optimized=True)
            fc_series = fit_full.forecast(horizon)

        figf = go.Figure()
        figf.add_trace(go.Scatter(x=nat.index, y=nat.values, mode='lines+markers', name='Historical'))
        figf.add_trace(go.Scatter(x=fc_series.index, y=fc_series.values, mode='lines+markers', name='Forecast'))
        st.plotly_chart(figf, use_container_width=True)

        csv_buffer = io.StringIO(); pd.DataFrame({'date': fc_series.index, 'forecast': fc_series.values}).to_csv(csv_buffer, index=False)
        st.download_button('Download forecast CSV', data=csv_buffer.getvalue().encode(), file_name='upi_forecast.csv', mime='text/csv')

    else:
        st.info('Not enough data to forecast')
