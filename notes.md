# Notes on Approach — Equity Data Analysis

## Approach
1. Loaded `prices.csv`, parsed dates, and sorted by ticker/date.
2. For each ticker, took the close price on X (2021-06-01) and Y (2021-10-13)
   and computed simple return: `(close_Y - close_X) / close_X`.
3. Computed the 30-day average trading volume ending on Y.
4. Ranked all 100 tickers by performance and took the top 5.
5. Plotted close price for the top performers over the window, and produced a PDF
   with company name, ISIN, performance, and 30-day average volume for each.

## Assumptions / judgement calls
- **X and Y are present in the dataset for all tickers.** Where the endpoint row
  existed but the price fields were null, I used the most recent available close
  on or before that date so the point-to-point return could still be computed.
- **Missing endpoint values (ADOB):** ADOB has a row on 2021-10-13, but its
  OHLCV fields are null. Rather than dropping the ticker from the ranking, I used
  the most recent available close on or before Y. This is a judgement call; an
  alternative would be to exclude ADOB because its end-of-window price is not
  directly observed on Y.
- **"30-day average volume"** is ambiguous between calendar days and trading
  sessions. I used a 30-calendar-day window ending on Y, i.e. all trading rows
  with date in `(Y-30d, Y]`. If needed, this could also be defined as the most
  recent 30 trading sessions instead.
- **Ranking metric:** simple point-to-point return from close_X to close_Y.
  I used this because the task asks for performance between two fixed dates.

## What I noticed about the data (Task 5)
This is dummy data, but it contains a few issues worth flagging explicitly:

1. **General Electric (GENE) shows a ~940% return driven by a sharp price jump
   on 2021-08-02.** This may indicate a potential anomaly, an unadjusted
   corporate action, or some other issue in the dataset. I kept it in the
   literal ranking, but also produced a review-adjusted ranking that excludes
   names flagged by a simple anomaly screen.
2. **Ten other tickers** (AMAZ, APPL, ATT, CISC, COCA, EXXO, FORD, INTE,
   MICR, PFIZ) show very large one-day jumps that reverse the next session.
   These do not affect the X-to-Y endpoint return unless they occur on X or Y,
   but they are still worth flagging for review because they could distort other
   analyses such as rolling returns or volatility.
3. **NETF (Netflix) has a block of July dates where rows are present but OHLCV
   values are null** (2021-07-01 through 2021-07-30). This does not affect the
   X-to-Y return directly, but it could affect rolling metrics if used elsewhere.
4. **ADOB has null OHLCV values on Y** exactly at the end-of-window boundary,
   so I used the nearest prior valid close as described above.
5. **NOKI's volume is consistently in the thousands all year**, much lower than
   most of the other names. It is internally consistent, but its scale looks
   unusual relative to the rest of the dataset and is worth a sanity check if
   the data were used for liquidity-based decisions.
6. No negative prices, no `high < low` rows, and no duplicate `(date, isin)`
   rows were found. Every ticker has 261 weekday rows in 2021 (Mon–Fri calendar
   coverage), although some rows contain null OHLCV values.

## Files
- `analysis.py` — full analysis code
- `make_pdf.py` — builds the deliverable PDF
- `top5_naive.csv` / `top5_clean.csv` — literal and review-adjusted rankings
- `top5_price_history.png` — chart based on the review-adjusted top 5
- `equity_analysis_himanshi_agrawal.pdf` — final deliverable