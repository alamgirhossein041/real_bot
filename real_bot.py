
from tracemalloc import start
import numpy as np
import matplotlib.pyplot as plt
from bot import *
import time
import datetime as datetime
from decouple import config
api_key = config('api_key')
api_secret = config('api_secret')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.animation as animation
import unicorn_binance_websocket_api.manager as ubwam
from unicorn_binance_rest_api.manager import BinanceRestApiManager
from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager
from google.cloud import storage

time_for_name = str(datetime.datetime.now())
path_to_private_key = './defaust-343537e24181.json'
client = storage.Client.from_service_account_json(json_credentials_path=path_to_private_key)
bucket = client.bucket('hedging-bot-statistics')

symbol = 'ethusdt'
testnet = 'binance.com-futures-testnet'
mainnet = 'binance.com-futures'

ys = []
xs = []

ubra = BinanceRestApiManager(api_key=api_key, api_secret = api_secret, exchange=mainnet, requests_params={'timeout' : 20})
binance_websocket_api_manager = ubwam.BinanceWebSocketApiManager(exchange=mainnet)
binance_websocket_api_manager.create_stream("trade", symbol, output="UnicornFy")
# create instances of BinanceWebSocketApiManager
ubwa_com = BinanceWebSocketApiManager(exchange=mainnet)

def animate(ys):
    data = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
    try:
        if data['stream_type']:
            ys.append(float(data['price']))
    except KeyError:
        pass
    except TypeError:
        pass


def last_price():
    animate(ys)
    try: 
        return(ys[-1])
    except IndexError:
        time.sleep(0.5)
        animate(ys)
        try: 
            return(ys[-1])
        except IndexError:
            time.sleep(1)
            animate(ys)
            try: 
                return(ys[-1])
            except IndexError:
                time.sleep(10)
                animate(ys)
                return (ys[-1])


class Portfolio:

    def __init__(self, prices, initPrice=35000, initBTCinPool=1, dailyVol=0.085, fundingRateStep=0.0001, makerFees=0.0005, APRstep=0.0008, mode=0):

        if mode == 0:                   
            self.price = initPrice      # FOR SIMULATION  


        elif mode == 1:
            self.prices = prices        #FOR BINANCE HISTORICAL DATA    
            self.ind = 0
            self.price = self.prices[0]
            initPrice = self.price  

        self.dailyVol = dailyVol
        self.mode = mode
        self.stepFundingRate = fundingRateStep
        self.makerFees = makerFees
        self.initialInvest = initBTCinPool * initPrice * 2
        self.stepPoolReturn = APRstep
        self.k = initPrice * initBTCinPool * initBTCinPool
        self.BTCinPool = initBTCinPool

        self.totalOpenShortAmount = 0 #everything is relative +/-
        self.totalFundingFees = 0
        self.totalShortPNL = 0
        self.totalShortingFees = 0
        self.averageOpenPrice = 0
        self.totalPoolFees = 0
        self.filled_order = False
        self.unrealizedPnL = 0

    def updateShortPosition(self):
        self.unrealizedPnL = (self.price - self.averageOpenPrice) * self.totalOpenShortAmount
        if self.filled_order == True:
            self.modifyShort(self.price, self.BTCinPool + self.totalOpenShortAmount)
            self.totalOpenShortAmount = getOpenedAmount(ubra, symbol)
            xs.append(self.totalOpenShortAmount)
        else: self.totalOpenShortAmount = xs[-1]
        
        


    def modifyShort(self, price, amount):
        if amount > 0:
            self.openShort(price, amount)
        else: 
            self.closeShort(price, amount)

    def openShort(self, openPrice, amount):
        amount = np.abs(amount)
        
        self.totalShortingFees +=  - openPrice * amount * self.makerFees
        self.averageOpenPrice = (np.abs(self.totalOpenShortAmount) * self.averageOpenPrice + openPrice * amount) / (np.abs(self.totalOpenShortAmount) + amount)

    def closeShort(self, closePrice, amount): 

        amount = np.abs(amount)
        #assert amount <= self.totalOpenShortAmount
        self.totalShortPNL += -(closePrice - self.averageOpenPrice) * amount
        self.totalShortingFees +=  - closePrice * amount * self.makerFees
        

    def payShortFees(self, price, amount):
        amount = np.abs(amount)
        self.totalShortingFees += - price * amount * self.makerFees


    def totalPoolAmount(self):
        return self.BTCinPool * self.price * 2
    
    def timeStep(self):
        self.newPrice()
        self.updatePoolPosition()
        self.earnStepFunding()
        self.earnPoolFees()


    def earnPoolFees(self):
        self.totalPoolFees += self.totalPoolAmount() * self.stepPoolReturn

    def earnStepFunding(self):
        #DEPENDS ON THE SPAN OF THE STEP. HERE IN DAYS
        self.totalFundingFees += self.totalOpenShortAmount * self.averageOpenPrice * self.stepFundingRate 


    def updatePoolPosition(self):
        
        self.BTCinPool = np.sqrt(self.k/self.price)
    
    def newPrice(self):

        if self.mode == 0:
            newPrice = self.price * (1 + np.random.normal(0, self.dailyVol))  #  FOR SIMULATION
            self.price = newPrice
            return newPrice
        elif self.mode == 1:
            self.ind += 1         # FOR BINANCE HISTORICAL DATA
            self.price = self.prices[self.ind]
            return self.price
        else:
            self.price = last_price()
            return self.price

    def bot(self, optimEachInS):
        
        dates = []
        prices = []
        shortPNL = []
        shortPNL_USD = []
        fundingFees = []
        shortingFees = []
        poolMoney = []
        poolFees = []
        impermanentLoss = []
        totalOpenShortAmount = []
        BTCinPool = []
        amounts = []
        averageOpenPrice = []
        unrealizedPnL_percent = []
        roi = []
        
        
        while True:
            #closeAllOpenOrders()
            self.price = last_price()
            
            print(self.BTCinPool, self.totalOpenShortAmount, self.price)
            self.updatePoolPosition()
            amount = self.BTCinPool + self.totalOpenShortAmount
            amount = round(amount,2)
            
            self.filled_order = False
            
            if amount > (10/self.price):
                try: 
                    openShortMarket(abs(amount), symbol)
                    print("-------------OPENED MARKET SHORT----------")
                    print("-------------"+str(amount)+"----------")
                    self.filled_order = True
                except KeyError:
                    pass
            
            elif amount < -(10/self.price):
                try: 
                    openLongMarket(abs(amount), symbol)
                    print("-------------OPENED MARKET LONG----------")
                    print("-------------"+str(amount)+"----------")
                    self.filled_order = True
                except KeyError:
                    pass


            #self.price = myPrice
            self.updateShortPosition()
            self.earnStepFunding()
            self.earnPoolFees()
            dates.append(datetime.datetime.now())
            prices.append(self.price)
            #amount.append(self.BTCinPool)
            shortPNL.append(self.totalShortPNL/self.initialInvest)
            shortPNL_USD.append(self.totalShortPNL)
            fundingFees.append(self.totalFundingFees/self.initialInvest)
            shortingFees.append(self.totalShortingFees/self.initialInvest)
            poolMoney.append(self.totalPoolAmount()/self.initialInvest - 1)
            poolFees.append(self.totalPoolFees/self.initialInvest)
            impermanentLoss.append(self.totalPoolAmount()/((prices[0]+self.price) * self.k / prices[0]) - 1)
            totalOpenShortAmount.append(self.totalOpenShortAmount)
            BTCinPool.append(self.BTCinPool)
            amounts.append(self.BTCinPool + self.totalOpenShortAmount)
            averageOpenPrice.append(self.averageOpenPrice)
            unrealizedPnL_percent.append(self.unrealizedPnL/self.initialInvest)
            roi.append(unrealizedPnL_percent[-1] + fundingFees[-1]+ shortingFees[-1]+ poolMoney[-1]+ poolFees[-1])

            d = {'Date' : dates, 
                'Price' : prices,
                'Short_PNL' : shortPNL,
                'ShortPNL_USD' : shortPNL_USD,
                'Funding_Fees' : fundingFees,
                'Shorting_Fees' : shortingFees,
                'Pool_Money' : poolMoney,
                'Pool_Fees' : poolFees,
                'Impermanent_Loss' : impermanentLoss,
                'Total_Open_Short_Amount' : totalOpenShortAmount,
                'Tokens_in_Pool' : BTCinPool,
                'Delta' : amounts,
                'Average_Open_Price' : averageOpenPrice,
                'Unrealized_PnL_%' : unrealizedPnL_percent,
                'ROI' :roi}
            
            
            print("-------------START----------")
            print("First price: " + str(prices[0]) + ' Price,c='+str(self.price))
            print("ROI: ", shortPNL[-1] + fundingFees[-1] + shortingFees[-1], poolMoney[-1], poolFees[-1])
            print("shortPNL", shortPNL[-1])
            print("unrealizedPnL_percent", unrealizedPnL_percent[-1])
            print("shortPNL_USD", shortPNL_USD[-1])
            print("fundingFees", fundingFees[-1])
            print("shortingFees", shortingFees[-1])
            print("poolMoney", poolMoney[-1])
            print("poolFees", poolFees[-1])
            print("totalOpenShortAmount", totalOpenShortAmount[-1])
            print("BTCinPool", BTCinPool[-1])
            print("amount", amounts[-1])
            print("APR", ( shortPNL[-1] + fundingFees[-1] + shortingFees[-1])*(525600/optimEachInS))
            print('Average Prics: ', averageOpenPrice[-1])
            print(datetime.datetime.now())
            print("--------------END-----------")
            
            df = pd.DataFrame(d)
            df.to_csv('stat.csv')
            
            
            #print("amount", amount[-1])
            time.sleep(optimEachInS)
            
def startStrategy():
    
    initPrice = last_price()
    pf = Portfolio([], initPrice, initBTCinPool=0.5, fundingRateStep=0.000000039583333, APRstep = 0.0003805175038, mode=2)
    pf.bot(optimEachInS = (0.1))
    
startStrategy()