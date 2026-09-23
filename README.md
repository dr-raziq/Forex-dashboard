Forex Dashboard

A small Flask web app that shows a simple BUY / SELL / HOLD signal for a forex pair. It pulls recent price data from Twelve Data, calculates a few technical indicators, optionally blends in news sentiment from MarketAux, and shows the result on a single page.

1.	Overview

The app is meant to give a quick, plain-language read on a currency pair without hiding how the call was made. Every number that feeds the signal is shown on the page, so you can see exactly why it says BUY, SELL or HOLD.
It is a single-page tool: pick a pair, the page reloads, and you see the current price, a chart, the indicators, the news (if enabled), and the combined signal with 20-pip buy and sell targets.

2.	Objectives

        •	Provide a simple, transparent trading signal instead of a black box.
        •	Keep the code small enough to read and modify in one sitting.
        •	Work with only free API tiers.
        •	Show the reasoning behind every signal on the page itself.
        •	Serve as a starting point, not a finished trading system.

3.	What It Does

        •	Fetches the last 60 15-minute candles for the selected pair.
        •	Calculates SMA20, SMA50 and RSI14 from those candles.
        •	If a MarketAux key is set, fetches recent news and averages sentiment.
        •	Combines the technical and news sides into one BUY / SELL / HOLD call.
        •	Shows 20-pip buy and sell targets from the current price.
        •	Draws a price, SMA20 and SMA50 line chart.

4.	Key Features

        •	Eight major forex pairs, selectable from a dropdown.
        •	15-minute timeframe.
        •	SMA20, SMA50 and RSI14 indicators.
        •	Optional news sentiment panel via MarketAux.
        •	Combined signal with the technical and news reasoning shown below it.
        •	20-pip buy and sell targets calculated from the current price.
        •	Line chart of price, SMA20 and SMA50.
        •	API keys stored in a local .env file, never committed to git.

5.	How It Works
        1.	You pick a pair from the dropdown and the page reloads with that pair.
        2.	app.py reads your API keys from the .env file.
        3.	forex.py fetches 15-minute candles from Twelve Data.
        4.	It calculates SMA20, SMA50 and RSI14 from the closing prices.
        5.	If a MarketAux key is present, it fetches recent news and averages the sentiment scores across all tagged entities.
        6.	The technical side and the news side are each labelled bullish, bearish or neutral.
        7.	The two are combined into a single BUY / SELL / HOLD call.
        8.	The result is passed to the HTML template and rendered on the page.
6.	Signal Rules

    Technical:
        •	Bullish if SMA20 is above SMA50 and RSI14 is below 70 (or RSI is unavailable).
        •	Bearish if SMA20 is below SMA50 and RSI14 is above 30 (or RSI is unavailable).
        •	Neutral otherwise.

    News (only when a MarketAux key is set):
        •	Bullish if average sentiment is above 0.15.
        •	Bearish if average sentiment is below -0.15.
        •	Neutral otherwise.

    Combined:
        •	BUY if technical is bullish and news is not bearish.
        •	SELL if technical is bearish and news is not bullish.
        •	HOLD otherwise.

7.	Project Structure

    Forex-dashboard
    |
    |__ app.py (Flask routes)
    |
    |__ forex.py (API calls and indicator calculations)
    |
    |__ templates/
    |           |__ index.html (The page)
    |
    |__ requirements.txt (Dependencies)
    |
    |__ .env.example (Example environment file)
    |
    |__ .gitignore
    |
    |__ README.md

8.	Requirements

        •	Python 3.9 or newer
        •	A free Twelve Data API key: https://twelvedata.com/register
        •	A free MarketAux API key: https://www.marketaux.com

9.	 How To Run

    Clone the repository:
        git clone https://github.com/<your-username>/forex-dashboard.git
        cd forex-dashboard

    Create and activate a virtual environment:
        python -m venv venv
        source venv/bin/activate # Windows: venv\Scripts\activate

    Install dependencies:
        pip install -r requirements.txt

    Copy the example environment file and add your keys:
        cp .env.example .env

    Then edit .env:
        TWELVE_DATA_KEY=your_key_here
        MARKETAUX_KEY=your_key_here
    MARKETAUX_KEY is optional. Without it the news panel stays empty and the signal uses only the technical side.

    Start the app:
        python app.py

    Open http://127.0.0.1:5000 in a browser.

10.	Notes

        •	The Twelve Data free tier is roughly 800 requests per day and 8 per minute. Avoid refreshing too quickly.
        •	The signal is a simple rule, not a tested trading strategy. It is not financial advice.
        •	Built and tested against the free tiers of both providers. If a provider changes its response format, a small fix may be needed.

11.	Future Improvements

        •	Add more timeframes (1h, 4h, 1d).
        •	Add more pairs.
        •	Cache API responses to reduce request usage.
        •	Add a simple backtest of the signal on historical data.
        •	Add a second technical indicator (for example MACD).
        •	Let the user save API keys through a settings page instead of .env.
        •	Add unit tests for the indicator calculations.
        •	Add a Dockerfile for easier setup.


