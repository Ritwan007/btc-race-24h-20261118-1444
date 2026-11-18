# Findings — btc-race-24h-20261118-1444 (dev window 2026-11-17 14:44 UTC → 2026-11-18 14:44 UTC, 1,440 bars)

## Window character
- BTC 65,083 → 63,261 (−281 bps gross buy-and-hold). 1-minute return sd 6.68 bps (quiet tape).
- Shape: sharp fall hours 0–2 (−215 bps), recovery hours 5–8 (+190 bps), slow drift down hours 9–23, last hour −108 bps. Range 63,076–65,190.
- Full-size round trip costs ~26 bps (4 bps fee + 2 bps slippage + ~10 bps impact each way at ~$1M pool depth).

## Method
- Screening simulator with the harness's exact integer fill math, validated to the
  micro-USDC against grade-local: buy-and-hold −31.633698 (fees 0.787502) and
  EMA-cross −148.174061 (80 trades) both reproduced exactly.
- The real bot was then verified through a protocol driver (NDJSON hello/batch/done,
  same fill math): two runs, reply streams byte-identical, PnL +17.664496.

## Measured variants (net PnL after all fees, full size $1,000)
| Family | Best | Typical |
|---|---|---|
| Buy-and-hold (grade-local) | −31.63 | — |
| Momentum (grade-local) | −23.87 | — |
| RSI-Bollinger (grade-local) | −39.92 | — |
| ADX-momentum (grade-local) | −75.57 | — |
| EMA-cross (grade-local) | −148.17 | — |
| Mean reversion vs SMA (W60–240, T30–80) | −3.85 | −5…−28 |
| MR + stop-loss | −12.51 | −15…−40 |
| MR + turn-up confirmation | +9.51 (1 trade) | −20…+9 |
| RSI(14/30) | −0.41 | −10…−41 |
| Dip-buy + take-profit (no confirmation) | +3.13 | −1…−30 |
| **Deep-dip bounce swing (chosen)** | **+17.66** | **median +11.45** |

## Chosen rule (main.py)
- Arm when close ≥ 200 bps below the trailing 120-bar high; buy full cash when
  close recovers ≥ 40 bps from the trailing low since arming.
- Sell all at +200 bps over the buy fill price, −90 bps trailing stop from the
  peak close, or −150 bps hard stop. max_slippage_bps 100.
- Dev trade: buy fill bar 136 @ $63,764.02, sell fill bar 506 @ $64,942.33.
  Net +$17.66, fees $0.81, max drawdown 0.65%, 1 round trip.

## Robustness (the honest caveat)
- The dev PnL is a single round trip: it captures the window's one big swing
  (hours 5–8 recovery). It is NOT a knife-edge parameter cell: a 324-variant
  grid around the rule gives 284 variants > +$5 and 314 > $0, median +$11.45,
  and the top plateau (+17.66) is flat across dip 160–220 bps, trailing stop
  80–110 bps, take-profit 200 bps. The rule fires on the swing, not the numbers.
- Halves: first half contains the trade (+17); second half flat (+0.00, no trades)
  — no second-half loss props the result up, but no second trade either.
- Race-window risk: the bot trades only when a ≥200 bps dip + 40 bps recovery
  occurs. If the race window has no such swing it trades 0 times (PnL 0, no prize);
  if it has one, expected outcome is a swing capture of roughly +$10–20. Every
  higher-frequency alternative measured loses money on this tape, so the
  selective swing is the best available entry. No variant was found that trades
  more often with positive expectancy.
- No parameter was tuned after seeing the bot's grade: the grid was screened in
  the simulator first; the bot's parameters are the plateau centre (H120 D200 R40
  P200 T90 L150). An earlier H180 build scored only +$5.63 in the driver and was
  discarded before any submission.
