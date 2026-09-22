import requests

PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "EUR/GBP",
    "AUD/USD",
    "USD/CHF",
    "USD/CAD",
    "NZD/USD",
]

TWELVE_DATA_URL = "https://api.twelvedata.com/time_series"
MARKETAUX_URL = "https://api.marketaux.com/v1/news/all"


def format_price(pair, value):
    if value is None:
        return "-"
    if "JPY" in pair:
        return f"{value:.3f}"
    return f"{value:.5f}"


def get_candles(pair, api_key, interval="15min", outputsize=60):
    params = {
        "symbol": pair,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": api_key,
    }
    resp = requests.get(TWELVE_DATA_URL, params=params, timeout=15)
    data = resp.json()

    if data.get("status") == "error" or "values" not in data:
        raise RuntimeError(data.get("message", "Price request failed"))

    rows = list(reversed(data["values"]))
    return [{"datetime": r["datetime"], "close": float(r["close"])} for r in rows]


def get_news(pair, api_key, limit=6):
    base, quote = pair.split("/")
    params = {
        "search": f"{base} OR {quote}",
        "language": "en",
        "limit": limit,
        "api_token": api_key,
    }
    resp = requests.get(MARKETAUX_URL, params=params, timeout=15)
    data = resp.json()
    return data.get("data", [])


def rolling_sma(values, period):
    out = []
    for i in range(len(values)):
        if i + 1 < period:
            out.append(None)
        else:
            window = values[i + 1 - period : i + 1]
            out.append(sum(window) / period)
    return out


def last_rsi(values, period=14):
    if len(values) < period + 1:
        return None

    gains = 0.0
    losses = 0.0
    for i in range(len(values) - period, len(values)):
        diff = values[i] - values[i - 1]
        if diff >= 0:
            gains += diff
        else:
            losses -= diff

    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def analyze(pair, td_key, ma_key=None):
    candles = get_candles(pair, td_key)
    closes = [c["close"] for c in candles]

    sma20_series = rolling_sma(closes, 20)
    sma50_series = rolling_sma(closes, 50)

    chart = []
    for i, candle in enumerate(candles):
        chart.append(
            {
                "time": candle["datetime"][5:16],
                "close": closes[i],
                "sma20": sma20_series[i],
                "sma50": sma50_series[i],
            }
        )

    current_price = closes[-1] if closes else None
    sma20 = sma20_series[-1] if sma20_series else None
    sma50 = sma50_series[-1] if sma50_series else None
    rsi14 = last_rsi(closes, 14)

    tech_signal = "neutral"
    if sma20 is not None and sma50 is not None:
        if sma20 > sma50 and (rsi14 is None or rsi14 < 70):
            tech_signal = "bullish"
        elif sma20 < sma50 and (rsi14 is None or rsi14 > 30):
            tech_signal = "bearish"

    news = []
    avg_sentiment = None
    sentiment_count = 0

    if ma_key:
        try:
            articles = get_news(pair, ma_key)
        except Exception:
            articles = []

        all_scores = []
        for article in articles:
            scores = [
                e.get("sentiment_score")
                for e in article.get("entities", [])
                if isinstance(e.get("sentiment_score"), (int, float))
            ]

            if scores:
                article_avg = sum(scores) / len(scores)
            else:
                article_avg = None

            if article_avg is None:
                tag = "neutral"
            elif article_avg > 0.15:
                tag = "bullish"
            elif article_avg < -0.15:
                tag = "bearish"
            else:
                tag = "neutral"

            all_scores.extend(scores)
            news.append(
                {
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "tag": tag,
                }
            )

        sentiment_count = len(all_scores)
        if all_scores:
            avg_sentiment = sum(all_scores) / len(all_scores)

    news_signal = "neutral"
    if avg_sentiment is not None:
        if avg_sentiment > 0.15:
            news_signal = "bullish"
        elif avg_sentiment < -0.15:
            news_signal = "bearish"

    if tech_signal == "bullish" and news_signal != "bearish":
        composite = "BUY"
    elif tech_signal == "bearish" and news_signal != "bullish":
        composite = "SELL"
    else:
        composite = "HOLD"

    pip = 0.01 if "JPY" in pair else 0.0001
    buy_target = current_price + 20 * pip if current_price is not None else None
    sell_target = current_price - 20 * pip if current_price is not None else None

    return {
        "pair": pair,
        "price": current_price,
        "sma20": sma20,
        "sma50": sma50,
        "rsi14": rsi14,
        "tech_signal": tech_signal,
        "news": news,
        "news_signal": news_signal,
        "avg_sentiment": avg_sentiment,
        "sentiment_count": sentiment_count,
        "composite": composite,
        "buy_target": buy_target,
        "sell_target": sell_target,
        "chart": chart,
    }