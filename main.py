import requests
import time
import random
import threading
import numpy as np
from datetime import datetime

numThreads = 6

# array of urls to check
urls = [
    "https://www.newegg.com/white-hegskaaaa-nintendo-switch-console/p/N82E16878190943", #Nintendo switch
    "https://www.newegg.com/p/N82E16868110298", #PS5
    "https://www.newegg.com/p/N82E16868105280", #Xbox Series S
    "https://www.newegg.com/msi-mpg-trident-as-12td-030us/p/N82E16883152973", #MSI GAMING PC
    "https://www.newegg.com/abs-ali646/p/N82E16883360311", #Corsair Gaming PC
    "https://www.newegg.com/asus-ga15dk-ib778-rog-strix-ga15/p/N82E16883221709" #ROG Gaming PC
]

urlChunks = np.array_split(urls, numThreads)

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
    #lock.acquire()
    response = requests.post(local, json=jsonData)
    #lock.release()

    # string holding all HTML code
    return str(response.content)



def newEgg(lock, urlChunk, tid):
    # Loop through the URLs array for this thread
    for i in range(len(urlChunk)):
        lock.acquire()
        # HTML Response Data
        htmlResponse = checkNeweggStock(urlChunk[i], lock)

        # Parse the relevant information from the HTML response
        inStock = bool(htmlResponse[htmlResponse.index('"Instock"') + 10:htmlResponse.index('"Stock"') - 1])
        price = htmlResponse[htmlResponse.index('"FinalPrice":') + 13:htmlResponse.index('"Instock"') - 1]
        shipping = htmlResponse[htmlResponse.index('"ShippingCharge"') + 17:htmlResponse.index('"VFAvail"') - 1]
        quantity = int(htmlResponse[htmlResponse.index('"Qty":')+6:htmlResponse.index('"UnitCost"') - 1])
        productName = htmlResponse[htmlResponse.index('<title>') + 7:htmlResponse.index('</title>') - 13]

        currentTime = getTime()

        if inStock:
            # Create the log message for in-stock items
            inStockLog = f"{currentTime} NEWEGG - {productName} | Price: ${price} Shipping Cost: ${shipping} Quantity: {quantity}"

            # Store the log message in the appropriate index of the logs array
            logs[(len(urlChunk)*tid) + i] = inStockLog
        else:
            # Create the log message for out-of-stock items
            outOfStockLog = f"{currentTime} NEWEGG - {productName} | OUT OF STOCK"
            # Store the log message in the appropriate index of the logs array
            logs[(len(urlChunk)*tid) + i] = outOfStockLog
        lock.release()
    


# prints logs in parallel
def printLogs(logChunk):
    for i in range(len(logChunk)):
        print(logChunk[i])



# will not let numThreads exceed the number of urls; waste of resources
if numThreads > len(urls):
    numThreads = len(urls)

while True:
    # any error that may occur will either be caused by spam detection or website traffic/outage
    try:
        # initialize mutex lock
        lock = threading.Lock()

        # create threads to handle each url
        for i in range(numThreads):
            thread = threading.Thread(target=newEgg, args=(lock, urlChunks[i], i))
            thread.start()

        # joins threads together when done. newEgg() will not run anymore in this iteration
        for i in range(numThreads):
            thread.join()

        # logs are split into chunks to be printed by threads in parallel
        logChunks = np.array_split(logs, numThreads)

        # now the threads are utilized to print messages to console in parallel
        for i in range(numThreads):
            thread = threading.Thread(target=printLogs, args=(logChunks[i], ))
            thread.start()
            

        # ensures program will not advance until all item stock messages are printed, joins threads together
        for i in range(numThreads):
            thread.join()

        print('------------------------------------')    


    except Exception as e:
        # handles any error that may occur as stated above, and quits the program accordingly.
        print('Detected by captcha! Exiting program.')
        print(e)
        quit()


    # program waits a random amount of time between 3.0 to 6.0 seconds
    # theoretically, less likely to activate website captcha that would break the program
    time.sleep(random.uniform(3, 6))
