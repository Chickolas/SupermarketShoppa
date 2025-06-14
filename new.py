# from Product import Product, Connect_db
# from bs4 import BeautifulSoup
# import re
# from selenium import webdriver
# from time import sleep
# from decimal import Decimal, ROUND_HALF_UP
# from datetime import date

# AsdaURL = "https://groceries.asda.com/aisle/chilled-food/milk-butter-cream-eggs/eggs/1215660378320-1215339432024-910000975407"

# def ScrapeAsda():
#         # Compile regex for the tesco price strings - Allows only the numbers to be gotten 
#         price_regex = re.compile(".*beans-price__text$")
#         ppi_regex = re.compile(".*beans-price__subtext$")

#         # Configures the selenium webdriver to chrome and allows manipulations of the oprions before scraping
#         options = webdriver.ChromeOptions()
#         options.add_argument("--window-size=1920,1080")
#         options.add_argument("start-maximized")
#         driver = webdriver.Chrome(options=options)
#         driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
#         #driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36'})
#         sleep(1)
#         driver.get(AsdaURL)
        

#         sleep(1) # Let the page load

#         # Save the page to the soup variable through html parsing
#         html = driver.page_source
#         soup = BeautifulSoup(html, 'html.parser')
#         #Find the page number from the html line including "pagination--button" and grabs the page reference
#         try:
#             page_number = re.search(r'\?page=(\d+)', soup.findAll("a", class_ = "pagination--button")[-2].get("href")).group(1)
#         except: 
#             page_number = 1

#         # Get the product grid
#         for i in range(1, int(page_number) + 1):
#             options = webdriver.ChromeOptions()
#             options.add_argument("--window-size=1920,1080")
#             options.add_argument("start-maximized")
#             driver = webdriver.Chrome(options=options)
#             driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36'})
#             #Simulates the use of the websites from another device to maske the scraping as a person by overriding the default User agent string to a custom one
            
#             driver.get(AsdaURL + "?page=" + str(i))
            
#             sleep(5) # Let the page load fully before trying to grab information

#             # Parse page
#             html = driver.page_source
#             soup = BeautifulSoup(html, 'html.parser')

#             grid = soup.find("ul", attrs={"class":" co-product-list__main-cntr"})
#             products = grid.find_all("li")

#             # Selection of all required elements from the product grid 
#             for product in products:
#                 try:
#                     #Each product is stored 3 div elements from the item in the list
#                     product = product.div.div.div

#                     #Using the beautiful soup find function all relevant information is than grabbed from their html elements and standardised in the samme formats
#                     image = product.img.get("src")
#                     name = product.find("a", attrs={"data-auto":"product-tile--title"}).span.get_text().strip()
#                     price = product.find("p", class_ = price_regex).get_text().strip()[1:]        
#                     ppi = product.find("p", class_ = ppi_regex).get_text().strip()
#                     if "£" in ppi:
#                         ppi = ppi.replace("£", "")
#                         if "each" in ppi:
#                             ppi = ppi.replace("/each", "")
#                         if "litre" in ppi:
#                             ppi = ppi.replace("/litre", "")
#                         if "kg" in ppi:
#                             ppi = ppi.replace("/kg", "")
#                         if "ml" in ppi:
#                             ppi = ppi.replace("/100ml", "")
#                             ppi = Decimal(ppi)*10

#                     if "p" in ppi:
#                         ppi = ppi.replace("p / ea", "")
#                         if "g" or "ml" in ppi:
#                             ppi = ppi.replace("p / 100g", "")
#                             ppi = ppi.replace("p / 100ml", "")
#                             ppi = Decimal(ppi)*10
#                         if "ltr" in ppi:
#                             ppi = ppi.replace("p / ltr", "")
#                         ppi = Decimal(ppi)/100
#                     ppi = Decimal(ppi).quantize(Decimal("0.00"), ROUND_HALF_UP)
                    

#                     # #Check if the product already exists in the database and updates the values if it is
#                     # InDatabase = Product.CheckProduct(name)

#                     # #Offer is attempted to be gotten from the item, If one doesnt exist an exception is raised
#                     # offer = product.find("span", class_ = "offer-text").get_text()
#                     # item = Product("", self.getCategoryName(), name, "Tesco", price, ppi, image, date.today(), offer)
#                     # #Each item is made into an object

#                     # #If the name and price are scraped (meaning they were available on that day) they are than
#                     # if name is not None and price is not None:
#                     #     if InDatabase:
#                     #         item.Update()
#                     #     else:
#                     #         item.Insert()
#                     # name,price = None,None
                    
#                 except:
#                     print("pasd")
#                     # #If offer is unavailable the product is remade without the offer and than either updated or inserted if the product already exists or not
#                     # try:
#                     #     item = Product("", self.getCategoryName(), name, "Tesco", price, ppi, image, date.today(), None)
#                     #     if name is not None and price is not None:
#                     #         if InDatabase:
#                     #             item.Update()
#                     #         else:
#                     #             item.Insert()
#                     #     name,price = None,None
#                     # except:
#                     #     #If the product shows a "This product is currently unavailable" text, another exception is raised and the product is skipped
#                     #     pass

# a = ScrapeAsda()
