import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from datetime import datetime, timedelta
import os
from hstrader import HsTrader
from hstrader.models import Tick, Event, Resolution
from dotenv import load_dotenv
import logging
import asyncio
import threading

# Enable logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Get the CLIENT_ID and CLIENT_SECRET from the environment variables
id = os.getenv('CLIENT_ID')
secret = os.getenv('CLIENT_SECRET')

# Initialize the HsTrader client with the client ID and secret
client = HsTrader(id, secret)

symbol = client.get_symbol('Bitcoin')
data = client.get_market_history(symbol=symbol.id, resolution=Resolution.M1)

# Create a DataFrame from the retrieved data
df = pd.DataFrame([bar.model_dump() for bar in data])
df['time'] = pd.to_datetime(df['time'])
df.set_index('time', inplace=True)

# Ichimoku Cloud calculations
def calculate_ichimoku(df):
    high_9 = df['high'].rolling(window=9).max()
    low_9 = df['low'].rolling(window=9).min()
    df['tenkan_sen'] = (high_9 + low_9) / 2

    high_26 = df['high'].rolling(window=26).max()
    low_26 = df['low'].rolling(window=26).min()
    df['kijun_sen'] = (high_26 + low_26) / 2

    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    high_52 = df['high'].rolling(window=52).max()
    low_52 = df['low'].rolling(window=52).min()
    df['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)

    df['chikou_span'] = df['close'].shift(-26)
    return df

df = calculate_ichimoku(df)

# Create a Figure
fig = go.Figure()

candlestick = go.Candlestick(
    x=df.index, open=df['open'], high=df['high'].shift(-26), low=df['low'].shift(-26), close=df['close'].shift(-26), name='Candlestick'
)
fig.add_trace(candlestick)

# Add Ichimoku Cloud traces
fig.add_trace(go.Scatter(x=df.index, y=df['senkou_span_a'], mode='lines', name='Senkou Span A'))
fig.add_trace(go.Scatter(x=df.index, y=df['senkou_span_b'], mode='lines', name='Senkou Span B'))

# Function to add the filled area with dynamic colors
def add_dynamic_filled_areas(fig, df):
    prev_fill_color = None
    x_segment = []
    y_segment_a = []
    y_segment_b = []
    for i in range(len(df)):
        fill_color = 'rgba(0, 250, 0, 0.4)' if df['senkou_span_a'].iloc[i] > df['senkou_span_b'].iloc[i] else 'rgba(255, 0, 0, 0.4)'
        if fill_color != prev_fill_color and prev_fill_color is not None:
            # Add a trace for the previous segment
            fig.add_trace(go.Scatter(
                x=x_segment + x_segment[::-1],
                y=y_segment_a + y_segment_b[::-1],
                fill='toself',
                fillcolor=prev_fill_color,
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False
            ))
            x_segment = []
            y_segment_a = []
            y_segment_b = []
        x_segment.append(df.index[i])
        y_segment_a.append(df['senkou_span_a'].iloc[i])
        y_segment_b.append(df['senkou_span_b'].iloc[i])
        prev_fill_color = fill_color

    # Add the last segment
    if x_segment:
        fig.add_trace(go.Scatter(
            x=x_segment + x_segment[::-1],
            y=y_segment_a + y_segment_b[::-1],
            fill='toself',
            fillcolor=prev_fill_color,
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False
        ))

add_dynamic_filled_areas(fig, df.shift(26))

# Dash app setup
app = Dash(__name__)
app.layout = html.Div([
    dcc.Graph(id='live-update-graph', figure=fig),
    dcc.Interval(id='Interval', interval=1 * 1000, n_intervals=0)
])

CANDLE_INTERVAL = timedelta(minutes=1)
data = {
    'x': list(df.index),
    'open': list(df['open']),
    'high': list(df['high']),
    'low': list(df['low']),
    'close': list(df['close'])
}

@client.subscribe(Event.MARKET)
async def on_market(tick: Tick):
    global data, df

    if tick.symbol_id == symbol.id:
        tick_time = pd.to_datetime(tick.time)
        if not data['x']:
            data['x'].append(tick_time)
            data['open'].append(data['close'][-1])
            data['high'].append(tick.bid)
            data['low'].append(tick.bid)
            data['close'].append(tick.bid)
        elif tick_time >= data['x'][-1] + CANDLE_INTERVAL:
            data['x'].append(tick_time)
            data['open'].append(data['close'][-1])
            data['high'].append(tick.bid)
            data['low'].append(tick.bid)
            data['close'].append(tick.bid)
        else:
            data['low'][-1] = min(tick.bid, data['low'][-1])
            data['high'][-1] = max(tick.bid, data['high'][-1])
            data['close'][-1] = tick.bid

        # Update DataFrame with the latest tick data
        df = pd.DataFrame({
            'time': data['x'],
            'open': data['open'],
            'high': data['high'],
            'low': data['low'],
            'close': data['close']
        }).set_index('time')
        
        # Recalculate Ichimoku Cloud
        df = calculate_ichimoku(df)

@app.callback(Output('live-update-graph', 'figure'), Input('Interval', 'n_intervals'))
def update_graph_live(n):
    # Extend DataFrame to include future dates for plotting
    future_dates = pd.date_range(start=df.index[-1], periods=27, freq='min')[1:]
    future_df = pd.DataFrame(index=future_dates)
    df_extended = pd.concat([df, future_df])

    new_fig = go.Figure()

    # Shift the data by -26
    shifted_data = pd.DataFrame({
        'x': data['x'],
        'open': data['open'],
        'high': data['high'],
        'low': data['low'],
        'close': data['close']
    }).shift(-26)

    # Add updated candlestick trace
    new_fig.add_trace(go.Candlestick(
        x=shifted_data['x'], open=shifted_data['open'], high=shifted_data['high'], low=shifted_data['low'], close=shifted_data['close'], name='Candlestick'
    ))

    # Add updated Ichimoku Cloud traces
    new_fig.add_trace(go.Scatter(x=df_extended.index, y=df_extended['senkou_span_a'].shift(26), mode='lines', name='Senkou Span A'))
    new_fig.add_trace(go.Scatter(x=df_extended.index, y=df_extended['senkou_span_b'].shift(26), mode='lines', name='Senkou Span B'))

    # Add dynamic filled areas
    add_dynamic_filled_areas(new_fig, df_extended.shift(26))

    # Add the rest of the Ichimoku Cloud components
    new_fig.add_trace(go.Scatter(x=df.index, y=df['tenkan_sen'], mode='lines', name='Tenkan-sen'))
    new_fig.add_trace(go.Scatter(x=df.index, y=df['kijun_sen'], mode='lines', name='Kijun-sen'))
    new_fig.add_trace(go.Scatter(x=df.index, y=df['chikou_span'], mode='lines', name='Chikou Span'))

    return new_fig

def run_dash():
    app.run_server(debug=False, use_reloader=False)

async def start_client():
    await client.start_async()

if __name__ == '__main__':
    dash_thread = threading.Thread(target=run_dash)
    dash_thread.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_client())
