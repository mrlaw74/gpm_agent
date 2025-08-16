import time
import requests
from datetime import datetime

BASE_URL = "https://api-demo.bybit.com"

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
    def __init__(self, initial_usdt=720):
        self.wallet = {"USDT": initial_usdt}
        self.positions = {}       # {symbol: order} 1 order duy nhất
        self.last_prices = {}     

    def place_order(self, symbol, side, qty):
        price = get_market_price(symbol)
        if price is None:
            return None

        # Không mở lệnh nếu đã có lệnh OPEN
        if symbol in self.positions and self.positions[symbol]['status'] == "OPEN":
            return None

        # TP/SL cố định ±1 USDT
        if side.lower() == "buy":
            stop_loss = round(price - 1/qty, 5)
            take_profit = round(price + 1/qty, 5)
        elif side.lower() == "sell":
            stop_loss = round(price + 1/qty, 5)
            take_profit = round(price - 1/qty, 5)

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

        # Log chi tiết khi mở lệnh
        print(f"[NEW ORDER] {symbol} {side} {qty} @ {price} | SL: {stop_loss} TP: {take_profit} | Time: {order['time']}")
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

            # TP/SL ±1 USDT
            if pnl >= 1 or pnl <= -1:
                close_order = True
                reason = "TP" if pnl >= 1 else "SL"
                price_now = get_market_price(symbol)
                print(f"[{reason}] Closing {symbol} {pos['side']} at {price_now} | PnL: {pnl} USDT")

            if close_order:
                self.wallet["USDT"] += pnl
                pos['status'] = "CLOSED"

    def show_wallet(self):
        now = datetime.now().strftime("%H:%M:%S")
        total_pnl = sum(self.compute_pnl(sym) for sym in self.positions if self.positions[sym]['status']=="OPEN")
        print("="*50)
        print(f"💰 Wallet (USDT): {round(self.wallet['USDT'] + total_pnl,2)} | Time: {now}")
        for symbol, pos in self.positions.items():
            print(f"\n{symbol} Position:")
            print(f"  {pos['side']} {pos['qty']} @ {pos['price']} | Status: {pos['status']} | SL: {pos['stop_loss']} TP: {pos['take_profit']}")
            print(f"  PnL: {self.compute_pnl(symbol)} USDT")
        print("="*50 + "\n")

    def auto_trade(self, symbol, qty=0.1):
        price_now = get_market_price(symbol)
        if price_now is None:
            return

        last_price = self.last_prices.get(symbol, price_now)
        change_pct = (price_now - last_price) / last_price

        print(f"[PRICE] {symbol}: {round(price_now,5)} | Change: {round(change_pct*100,3)}%")

        # Nếu chưa có lệnh, mở 1 lệnh theo biến động ±0.04%
        if symbol not in self.positions or self.positions[symbol]['status'] != "OPEN":
            if change_pct <= -0.0004:
                self.place_order(symbol, "Buy", qty)
            elif change_pct >= 0.0004:
                self.place_order(symbol, "Sell", qty)

        self.last_prices[symbol] = price_now

# ----------------------------
# Main Demo
# ----------------------------
if __name__ == "__main__":
    symbols = [
        "ETHUSDT", "BTCUSDT", "DOGEUSDT", "SOLUSDT", "ADAUSDT",
        "BNBUSDT", "XRPUSDT", "MATICUSDT", "LTCUSDT", "DOTUSDT"
    ]
    exchange = DemoExchange()

    while True:
        for sym in symbols:
            price_now = get_market_price(sym)
            if price_now is None:
                continue

            # Xác định volume theo token
            if sym in ["ETHUSDT", "BTCUSDT"]:
                volume = 10000  # USDT
            else:
                volume = 1000   # USDT

            qty = round(volume / price_now, 5)  # tính số lượng token
            exchange.auto_trade(sym, qty=qty)
        exchange.check_stop_take()
        exchange.show_wallet()
        time.sleep(5)
