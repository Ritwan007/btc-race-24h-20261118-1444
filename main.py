# SPDX-License-Identifier: MIT
"""Deep-dip bounce swing bot for btc-race-24h-20261118-1444.

Trades cbBTC/USDC on 1-minute bars, long only, starting from $1,000 paper
money. One rule, deliberately selective: the dev window is a quiet, drifting
tape (1-minute return sd ~7 bps, buy-and-hold -31.6 USDC), and every
frequent-trading family measured on it loses money to fees and whipsaw
(EMA-cross -148, RSI-Bollinger -40, plain mean reversion -4..-28). The only
family that clears the gate is a deep-dip bounce swing: wait for a large
drawdown from the trailing high, buy only once the tape turns up off its
low, then ride the swing with a wide trailing stop. Across a 324-variant
grid around these parameters 284 variants score above +$5 (median +$11.45),
so the edge is the swing itself, not a tuned cell.

Rule, per batch (decisions fill at the NEXT bar's open):
  flat:  arm when close is >= 200 bps below the trailing 120-bar high;
         buy full cash when close has recovered >= 40 bps from the
         trailing low seen since arming.
  long:  sell everything when the close is >= 200 bps above the buy fill
         price, or >= 90 bps below the peak close since entry, or
         <= 150 bps below the buy fill price.
Position is read from the harness account each batch, so a rejected fill
simply leaves the bot flat and the rule re-arms; no order is ever sent
twice for the same decision. Deterministic: pure function of closes.
Standard library only.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"
LOOKBACK = 120          # bars of trailing high for the dip test
DIP_BPS = 200           # arm once close is this far below the trailing high
RECOVER_BPS = 40        # buy once close recovers this far above the trail low
TAKE_PROFIT_BPS = 200   # sell at this gain over the buy fill price
TRAIL_BPS = 90          # sell this far below the peak close since entry
STOP_BPS = 150          # sell at this loss under the buy fill price
MAX_SLIPPAGE_BPS = 100  # cap the move from the latest close at the fill


class SwingBot:
    """One deep-dip bounce swing at a time, full size."""

    def __init__(self):
        self.closes = []
        self.armed = False
        self.trail_low = None
        self.entry_price = None
        self.peak = None

    def _dip_bps(self, close, high):
        return (high - close) * 10000 // high

    def _rise_bps(self, close, low):
        return (close - low) * 10000 // low

    def on_batch(self, state, batch):
        close = state.close(SYMBOL)
        if close is None:
            return []
        self.closes.append(close)

        holding = state.positions.get(SYMBOL)
        qty = holding.qty if holding is not None else 0

        # Learn the buy fill price from this batch's fills when a position
        # first appears, so exits are measured from what we actually paid.
        if qty > 0 and self.entry_price is None:
            for fill in batch.get("fills", []):
                if (fill.get("side") == "buy" and fill.get("symbol") == SYMBOL
                        and fill.get("status") == "filled"):
                    self.entry_price = int(fill["price"])
                    break
            if self.entry_price is None:
                self.entry_price = close
            self.peak = close

        if qty > 0:
            self.peak = max(self.peak, close)
            gain = (close - self.entry_price) * 10000 // self.entry_price
            trail = (self.peak - close) * 10000 // self.peak
            if gain >= TAKE_PROFIT_BPS or trail >= TRAIL_BPS or gain <= -STOP_BPS:
                # Keep entry/peak: if this sell is rejected at the fill, the
                # position is still held next batch and the same exit must
                # fire again. They are cleared when the bot is flat again.
                return [{"side": "sell", "symbol": SYMBOL, "qty": qty,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            return []

        # Flat: reset long state, then run the dip/bounce entry rule.
        self.entry_price = None
        self.peak = None
        if len(self.closes) < LOOKBACK:
            return []
        high = max(self.closes[-LOOKBACK:])
        if self._dip_bps(close, high) >= DIP_BPS:
            self.armed = True
            if self.trail_low is None or close < self.trail_low:
                self.trail_low = close
        if not self.armed:
            self.trail_low = None
            return []
        if self.trail_low is not None and close > self.trail_low:
            if self._rise_bps(close, self.trail_low) >= RECOVER_BPS:
                self.armed = False
                self.trail_low = None
                if state.cash < 1_000_000:
                    return []
                return [{"side": "buy", "symbol": SYMBOL,
                         "notional_quote_units": state.cash,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        elif self.trail_low is not None and close < self.trail_low:
            self.trail_low = close
        return []


def main():
    bot = SwingBot()
    makefun_bars.run(bot.on_batch)


if __name__ == "__main__":
    main()
