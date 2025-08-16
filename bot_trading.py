import time
import requests
from datetime import datetime

BASE_URL = "https://api-demo.bybit.com"

# ----------------------------
# CONSTANTS
# ----------------------------
DEFAULT_USDT = 690
TP_SL_USDT = 5       # Take Profit / Stop Loss cố định
VOLUME_BIG = 10000    # ETH, BTC
VOLUME_SMALL = 1000   # Các token còn lại
ENTRY_PRICE_DIFF = 0.00008  # Chênh lệch giá để vào lệnh

SYMBOLS = [
    "ETHUSDT", "BTCUSDT", "DOGEUSDT", "SOLUSDT", "ADAUSDT",
    "BNBUSDT", "XRPUSDT", "MATICUSDT", "LTCUSDT", "DOTUSDT"
]

BIG_VOLUME_SYMBOLS = ["ETHUSDT", "BTCUSDT"]

# ----------------------------
# Lấy giá thị trường thật từ Bybit Demo
# ----------------------------
def get_market_price(symbol="ETHUSDT"):
    url = f"{BASE_URL}/v5/market/recent-trade"
    params = {"symbol": symbol}
    try:
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        if data['retCode'] == 0 and data['result'].get('list'):
            return float(data['result']['list'][-1]['price'])
    except:
        pass
    return None

# ----------------------------
# Exchange Demo kiểu Future, 1 lệnh/buy/sell/token
# ----------------------------
class DemoExchange:
    def __init__(self, initial_usdt=DEFAULT_USDT):
        self.wallet = {"USDT": initial_usdt}
        self.positions = {}       # {symbol: order} 1 order duy nhất
        self.last_prices = {}     

    def place_order(self, symbol, side, qty):
        price = get_market_price(symbol)
        if price is None:
            return None

        if symbol in self.positions and self.positions[symbol]['status'] == "OPEN":
            return None

        # TP/SL ±1 USDT
        if side.lower() == "buy":
            stop_loss = round(price - TP_SL_USDT/qty, 5)
            take_profit = round(price + TP_SL_USDT/qty, 5)
        elif side.lower() == "sell":
            stop_loss = round(price + TP_SL_USDT/qty, 5)
            take_profit = round(price - TP_SL_USDT/qty, 5)

        order = {
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "price": round(price, 5),
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "status": "OPEN",
            "time": datetime.now().strftime("%H:%M:%S")
        }
        self.positions[symbol] = order

        side_icon = "⬆️" if side.lower() == "buy" else "⬇️"
        print(f"[NEW ORDER] {symbol} {side_icon} {qty} @ {price} | SL: {stop_loss} TP: {take_profit} | Time: {order['time']}")
        return order

    def compute_pnl(self, symbol):
        price_now = get_market_price(symbol)
        if price_now is None or symbol not in self.positions:
            return 0
        pos = self.positions[symbol]
        if pos['status'] != "OPEN":
            return 0
        if pos['side'].lower() == "buy":
            return round((price_now - pos['price']) * pos['qty'],2)
        elif pos['side'].lower() == "sell":
            return round((pos['price'] - price_now) * pos['qty'],2)

    def check_stop_take(self):
        for symbol, pos in list(self.positions.items()):
            if pos['status'] != "OPEN":
                continue

            pnl = self.compute_pnl(symbol)
            close_order = False

            if pnl >= TP_SL_USDT or pnl <= -TP_SL_USDT:
                close_order = True
                reason = "TP" if pnl >= TP_SL_USDT else "SL"
                price_now = get_market_price(symbol)
                print(f"[{reason}] Closing {symbol} {pos['side']} at {price_now} | PnL: {pnl} USDT")

            if close_order:
                self.wallet["USDT"] += pnl
                pos['status'] = "CLOSED"

    def show_wallet(self):
        now = datetime.now().strftime("%H:%M:%S")
        total_pnl = sum(self.compute_pnl(sym) for sym in self.positions if self.positions[sym]['status']=="OPEN")
        print("="*50)
        print(f"💰 Wallet (USDT): {round(self.wallet['USDT'] + total_pnl,2)} | ⏰ Time: {now}")
        for symbol, pos in self.positions.items():
            status_icon = "🟢" if pos['status']=="OPEN" else "🔴"
            side_icon = "⬆️" if pos['side'].lower()=="buy" else "⬇️"
            pnl_val = self.compute_pnl(symbol)
            pnl_icon = "📈" if pnl_val > 0 else "📉" if pnl_val < 0 else "⚖️"
            print(f"\n{symbol} Position:")
            print(f"  {side_icon} {pos['qty']} @ {pos['price']} | {status_icon} {pos['status']} | SL: {pos['stop_loss']} TP: {pos['take_profit']}")
            print(f"  {pnl_icon} PnL: {pnl_val} USDT")
        print("="*50 + "\n")

    def auto_trade(self, symbol, qty=0.1):
        price_now = get_market_price(symbol)
        if price_now is None:
            return

        last_price = self.last_prices.get(symbol, price_now)
        change_pct = (price_now - last_price) / last_price

        print(f"[PRICE] {symbol}: {round(price_now,5)} | Change: {round(change_pct*100,3)}%")

        if symbol not in self.positions or self.positions[symbol]['status'] != "OPEN":
            if change_pct <= -ENTRY_PRICE_DIFF:
                self.place_order(symbol, "Buy", qty)
            elif change_pct >= ENTRY_PRICE_DIFF:
                self.place_order(symbol, "Sell", qty)

        self.last_prices[symbol] = price_now

# ----------------------------
# Main Demo
# ----------------------------
if __name__ == "__main__":
    exchange = DemoExchange()

    while True:
        for sym in SYMBOLS:
            price_now = get_market_price(sym)
            if price_now is None:
                continue

            # Xác định volume theo token
            volume = VOLUME_BIG if sym in BIG_VOLUME_SYMBOLS else VOLUME_SMALL
            qty = round(volume / price_now, 5)

            exchange.auto_trade(sym, qty=qty)
        exchange.check_stop_take()
        exchange.show_wallet()
        time.sleep(5)
