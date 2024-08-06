
![ichimoku cloud plot](img/ichimoku_live.png)

This Python script visualizes the Ichimoku Cloud indicator using both real-time and historical market data. The Ichimoku Cloud is a comprehensive technical analysis tool that provides information about support and resistance levels, trend direction, and momentum in financial markets.

## Prerequisites

Ensure you have the requirements file installed.

To install the libraries listed in the `requirements.txt` file, use the following command:

```sh
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in your project directory and add your `CLIENT_ID` and `CLIENT_SECRET`:

```env
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
```

These variables enable secure access to market data from the [HSTRADER](https://staging.hstrader.com/login) platform.

**Reminder:**
Your unique `CLIENT_ID` and `CLIENT_SECRET` can be obtained from your personal account on the platform. Ensure you keep them confidential to protect your data.

## Usage

1. Import the necessary modules and load your environment variables.
2. Initialize the HsTrader client with your credentials.
3. Retrieve the symbol for the desired asset (e.g., `Bitcoin`).
4. Fetch historical market data at the specified resolution.
5. Calculate the Ichimoku Cloud components based on historical data.
6. Set up real-time data subscription to continuously update the Ichimoku Cloud indicators.
7. Visualize the data using Plotly to create an interactive candlestick chart with Ichimoku Cloud overlays.
### Ichimoku Cloud Components

The Ichimoku Cloud consists of five main components:

1. **Tenkan-sen (Conversion Line):**
   - Calculation: (9-period high + 9-period low) / 2
   - Purpose: Identifies short-term price momentum.

2. **Kijun-sen (Base Line):**
   - Calculation: (26-period high + 26-period low) / 2
   - Purpose: Shows medium-term price momentum.

3. **Senkou Span A (Leading Span A):**
   - Calculation: (Tenkan-sen + Kijun-sen) / 2 (shifted 26 periods forward)
   - Purpose: Forms one of the boundaries of the cloud.

4. **Senkou Span B (Leading Span B):**
   - Calculation: (52-period high + 52-period low) / 2 (shifted 26 periods forward)
   - Purpose: Forms the other boundary of the cloud.

5. **Chikou Span (Lagging Span):**
   - Calculation: Close price shifted 26 periods back
   - Purpose: Confirms the trend and signals potential buy/sell opportunities.

### Why Use the Ichimoku Cloud?

1. **Trend Identification:**
   - Helps traders identify the direction and strength of the trend.

2. **Support and Resistance:**
   - The cloud provides potential support and resistance levels.

3. **Comprehensive Indicator:**
   - Offers a complete view of market conditions, including trend, momentum, and potential reversals.

4. **Visual Clarity:**
   - Easy to interpret and apply to various trading strategies.

## Visualization

The final visualization is an interactive chart that displays:

- Candlestick representation of price movements.
- Ichimoku Cloud components including Tenkan-sen, Kijun-sen, Senkou Span A, Senkou Span B, and Chikou Span.
- Dynamic filled areas between Senkou Span A and Senkou Span B, color-coded to indicate potential buy or sell signals.

## Running the Script

To run the script, simply execute it in your Python environment. The script initializes a Dash app to display real-time updates of the Ichimoku Cloud indicator.

```python
if __name__ == '__main__':
    dash_thread = threading.Thread(target=run_dash)
    dash_thread.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_client())
```

## Conclusion

The Ichimoku Cloud is a versatile tool for technical analysis, providing a comprehensive view of market trends and potential support/resistance levels. Its ability to offer insight into both short-term and long-term market conditions makes it a valuable asset for traders.
