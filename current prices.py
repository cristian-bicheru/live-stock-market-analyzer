import json
import requests
import time
import datetime
import os

def send(msg):
    os.system('curl https://notify.run/gAtBfgIHhd2CsZ5w -d "' + msg + '"')

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

stocks = ("AMZN", "GOOG", "AAPL", "MSFT", "NVDA", "AMD")

stockString = ""
for stock in stocks:
    pauselist[stock] = 0
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
        data = requests.get(url).json()
        currentDate = datetime.datetime.now()
        currentHour = currentDate.hour
        currentMinute = currentDate.minute
        cont = 1

        notopen = currentDate.weekday()
        if notopen >= 5 or (currentDate.weekday() == 4 and currentHour >= 16):
            nextOpen = currentDate
            if nextOpen.isoweekday() in set((6, 7)):
                nextOpen += datetime.timedelta(days=8 - nextOpen.isoweekday())
            nextOpen = nextOpen.replace(hour=9, minute=30)
            tempHTML = template
            tempHTML.insert(200, "<p> sleeping for the weekend, wakeing in " + str((nextOpen-currentDate).total_seconds()+122) + " seconds. </p>")
            tempHTML.insert(200, "<p> "+str(currentDate)+" </p>")            
            updateSite(tempHTML)
            yeardata = requests.get(yearurl).json()
            time.sleep((nextOpen-currentDate).total_seconds()+122)
        else:
            if currentHour >= 16:
                nextOpen = (currentDate+datetime.timedelta(days=1)).replace(hour=9, minute=30)
                tempHTML = template
                tempHTML.insert(200, "<p> market closed, sleeping for " + str((nextOpen-currentDate).total_seconds()+122) + " seconds. </p>")
                tempHTML.insert(200, "<p> "+str(currentDate)+" </p>")
                updateSite(tempHTML)
                yeardata = requests.get(yearurl).json()
                cont = 0
                time.sleep((nextOpen-currentDate).total_seconds()+122)
            elif currentHour < 9:
                nextOpen = currentDate.replace(hour=9, minute=30)
                tempHTML = template
                tempHTML.insert(200, "<p> market closed, sleeping for " + str((nextOpen-currentDate).total_seconds()+122) + " seconds. </p>")
                tempHTML.insert(200, "<p> "+str(currentDate)+" </p>")
                updateSite(tempHTML)
                yeardata = requests.get(yearurl).json()
                cont = 0
                time.sleep((nextOpen-currentDate).total_seconds()+122)
            elif currentHour == 9:
                if currentMinute < 30:
                    nextOpen = currentDate.replace(hour=9, minute=30)
                    tempHTML = template
                    tempHTML.insert(200, "<p> market closed, sleeping for " + str((nextOpen-currentDate).total_seconds()+122) + " seconds. </p>")
                    tempHTML.insert(200, "<p> "+str(currentDate)+" </p>")
                    updateSite(tempHTML)
                    yeardata = requests.get(yearurl).json()
                    cont = 0
                    time.sleep((nextOpen-currentDate).total_seconds()+122)
                else:
                    cont = 1
            if cont == 1:
                minOpen = (currentDate - currentDate.replace(hour=9, minute=30)).total_seconds()/60
                tempHTML = template
                for stock in stocks:
                    try:
                        sData = list(data[stock]["chart"])
                        Cdata = sData[-2]
                        Ldata = sData[-3]
                        Odata = sData[0]
                        yData = list(yeardata[stock]["chart"])
                        pctChange = Cdata["changeOverTime"]
                        pctChgToDate = round((Cdata["close"]-yData[-1]["close"])/yData[-1]["close"]*100, 2)
                        if pctChgToDate < 0:
                            yData = list(yeardata[stock]["chart"])
                            lastDayThisLow = lowSince(yData, Cdata["close"])
                            tempHTML.insert(200, "<p> "+stock+" has changed by " + str(pctChgToDate) + " so far, current price: " + str(Cdata["close"]) + ", opened at: " + str(Odata["marketClose"])+ " and closed at: "+str(yData[-1]["close"])+"$
                        else:
                            tempHTML.insert(200, "<p> "+stock+" has changed by " + str(pctChgToDate) + " so far, current price: " + str(Cdata["close"]) + ", opened at: " + str(Odata["marketClose"])+ " and closed at: "+str(yData[-1]["close"])+"$
                    except:
                        pass
                tempHTML.insert(200, "<p> "+str(currentDate)+" </p>")
                updateSite(tempHTML)
                time.sleep(302)
    except Exception as ex:
        print("Exception encountered in program: " + str(ex))

