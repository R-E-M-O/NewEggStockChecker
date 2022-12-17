import requests
import time
import random
import threading
from datetime import datetime

numThreads = 2

# Nintendo switch, PS5, Xbox Series S, MSI GAMING PC, Corsair Gaming PC, ROG Gaming PC
urls = [
    "https://www.newegg.com/white-hegskaaaa-nintendo-switch-console/p/N82E16878190943",
    "https://www.newegg.com/p/N82E16868110298",
    "https://www.newegg.com/p/N82E16868105280",
    "https://www.newegg.com/msi-mpg-trident-as-12td-030us/p/N82E16883152973",
    "https://www.newegg.com/abs-ali646/p/N82E16883360311",
    "https://www.newegg.com/asus-ga15dk-ib778-rog-strix-ga15/p/N82E16883221709"
]

# array to store each product log
logs = ["", "", "", "", "", ""]


def getTime():
    # timezone formatting
    utcTime = datetime.utcnow()
    return utcTime.strftime('%Y-%m-%d %H:%M:%S')


# handles http get requests, uses mutex lock to isolate the critical section
def checkNeweggStock(url, lock):
    local = "http://localhost:5000/api/v1/request"
    jsonData = {"apikey": "cffb0029-bbfe-40c0-8f20-fc76c15fd51b",
                "url": url}
    lock.acquire()
    response = requests.post(local, json=jsonData)
    lock.release()
    # string holding all HTML code
    return str(response.content)


def newEgg(url, lock):
    # HTML Response Data
    htmlResponse = checkNeweggStock(url, lock)

    # status of labels
    inStock = bool(htmlResponse[htmlResponse.index('"Instock"') +
                           10:htmlResponse.index('"Stock"') - 1])
    price = htmlResponse[htmlResponse.index('"FinalPrice":') + 13:htmlResponse.index('"Instock"') - 1]
    shipping = htmlResponse[htmlResponse.index('"ShippingCharge"') + 17:htmlResponse.index('"VFAvail"') - 1]
    quantity = int(htmlResponse[htmlResponse.index('"Qty":')+6:htmlResponse.index('"UnitCost"') - 1])
    productName = htmlResponse[htmlResponse.index('<title>') + 7:htmlResponse.index('</title>') - 13]

    currentTime = getTime()

    if inStock:
        # combine the parsed string fragments together
        inStockLog = currentTime + " NEWEGG - " + productName + ' | Price: $' + str(price) + ' Shipping Cost: $' + str(
            shipping) + ' Quantity: ' + str(quantity)
        logs[urls.index(url)] = inStockLog
    else:
        logs[urls.index(url)] = currentTime + " NEWEGG - " + productName + " | OUT OF STOCK"


# prints each stock log
def printLogs(log):
    print(log)


while True:
    # any error that may occur will either be caused by spam detection or website traffic/outage
    try:
        # initialize mutex lock
        lock = threading.Lock()
        # executes item stock-checking in parallel for each url in the url array
        for i in range(len(urls)):
            thread = threading.Thread(target=newEgg, args=(urls[i], lock,))
            thread.start()

        # joins threads together when done. newEgg() will not run anymore in this iteration
        for i in range(len(urls)):
            thread.join()

        # previous join forces program to wait for each thread to finish
        # now the threads are utilized to print messages to console in parallel
        for i in range(len(urls)):
            thread = threading.Thread(target=printLogs, args=(logs[i], ))
            thread.start()

        # ensures program will not advance until all item stock messages are printed, joins threads together
        for i in range(len(urls)):
            thread.join()
    except:
        # handles any error that may occur as stated above, and quits the program accordingly.
        print('Detected by captcha! Exiting program.')
        quit()

    # new line for tidiness
    print()

    # program waits a random amount of time between 3.0 to 6.0 seconds
    # theoretically, less likely to activate website captcha that would break the program
    time.sleep(random.uniform(3, 6))
