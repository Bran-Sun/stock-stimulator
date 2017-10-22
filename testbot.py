import sys
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
team_name = "HUJUBIAOJU"
test_mode = True
price_min = 10000000

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index = 0
prod_exchange_hostname = "loacalhost"

port = 25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = ("test-exch-" + team_name) if test_mode else prod_exchange_hostname

# ------------------
order_id = 1


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

def read_from_mess(exchange):
    mes = read_from_exchange(exchange)
    if mes["type"] != "reject":
        print(mes)


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

    read_from_mess(exchange)


def handle_HHBC(exchange):
    pass


def handle_():
    pass

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    print(read_from_exchange(exchange))
    
    while True:
      mes = read_from_exchange(exchange)
      if mes["type"] != "reject":
          print(mes)
      if ("symbol" in mes.keys()) and ("buy" in mes.keys()):
          if (mes["symbol"] == "HSBC") or (mes["symbol"] == "FIVEHK"):
              print(mes)
          if mes["symbol"] == "USDHKD":
              handle_USDHKD(exchange, mes)
        
if __name__ == "__main__":
    main()
