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


def handle_USDHKD(exchange):
    write_to_exchange(exchange,
                      {"type"    : "add",
                       "order_id": get_order_id(),
                       "symbol"  : "USDHKD",
                       "dir"     : "BUY",
                       "price"   : 80000,
                       "size"    : 200})
    write_to_exchange(exchange,
                      {"type"    : "add",
                       "order_id": get_order_id(),
                       "symbol"  : "USDHKD",
                       "dir"     : "SELL",
                       "price"   : 80001,
                       "size"    : 200})


def handle_HSBC(exchange, msg):
    pass


def handle_():
    pass


def handle_GBP(exchange, msg):
    pass


# def USD_to_GBP_to_HKD(exchange):
#     usd_to_gbp = (max(shares["GBPUSD"]["sell"], key=lambda x: x[0], default=[0, 0])[0]+min(shares["GBPUSD"]["buy"], key=lambda x: x[0], default=[10000000, 0])[0])/2
#     gbp_to_hkd = (min(shares["GBPHKD"]["buy"], key=lambda x: x[0], default=[10000000, 0])[0]+max(shares["GBPHKD"]["sell"], key=lambda x: x[0], default=[0, 0])[0])/2
#     print("USD_TO_GBP: ".lower(), usd_to_gbp, "GBP_TO_HKD: ".lower(), gbp_to_hkd)
#     if usd_to_gbp != 0 and gbp_to_hkd != 10000000 and usd_to_gbp * 8 < gbp_to_hkd:
#         write_to_exchange(exchange, {
#             "type"    : "add",
#             "order_id": get_order_id(),
#             "symbol"  : "GBPUSD",
#             "dir"     : "BUY",
#             "price"   : usd_to_gbp,
#             "size"    : 1})
#         write_to_exchange(exchange, {
#             "type"    : "add",
#             "order_id": get_order_id(),
#             "symbol"  : "GBPHKD",
#             "dir"     : "SELL",
#             "price"   : gbp_to_hkd - 1,
#             "size"    : 1})
#

# def HKD_to_GBP_to_USD(exchange):
#     hkd_to_gbp = (max(shares["GBPHKD"]["sell"], key=lambda x: x[0], default=[0, 0])[0]+min(shares["GBPHKD"]["buy"], key=lambda x: x[0], default=[0, 0])[0]
#     gbp_to_usd = min(shares["GBPUSD"]["buy"], key=lambda x: x[0], default=[10000000, 0])[0]
#     print("HKD_TO_GBP: ", hkd_to_gbp, "GBP_TO_USD: ", gbp_to_usd)
#     if hkd_to_gbp != 0 and gbp_to_usd != 10000000 and hkd_to_gbp < gbp_to_usd * 8:
#         write_to_exchange(exchange, {
#             "type"    : "add",
#             "order_id": get_order_id(),
#             "symbol"  : "GBPHKD",
#             "dir"     : "BUY",
#             "price"   : hkd_to_gbp,
#             "size"    : 1})
#         write_to_exchange(exchange, {
#             "type"    : "add",
#             "order_id": get_order_id(),
#             "symbol"  : "GBPUSD",
#             "dir"     : "SELL",
#             "price"   : gbp_to_usd - 1,
#             "size"    : 1})

def fuck_USD(exchange):
    usd_to_gbp = (max(shares["GBPUSD"]["buy"], key=lambda x: x[0], default=[0, 0])[0] +
                  min(shares["GBPUSD"]["sell"], key=lambda x: x[0], default=[10000000, 0])[0]) / 2
    gbp_to_hkd = (min(shares["GBPHKD"]["sell"], key=lambda x: x[0], default=[10000000, 0])[0] +
                  max(shares["GBPHKD"]["buy"], key=lambda x: x[0], default=[0, 0])[0]) / 2
    print("USD_TO_GBP: ".lower(), usd_to_gbp, "GBP_TO_HKD: ".lower(), gbp_to_hkd)
    if usd_to_gbp != 0 and gbp_to_hkd != 10000000:
        if usd_to_gbp * 8 < gbp_to_hkd:
            write_to_exchange(exchange, {
                "type"    : "add",
                "order_id": get_order_id(),
                "symbol"  : "GBPUSD",
                "dir"     : "BUY",
                "price"   : int(usd_to_gbp - 0.5),
                "size"    : 2})
            write_to_exchange(exchange, {
                "type"    : "add",
                "order_id": get_order_id(),
                "symbol"  : "GBPHKD",
                "dir"     : "SELL",
                "price"   : int(gbp_to_hkd + 1.5),
                "size"    : 1})
        elif usd_to_gbp * 8 > gbp_to_hkd:
            write_to_exchange(exchange, {
                "type"    : "add",
                "order_id": get_order_id(),
                "symbol"  : "GBPHKD",
                "dir"     : "BUY",
                "price"   : int(gbp_to_hkd - 0.5),
                "size"    : 2})
            write_to_exchange(exchange, {
                "type"    : "add",
                "order_id": get_order_id(),
                "symbol"  : "GBPUSD",
                "dir"     : "SELL",
                "price"   : int(usd_to_gbp + 1.5),
                "size"    : 1})
 
def fuck_fund(exchange):
    hsbc_max = max(shares["HSBC"]["buy"], key=lambda x: x[0], default=[0, 0])[0]
    hsbc_min = min(shares["HSBC"]["sell"], key=lambda x: x[0], default=[10000000, 0])[0]
    hsbc_fair = (hsbc_max + hsbc_min) / 2
    fiveehk_max = min(shares["HSBC"]["sell"], key=lambda x: x[0], default=[10000000, 0])[0]
    fiveehk_min = max(shares["HSBC"]["buy"], key=lambda x: x[0], default=[0, 0])[0] 
    fiveehk_fair = (fiveehk_min + fiveehk_max) / 2



l = {
    "USDHKD": False,
    "GBPUSD": False,
    "GBPHKD": False,
    "FIVEHK": False,
    "HSBC"  : False,
}

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    
    while True:
        msg = read_from_exchange(exchange)
        print("from exchange: ", read_from_exchange(exchange))
        if msg["type"] == "book":
            l[msg["symbol"]] = True
            shares[msg["symbol"]]["buy"] = msg["buy"]
            shares[msg["symbol"]]["sell"] = msg["sell"]
            if (msg["symbol"] == "USDHKD" or msg["symbol"] == "GBPHKD" or msg["symbol"] == "GBPUSD") and l["USDHKD"] and l["GBPHKD"] and l["GBPUSD"]:
                fuck_USD(exchange)
                handle_USDHKD(exchange)
                l["USDHKD"] = False
                l["GBPHKD"] = False
                l["GBPUSD"] = False
            if (msg["symbol"] == "HSBC" or msg["symbol"] == "FIVEHK") and l["HSBC"] and l["FIVEHK"]:
                fuck_fund(exchange)
                l["HSBC"] = False
                l["FIVEHK"] = False


if __name__ == "__main__":
    main()
