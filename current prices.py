import json
import requests
import time
import datetime
import os

def send(msg):
    os.system('curl https://notify.run/gAtBfgIHhd2CsZ5m -d "' + msg + '"')

def updateSite(newHTML):
    HTML = ""
    for x in range(0, len(newHTML)):
        if x != len(newHTML)-1:
            HTML = HTML + newHTML[x] + " \n "
        else:
            HTML = HTML + newHTML[x]
    exsisting = open("index.html", "w")
    exsisting.write(HTML)
    exsisting.close()

def loadTemplate():
    tp = open("template.html", "r")
    rt = tp.read().split("\n")
    tp.close()
    return rt

template = loadTemplate()

send("stock analyzer started")
#example: https://api.iextrading.com/1.0/stock/market/batch?symbols=aapl,fb&types=chart&range=1d&last=5

urlp1 = "https://api.iextrading.com/1.0/stock/market/batch?symbols="
urlp2 = "&types=chart&range=1d&last=5"
urlp3 = "&types=chart&range=1y&last=5"

stocks = ("AMZN", "AAPL", "GOOG")

baseportfolio = ("AMZN:20:1500")

stockString = ""
for stock in stocks:
    stockString = stockString + stock + ","

url = urlp1+stockString+urlp2
yearurl = urlp1+stockString+urlp3
yeardata = requests.get(yearurl).json()

def lowSince(data, price):
    for day in range(len(data)-1, 0, -1):
        diff = data[day]["close"]-price
        if diff <= 0:
            return data[day]["label"]
            break
            

while True:
    try:
        template = loadTemplate()
        currentDate = datetime.datetime.now()
        currentHour = currentDate.hour
        currentMinute = currentDate.minute
        cont = 1

        notopen = currentDate.weekday()
        if notopen >= 5 or (currentDate.weekday() == 4 and currentHour >= 16):
            nextOpen = currentDate
            if nextOpen.isoweekday() in set((5, 6, 7)):
                nextOpen += datetime.timedelta(days=8 - nextOpen.isoweekday())
            nextOpen = nextOpen.replace(hour=9, minute=30)
            tempHTML = template
            tempHTML.insert(223, "<p> sleeping for the weekend, wakeing in " + str((nextOpen-currentDate).total_seconds()+122) + " seconds. </p>")
            tempHTML.insert(223, "<p> "+str(currentDate)+" </p>")            
            updateSite(tempHTML)
            yeardata = requests.get(yearurl).json()
            time.sleep((nextOpen-currentDate).total_seconds()+122)
        else:
            if currentHour >= 16:
                nextOpen = (currentDate+datetime.timedelta(days=1)).replace(hour=9, minute=30)
                tempHTML = template
                tempHTML.insert(223, "<p> market closed, sleeping for " + str((nextOpen-currentDate).total_seconds()+122) + " seconds. </p>")
                tempHTML.insert(223, "<p> "+str(currentDate)+" </p>")
                updateSite(tempHTML)
                yeardata = requests.get(yearurl).json()
                cont = 0
                time.sleep((nextOpen-currentDate).total_seconds()+122)
            elif currentHour < 9:
                nextOpen = currentDate.replace(hour=9, minute=30)
                tempHTML = template
                tempHTML.insert(223, "<p> market closed, sleeping for " + str((nextOpen-currentDate).total_seconds()+122) + " seconds. </p>")
                tempHTML.insert(223, "<p> "+str(currentDate)+" </p>")
                updateSite(tempHTML)
                yeardata = requests.get(yearurl).json()
                cont = 0
                time.sleep((nextOpen-currentDate).total_seconds()+122)
            elif currentHour == 9:
                if currentMinute < 30:
                    nextOpen = currentDate.replace(hour=9, minute=30)
                    tempHTML = template
                    tempHTML.insert(223, "<p> market closed, sleeping for " + str((nextOpen-currentDate).total_seconds()+122) + " seconds. </p>")
                    tempHTML.insert(223, "<p> "+str(currentDate)+" </p>")
                    updateSite(tempHTML)
                    yeardata = requests.get(yearurl).json()
                    cont = 0
                    time.sleep((nextOpen-currentDate).total_seconds()+122)
                else:
                    cont = 1
            if cont == 1:
                minOpen = (currentDate - currentDate.replace(hour=9, minute=30)).total_seconds()/60
                tempHTML = template
                try:
                    data = requests.get(url).json()
                except:
                    print("data retrival error")
                for stock in stocks:
                    try:
                        sData = list(data[stock]["chart"])
                        Cdata = sData[-1]
                        Odata = sData[0]
                        yData = list(yeardata[stock]["chart"])
                        if Cdata["numberOfTrades"] > 0:
                            cdataclose = Cdata["close"]
                            ydataclose = yData[-1]["close"]
                            pctChange = Cdata["changeOverTime"]
                            pctChgToDate = round((cdataclose-ydataclose)/ydataclose*100, 2)
                            if pctChgToDate < 0:
                                lastDayThisLow = lowSince(yData, cdataclose)
                                tempHTML.insert(223, "<p> "+stock+" has changed by " + str(pctChgToDate) + " so far, current price: " + str(cdataclose) + ", opened at: " + str(Odata["close"])+ " and closed at: "+str(ydataclose)+" yesterday. The last time it was this low was on " + lastDayThisLow + ". </p> \n")
                            else:
                                tempHTML.insert(223, "<p> "+stock+" has changed by " + str(pctChgToDate) + " so far, current price: " + str(cdataclose) + ", opened at: " + str(Odata["close"])+ " and closed at: "+str(ydataclose)+" yesterday. </p>\n")
                        else:
                            tempHTML.insert(223, "<p> No trades for " + stock + " in the last minute. </p>")
                    except Exception as ex:
                        print(ex)
                
                balance = 100000
                
                for stock in baseportfolio:
                    try:
                        info = stock.split(":")
                        symbol = info[0]
                        shares = info[1]
                        buy = info[2]
                        sData = list(data[symbol]["chart"])
                        for x in range(1, 100):
                            Cdata = sData[-x]
                            if Cdata["numberOfTrades"] > 0:
                                cdataclose = Cdata["close"]
                                balance += shares*(cdataclose-buy)
                                break
                            print("bug")
                    except Exception as ex:
                        print(ex)
                if currentHour == 15 and currentMinute >= 59:
                    send("portfolio closed at "+str(balance/100000)+" today ("+str(currentDate)+")")
                
                tempHTML.insert(223, "<p> Portfolio Gains: "+str(balance/100000)+" </p>")
                tempHTML.insert(223, "<p> "+str(currentDate)+" </p>")
                updateSite(tempHTML)
                tempHTML = ""
                time.sleep(62)
    except Exception as ex:
        print("Exception encountered in program: " + str(ex))
