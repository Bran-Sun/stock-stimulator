import sys
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
team_name = "HUJUBIAOJU"
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index = 0
prod_exchange_hostname = "localhost"

port = 25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = ("test-exch-" + team_name) if test_mode else prod_exchange_hostname

# ------------------
order_id = 0

HSBC_fair = None
shares = {
    "USDHKD": {"buy": [], "sell": []},
    "GBPUSD": {"buy": [], "sell": []},
    "GBPHKD": {"buy": [], "sell": []},
    "FIVEHK": {"buy": [], "sell": []},
    "HSBC"  : {"buy": [], "sell": []},
}


def get_order_id():
    global order_id
    order_id += 1
    if order_id > 10000000:
        order_id = 0
    return order_id


# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)


def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")


def read_from_exchange(exchange):
    return json.loads(exchange.readline())


def print_msg(exchange):
    recv = read_from_exchange(exchange)
    if recv["type"] == "book":
        print(recv)


def handle_USDHKD(exchange, mes):
    price_buy = mes["buy"]
    price_sell = mes["sell"]
    if price_buy and price_sell:
        high = price_buy[0]
        price_in = high[0]
        low = price_sell[0]
        price_out = low[0]
        if (price_in<= 80000) and (price_out >= 80001):
            write_to_exchange(exchange,
                              {"type"    : "add",
                              "order_id": get_order_id(),
                              "symbol"  : "USDHKD",
                              "dir"     : "BUY",
                              "price"   : price_in,
                              "size"    : 1})
            write_to_exchange(exchange,
                              {"type"    : "add",
                              "order_id": get_order_id(),
                              "symbol"  : "USDHKD",
                              "dir"     : "SELL",
                              "price"   : price_out,
                              "size"    : 1})


def handle_HSBC(exchange, msg):
    pass


def handle_():
    pass


def handle_GBP(exchange, msg):
    pass


def USD_to_GBP_to_HKD(exchange):
    usd_to_gbp = min(shares["GBPUSD"]["sell"], key=lambda x: x[0], default=[0, 0])[0]
    gbp_to_hkd = max(shares["GBPHKD"]["buy"], key=lambda x: x[0], default=[10000000, 0])[0]
    print("USD_TO_GBP: ".lower(), usd_to_gbp, "GBP_TO_HKD: ".lower(), gbp_to_hkd)
    if usd_to_gbp != 0 and gbp_to_hkd != 10000000 and usd_to_gbp * 8 < gbp_to_hkd:
        write_to_exchange(exchange, {
            "type"    : "add",
            "order_id": get_order_id(),
            "symbol"  : "GBPUSD",
            "dir"     : "BUY",
            "price"   : usd_to_gbp,
            "size"    : 1})
        write_to_exchange(exchange, {
            "type"    : "add",
            "order_id": get_order_id(),
            "symbol"  : "GBPHKD",
            "dir"     : "SELL",
            "price"   : gbp_to_hkd,
            "size"    : 1})


def GBP_to_USD(exchange):
    gbp_to_usd = max(shares["GBPUSD"]["buy"], key=lambda x: x[0], default=[10000000, 0])[0]
    write_to_exchange(exchange, {
            "type"    : "add",
            "order_id": get_order_id(),
            "symbol"  : "GBPUSD",
            "dir"     : "SELL",
            "price"   : gbp_to_usd - 1,
            "size"    : 10})


# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})

    GBP = False;
    GBP2 = False;

    
    while True:
        msg = read_from_exchange(exchange)
        print("from exchange: ", read_from_exchange(exchange))
        if msg["type"] == "book":
            shares[msg["symbol"]]["buy"] = msg["buy"]
            shares[msg["symbol"]]["sell"] = msg["sell"]
            if msg["symbol"] == "USDHKD":
                handle_USDHKD(exchange, msg)
            if msg["symbol"] == "GBPUSD":
                GBP = True
            if (msg["symbol"] == "GBPHKD") and GBP:
                USD_to_GBP_to_HKD(exchange)
                GBP = False
            if msg["symbol"] == "GBPUSD":
                GBP_to_USD(exchange)



if __name__ == "__main__":
    main()
