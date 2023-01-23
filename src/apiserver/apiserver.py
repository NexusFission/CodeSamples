from bottle import route, request, run
import json
import datetime
from tabulate import tabulate

signal = {
  "supertrend" : None,
  "larsi" : None,
  "larsi_val" : None
}

current_order = {}
total_pnl = 0
header = ["Symbol", "EntryTime", "Type", "EntryPrice", "ExitTime", "ExitPrice", "CurrentPNL", "TotalPNL"]
order_table = []
order_table.append(header)

def init_order():
  global current_order

  current_order = {
    "status" : None,
    "symbol" : None,
    "position_type" : None,
    "entry_price" : None,
    "entry_time" : None,
    "exit_price" : None,
    "exit_time" : None,
    "current_pnl" : None
  }

init_order()

def record_signal(alert_type):
  global signal
  if alert_type == "supertrend_buy":
    signal["supertrend"] = "BUY"
  if alert_type == "supertrend_sell":
    signal["supertrend"] = "SELL"
  if alert_type == "larsi_moveup":
    signal["larsi"] = "MOVEUP"
  if alert_type == "larsi_movedown":
    signal["larsi"] = "MOVEDOWN"

def print_signal():
  global signal
  print(signal)

def check_signal():
  global signal
  order = None

  if signal["supertrend"] == "BUY" and signal["larsi"] == "MOVEUP":
    order = "LONG"
  if signal["supertrend"] == "SELL" and signal["larsi"] == "MOVEDOWN":
    order = "SHORT"

  return order

def time_now():
  return str(datetime.datetime.now())

def convert_dict_to_array(current_order):
  order = []
  order.append(current_order["symbol"])
  order.append(current_order["entry_time"])
  order.append(current_order["position_type"])
  order.append(current_order["entry_price"])
  order.append(current_order["exit_time"])
  order.append(current_order["exit_price"])
  order.append(current_order["current_pnl"])

  return order

def print_current_order():
  global current_order
  global total_pnl
  global header

  print_order = []
  print_order.append(header)

  order = convert_dict_to_array(current_order)
  order.append(total_pnl)
  print_order.append(order)
  print(tabulate(print_order, tablefmt="txt", headers="firstrow"))

def enter_order(position_type, current_price):
  global order_table
  global current_order

  #Currently one symbol, so one active order, later need to modify
  if current_order["status"] == "Active":
    print("Not entring a new order, since already one is active")
    return

  print("Entering the " + position_type + " trade : " + str(current_price))
  current_order["status"] = "Active"
  current_order["symbol"] = "BTC"
  current_order["position_type"] = position_type
  current_order["entry_price"] = current_price
  current_order["entry_time"] = time_now()
  print_current_order()

def exit_order(position_type, current_price):
  global order_table
  global current_order
  global total_pnl

  if position_type == "LONG":
    pnl = current_price - current_order["entry_price"]
  else:
    pnl = current_order["entry_price"] - current_price

  total_pnl += pnl
  print("Closing the long trade, profit / loss = " + str(pnl))
  print("Total pnl so far = " + str(total_pnl))
  current_order["exit_price"] = current_price
  current_order["exit_time"] = time_now()
  current_order["current_pnl"] = pnl

  order = convert_dict_to_array(current_order)
  order.append(total_pnl)
  order_table.append(order)
  print(tabulate(order_table, tablefmt="txt", headers="firstrow"))

  init_order()

@route('/api/v1/tradingview/alert', method='POST')
def process_alert():
    global signal
    global current_order

    #Read the body from request
    body = request.body.read()
    req_val = request.body.getvalue()
    print(req_val)
    return

    #The request will be in string, convert it to json
    val = json.loads(req_val)
    print(val)
    return

    #Handle based on the alert type
    alert_type = val.get("alert_type")
    record_signal(alert_type)
    print_signal()

    price = val.get("price")

    print("Alert: " + alert_type + ", price: " + str(price))
    return

    #Enter the order for Long / Short if it matches
    order = check_signal()
    if order == "LONG" and current_order["status"] == None:
      enter_order("LONG", price)
      
    if order == "SHORT" and current_order["status"] == None:
      enter_order("SHORT", price)


    #Exit the order for Long / Short if it matches
    if current_order["status"] == "Active":
      if current_order["position_type"] == "LONG" and alert_type == "supertrend_sell":
        exit_order("LONG", price)
      if current_order["position_type"] == "SHORT" and alert_type == "supertrend_buy":
        exit_order("SHORT", price)

@route('/api/v1/tda/oauthcallback', method='POST')
def tda_oauthcallback():
  body = request.body.read()
  val = request.body.getvalue()
  print(val)

run(host='localhost', port=8080, debug=True)
