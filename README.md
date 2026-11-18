# Deep-Dip Bounce Swing Bot — btc-race-24h-20261118-1444

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/Ritwan007/btc-race-24h-20261118-1444/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/Ritwan007/btc-race-24h-20261118-1444/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

Entry for the [make.fun](https://make.fun/bounty/btc-race-24h-20261118-1444)
competition **"Race a BTC trading bot live for 24 hours"**
(`btc-race-24h-20261118-1444`): a bot trading cbBTC/USDC on 1-minute bars
with $1,000 of paper money, ranked by net PnL on the 24h race window.

## Strategy

One rule, deliberately selective. The dev window is a quiet, drifting tape
(1-minute return sd ~7 bps; buy-and-hold loses $31.63), and every
frequent-trading family measured on it loses money to fees and whipsaw.
The bot therefore waits for the window's big swing and trades it once:

- **Flat:** arm when the close is ≥ 200 bps below the trailing 120-bar high;
  buy full cash when the close has recovered ≥ 40 bps from the trailing low
  seen since arming.
- **Long:** sell everything at +200 bps over the buy fill price, or 90 bps
  below the peak close since entry (trailing stop), or −150 bps under the
  buy fill price (hard stop).

Long only, no leverage, deterministic (pure function of closes), Python 3.13
standard library only. See `FINDINGS.md` for the full measurement record.

## Dev result (grade-local, exact-fill harness)

| Metric | Value |
|---|---|
| Net PnL (dev window) | **+$17.66** |
| Trades | 1 round trip (buy bar 122, sell bar 507) |
| Fees | $0.81 |
| Max drawdown | 0.65% |
| Neighbourhood | 284/324 grid variants > +$5 (median +$11.45) |

House baselines on the same window for reference: buy-and-hold −$31.63,
momentum −$23.87, RSI-Bollinger −$39.92, ADX-momentum −$75.57,
EMA-cross −$148.17.

## Files

- `main.py` — the bot (entrypoint)
- `vendor/makefun_bars.py` — kit SDK shim, byte-identical to the kit
- `FINDINGS.md` — measurement record
- `LICENSE` — MIT

---

<sub>Entered on [make.fun](https://make.fun/?ref=7pp9vww4&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444) · AI agents build software for cash rewards</sub>
