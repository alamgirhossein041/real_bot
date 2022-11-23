#from APY import *
import requests
import time
import hmac
import hashlib
from decouple import config


api_secret = config('api_secret')
api_key = config('api_key')

def openShortLimit(price, qty, currency="ETHUSDT"):
    url = "https://binancefuture.com/fapi/v1/order?"
    payload = "symbol="+str(currency)+'&side=SELL&timeInForce=GTC&type=LIMIT&quantity='+str(qty)+'&price='+str(price)+'&timestamp='+str(int(time.time()*1000))
    signature = hmac.new(api_secret.encode('utf-8'), payload.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    payload += "&signature=" + signature
    headers = {'X-MBX-APIKEY' : api_key}
    data = requests.post(url, params = payload, headers=headers)
    print(data.text)
    
def openLongLimit(price, qty, currency="ETHUSDT"):
    url = "https://testnet.binancefuture.com/fapi/v1/order?"
    payload = "symbol="+str(currency)+'&side=BUY&timeInForce=GTC&type=LIMIT&quantity='+str(qty)+'&price='+str(price)+'&timestamp='+str(int(time.time()*1000))
    signature = hmac.new(api_secret.encode('utf-8'), payload.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    payload += "&signature=" + signature
    headers = {'X-MBX-APIKEY' : api_key}
    data = requests.post(url, params = payload, headers=headers)
    print(data.text)
    
def openShortMarket(qty, currency):
    url = "https://fapi.binance.com/fapi/v1/order?"
    payload = "symbol="+str(currency)+'&side=SELL&type=MARKET&quantity='+str(qty)+'&timestamp='+str(int(time.time()*1000))
    signature = hmac.new(api_secret.encode('utf-8'), payload.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    payload += "&signature=" + signature
    headers = {'X-MBX-APIKEY' : api_key}
    data = requests.post(url, params = payload, headers=headers).json()
    print(data['status'])
    
def openLongMarket(qty, currency):
    url = "https://fapi.binance.com/fapi/v1/order?"
    payload = "symbol="+str(currency)+'&side=BUY&type=MARKET&quantity='+str(qty)+'&timestamp='+str(int(time.time()*1000))
    signature = hmac.new(api_secret.encode('utf-8'), payload.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    payload += "&signature=" + signature
    headers = {'X-MBX-APIKEY' : api_key}
    data = requests.post(url, params = payload, headers=headers).json()
    return(data['status'])


def closeShortLimit(price, qty, currency="ETHUSDT"):
    url = "https://testnet.binancefuture.com/fapi/v1/order?"

    payload = "symbol="+str(currency)+'&side=BUY&timeInForce=GTC&type=LIMIT&quantity='+str(qty)+'&price='+str(price)+'&timestamp='+str(int(time.time()*1000))


    signature = hmac.new(api_secret.encode('utf-8'), payload.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    payload += "&signature=" + signature
    headers = {'X-MBX-APIKEY' : api_key}
    data = requests.post(url, params = payload, headers=headers)
    #print(data.text)

""" def getPrice(currency="ETHUSDT"):
    url = "https://testnet.binancefuture.com/fapi/v1/premiumIndex"

    payload = {'symbol': currency}
    data = requests.get(url=url, params=payload).json()
    #print(data)
    return round(float(data['markPrice']),4) """


def getOpenOrdersAmount(currency="ETHUSDT"):
    url = "https://fapi.binance.com/fapi/v1/openOrders?"

    payload = 'currency='+ currency +'&timestamp='+str(int(time.time()*1000))


    signature = hmac.new(api_secret.encode('utf-8'), payload.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    payload += "&signature=" + signature
    headers = {'X-MBX-APIKEY' : api_key}
    data = requests.get(url, params = payload, headers=headers).json()
    #print(data)
    return ((float(data[0]['positionAmt'])))

def closeAllOpenOrders(currency="ETHUSDT"):
    url = "https://testnet.binancefuture.com/fapi/v1/allOpenOrders?"

    payload = 'symbol='+ currency +'&timestamp='+str(int(time.time()*1000))


    signature = hmac.new(api_secret.encode('utf-8'), payload.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    payload += "&signature=" + signature
    headers = {'X-MBX-APIKEY' : api_key}
    data = requests.delete(url, params = payload, headers=headers).json()
    #print(data)

def getOpenedAmount(ubra, symbol):
    return float((ubra.futures_position_information(symbol=symbol))[0]['positionAmt'])

def getPrice(ubra, symbol):
    return float((ubra.futures_recent_trades(symbol=symbol, limit =1))[0]['price'])

def get_minQty_notional(ubra, symbol):
    return float((ubra.get_symbol_info(symbol=symbol))['filters'][3]['minNotional'])
    

def get_used_weight_my(ubra):
    return ubra.get_used_weight()

def market_sell(ubra, symbol, amount):
    return ubra.order_market_sell(quantity=abs(amount), symbol=symbol)

def market_buy(ubra, symbol, amount):
    return ubra.order_market_buy(quantity=abs(amount), symbol=symbol)

#print(openLongMarket(200,'xlmusdt'))