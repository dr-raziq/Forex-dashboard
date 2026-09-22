import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

import forex

load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    pair = request.args.get("pair", "EUR/USD")
    if pair not in forex.PAIRS:
        pair = "EUR/USD"

    td_key = os.environ.get("TWELVE_DATA_KEY", "")
    ma_key = os.environ.get("MARKETAUX_KEY", "")

    result = None
    error = None

    if not td_key:
        error = "Set TWELVE_DATA_KEY in your .env file to load data."
    else:
        try:
            result = forex.analyze(pair, td_key, ma_key)
        except Exception as exc:
            error = str(exc)

    return render_template(
        "index.html",
        pairs=forex.PAIRS,
        pair=pair,
        result=result,
        error=error,
        has_news_key=bool(ma_key),
        format_price=forex.format_price,
    )


if __name__ == "__main__":
    app.run(debug=True)