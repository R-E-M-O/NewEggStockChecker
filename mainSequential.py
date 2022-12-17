import requests
import time
import random
from datetime import datetime

# Nintendo switch, PS5, Xbox Series S, MSI GAMING PC, Corsair Gaming PC, ROG Gaming PC
urls = [
    "https://www.newegg.com/white-hegskaaaa-nintendo-switch-console/p/N82E16878190943",
    "https://www.newegg.com/p/N82E16868110298",
    "https://www.newegg.com/p/N82E16868105280",
    "https://www.newegg.com/msi-mpg-trident-as-12td-030us/p/N82E16883152973",
    "https://www.newegg.com/abs-ali646/p/N82E16883360311",
    "https://www.newegg.com/asus-ga15dk-ib778-rog-strix-ga15/p/N82E16883221709"
]


# handles http get requests
def checkNewEggStock(url):
    local = "http://localhost:5000/api/v1/request"
    jsonData = {"apikey": "cffb0029-bbfe-40c0-8f20-fc76c15fd51b",
                "url": url}
    response = requests.post(local, json=jsonData)
    # string holding all HTML code
    return str(response.content)


def getTime():
    # timezone formatting
    utcTime = datetime.utcnow()
    formattedEDT = utcTime.strftime('%Y-%m-%d %H:%M:%S')
    return formattedEDT


def newEgg(url):
    # HTML Response Data
    htmlResponse = checkNewEggStock(url)

    # status of labels
    inStock = bool(htmlResponse[htmlResponse.index('"Instock"') +
                           10:htmlResponse.index('"Stock"') - 1])
    price = htmlResponse[htmlResponse.index('"FinalPrice":') + 13:htmlResponse.index('"Instock"') - 1]
    shipping = htmlResponse[htmlResponse.index('"ShippingCharge"') + 17:htmlResponse.index('"VFAvail"') - 1]
    quantity = int(htmlResponse[htmlResponse.index('"Qty":') + 6:htmlResponse.index('"UnitCost"') - 1])
    productName = htmlResponse[htmlResponse.index('<title>') + 7:htmlResponse.index('</title>') - 13]

    currentTime = getTime()
    inStockLog: str

    if inStock:
        inStockLog = currentTime + " NEWEGG - " + productName + ' | Price: $' + str(
            price) + ' Shipping Cost: $' + str(
            shipping) + ' Quantity: ' + str(quantity)
    else:
        inStockLog = currentTime + " NEWEGG - " + productName + " | OUT OF STOCK"

    return inStockLog


def bestBuy():
    url = 'https://www.bestbuy.com/site/msi-nvidia-geforce-rtx-4090-gaming-trio-24g-24gb-ddr6x-pci-express-4-0-graphics-card/6522371.p?skuId=6522371'
    local = "http://localhost:5000/api/v1/request"
    jsonData = {"apikey": "cffb0029-bbfe-40c0-8f20-fc76c15fd51b",
                "url": url}
    response = requests.post(local, json=jsonData)
    responseText = response.text

    # string holding all HTML code
    productName = responseText[responseText.index('<title >') + 8: responseText.index('</title>')]
    return productName


while True:
    try:
        print(bestBuy())
        for i in range(len(urls)):
            print(newEgg(urls[i]))
    except:
        print('Detected by captcha! Exiting program.')
        quit()

    print()
    time.sleep(random.uniform(3, 6))
