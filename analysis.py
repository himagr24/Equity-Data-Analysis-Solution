"""
WK Vermögensverwaltung — Coding Exercise: Equity Data Analysis
Author: Himanshi Agrawal

Approach & assumptions are documented inline where judgement calls were made.
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

DATA_PATH = "prices.csv"
X = "2021-06-01"
Y = "2021-10-13"
N_TOP = 5

df = pd.read_csv(DATA_PATH, parse_dates=["date"])
df = df.sort_values(["ticker", "date"]).reset_index(drop=True)

# ---------------------------------------------------------------------------
# 1. Data-quality observations
# ---------------------------------------------------------------------------
# a) ADOB has a row on Y (2021-10-13), but its OHLCV fields are null.
#    Assumption: use the most recent available close on or before Y so the
#    point-to-point return can still be computed. This keeps the name in the
#    ranking while making the fallback explicit.
#
# b) NETF has a block of dates in July where rows are present but OHLCV values
#    are null. Since this does not affect X or Y directly, no adjustment is
#    made for the return calculation. It is still worth flagging as a data-
#    quality issue because it could matter for rolling metrics.
#
# c) GENE shows a very large price step on 2021-08-02. That may indicate a
#    potential anomaly, an unadjusted corporate action, or some other issue in
#    the dummy dataset. I do not remove it from the literal ranking, but I do
#    produce an additional "reviewed" ranking excluding names flagged by a
#    simple anomaly screen.
#
# d) Several other tickers show extreme single-day jumps that immediately
#    reverse. These do not affect the X-to-Y endpoint return directly unless
#    they occur on X or Y, but they are still worth flagging for review.


def nearest_on_or_before(ticker_df: pd.DataFrame, target_date: str) -> pd.Series:

    #Return the latest row on or before target_date with a non-null close.

    sub = ticker_df[ticker_df["date"] <= pd.Timestamp(target_date)]
    sub = sub.dropna(subset=["close"])

    if sub.empty:
        raise ValueError(f"No valid close found on or before {target_date}.")

    return sub.iloc[-1]


records = []
for ticker, g in df.groupby("ticker"):
    row_x = nearest_on_or_before(g, X)
    row_y = nearest_on_or_before(g, Y)

    # Simple point-to-point return between the two requested dates.
    perf_pct = (row_y["close"] - row_x["close"]) / row_x["close"] * 100

    # "30-day average volume" is ambiguous, so this uses a 30-calendar-day
    # lookback ending on Y and averages the available trading rows in that
    # window.
    window = g[
        (g["date"] > pd.Timestamp(Y) - pd.Timedelta(days=30)) &
        (g["date"] <= pd.Timestamp(Y))
    ]
    avg_vol_30d = window["volume"].mean()

    records.append({
        "ticker": ticker,
        "isin": g["isin"].iloc[0],
        "name": g["name"].iloc[0],
        "close_x": row_x["close"],
        "close_x_date": row_x["date"].date(),
        "close_y": row_y["close"],
        "close_y_date": row_y["date"].date(),
        "perf_pct": perf_pct,
        "avg_vol_30d": avg_vol_30d,
    })

result = (
    pd.DataFrame(records)
    .sort_values("perf_pct", ascending=False)
    .reset_index(drop=True)
)

# ---------------------------------------------------------------------------
# 2. Simple anomaly screen
# ---------------------------------------------------------------------------
# This is a rule-of-thumb screen, not proof of bad data. A >50% single-day
# move is unusual enough in this dataset to warrant review, especially if it
# does not line up with other supporting evidence. These names are flagged for
# inspection, and I provide both the literal top 5 and a review-adjusted top 5.
df["day_ret"] = df.groupby("ticker")["close"].pct_change()
ANOMALY_THRESHOLD = 0.5
flagged_tickers = set(df.loc[df["day_ret"].abs() > ANOMALY_THRESHOLD, "ticker"])

result["flag"] = result["ticker"].apply(
    lambda t: "potential anomaly: >50% one-day move" if t in flagged_tickers else ""
)

# Literal answer to the prompt.
top5_naive = result.head(N_TOP).copy()

# Additional reviewed view excluding names flagged by the anomaly screen.
top5_reviewed = result[~result["ticker"].isin(flagged_tickers)].head(N_TOP).copy()

print("Top 5 (literal ranking from close_X to close_Y)")
print(top5_naive[["ticker", "name", "perf_pct", "avg_vol_30d", "flag"]].to_string(index=False))
print()

print("Top 5 (review-adjusted, excluding flagged anomalies)")
print(top5_reviewed[["ticker", "name", "perf_pct", "avg_vol_30d"]].to_string(index=False))

top5_naive.to_csv("top5_naive.csv", index=False)
top5_reviewed.to_csv("top5_clean.csv", index=False)

# ---------------------------------------------------------------------------
# 3. Plot price history
# ---------------------------------------------------------------------------
# I use the review-adjusted list for the plot so one extreme flagged name does
# not compress the scale and make the other lines unreadable. The literal top 5
# is still preserved in the CSV output above.
plot_tickers = top5_reviewed["ticker"].tolist()
window_df = df[
    (df["date"] >= X) &
    (df["date"] <= Y) &
    (df["ticker"].isin(plot_tickers))
]

fig, ax = plt.subplots(figsize=(9, 5.5))
for ticker in plot_tickers:
    tdf = window_df[window_df["ticker"] == ticker].sort_values("date")
    ax.plot(tdf["date"], tdf["close"], label=ticker, linewidth=1.8)

ax.set_title(f"Top {N_TOP} Performers: Close Price, {X} to {Y}")
ax.set_xlabel("Date")
ax.set_ylabel("Close Price")
ax.legend(title="Ticker", loc="upper left")
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f"))
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig("top5_price_history.png", dpi=150)

print("\nSaved plot: top5_price_history.png")