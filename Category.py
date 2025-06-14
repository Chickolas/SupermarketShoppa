from Product import Product, Connect_db
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from time import sleep
from decimal import Decimal, ROUND_HALF_UP
from datetime import date

class Category():
    def __init__(self, CategoryName, TescoURL, SainsburyURL):
        self.__CategoryName = CategoryName
        self.__TescoURL = TescoURL
        self.__SainsburyURL = SainsburyURL

    #Getters and setters
    def setCategoryName(self, CategoryName):
        self.__CategoryName = CategoryName

    def setTescoURL(self, TescoURL):
        self.__TescoURL = TescoURL

    def setSainsburyURL(self, SainsburyURL):
        self.__SainsburyURL = SainsburyURL

    def getCategoryName(self):
        return self.__CategoryName

    def getTescoURL(self):
        return self.__TescoURL
    
    def getSainsburyURL(self):
        return self.__SainsburyURL
    
    #Creation and update of category in the database based from object attributes
    def CreateCategory(self):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "INSERT INTO Category(CategoryName, TescoURL, SainsburyURL) VALUES (%s, %s, %s)"
        Values = (self.__CategoryName, self.__TescoURL, self.__SainsburyURL)
        connection.execute(Query, Values)
        db.commit()
        connection.close()

    def UpdateCategory(self):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "Update Category SET TescoURL = %s, SainsburyURL = %s WHERE CategoryName = %s"
        values = (self.getTescoURL(), self.getSainsburyURL(), self.getCategoryName())
        connection.execute(Query, values)
        db.commit()
        connection.close()

    #Scraping algorithm
    def ScrapeTesco(self):
        # Compile regex for the tesco price strings - Allows only the numbers to be gotten 
        price_regex = re.compile(".*beans-price__text$")
        ppi_regex = re.compile(".*beans-price__subtext$")

        # Configures the selenium webdriver to chrome and allows manipulations of the oprions before scraping
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("start-maximized")
        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        #driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36'})
        sleep(1)
        driver.get(self.getTescoURL())
        

        sleep(1) # Let the page load

        # Save the page to the soup variable through html parsing
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        #Find the page number from the html line including "pagination--button" and grabs the page reference
        try:
            page_number = re.search(r'\?page=(\d+)', soup.findAll("a", class_ = "pagination--button")[-2].get("href")).group(1)
        except:
            page_number = 1

        # Get the product grid
        for i in range(1, int(page_number) + 1):
            options = webdriver.ChromeOptions()
            options.add_argument("--window-size=1920,1080")
            options.add_argument("start-maximized")
            driver = webdriver.Chrome(options=options)
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36'})
            #Simulates the use of the websites from another device to maske the scraping as a person by overriding the default User agent string to a custom one
            
            driver.get(self.getTescoURL() + "?page=" + str(i))
            
            sleep(5) # Let the page load fully before trying to grab information

            # Parse page
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            grid = soup.find("ul", attrs={"class":"product-list grid"})
            products = grid.find_all("li")

            # Selection of all required elements from the product grid 
            for product in products:
                try:
                    #Each product is stored 3 div elements from the item in the list
                    product = product.div.div.div

                    #Using the beautiful soup find function all relevant information is than grabbed from their html elements and standardised in the samme formats
                    image = product.img.get("src")
                    name = product.find("a", attrs={"data-auto":"product-tile--title"}).span.get_text().strip()
                    price = product.find("p", class_ = price_regex).get_text().strip()[1:]        
                    ppi = product.find("p", class_ = ppi_regex).get_text().strip()
                    if "£" in ppi:
                        ppi = ppi.replace("£", "")
                        if "each" in ppi:
                            ppi = ppi.replace("/each", "")
                        if "litre" in ppi:
                            ppi = ppi.replace("/litre", "")
                        if "kg" in ppi:
                            ppi = ppi.replace("/kg", "")
                        if "ml" in ppi:
                            ppi = ppi.replace("/100ml", "")
                            ppi = Decimal(ppi)*10

                    if "p" in ppi:
                        ppi = ppi.replace("p / ea", "")
                        if "g" or "ml" in ppi:
                            ppi = ppi.replace("p / 100g", "")
                            ppi = ppi.replace("p / 100ml", "")
                            ppi = Decimal(ppi)*10
                        if "ltr" in ppi:
                            ppi = ppi.replace("p / ltr", "")
                        ppi = Decimal(ppi)/100
                    ppi = Decimal(ppi).quantize(Decimal("0.00"), ROUND_HALF_UP)
                    

                    #Check if the product already exists in the database and updates the values if it is
                    InDatabase = Product.CheckProduct(name)

                    #Offer is attempted to be gotten from the item, If one doesnt exist an exception is raised
                    offer = product.find("span", class_ = "offer-text").get_text()
                    item = Product("", self.getCategoryName(), name, "Tesco", price, ppi, image, date.today(), offer)
                    #Each item is made into an object

                    #If the name and price are scraped (meaning they were available on that day) they are than
                    if name is not None and price is not None:
                        if InDatabase:
                            item.Update()
                        else:
                            item.Insert()
                    name,price = None,None
                    
                except:
                    #If offer is unavailable the product is remade without the offer and than either updated or inserted if the product already exists or not
                    try:
                        item = Product("", self.getCategoryName(), name, "Tesco", price, ppi, image, date.today(), None)
                        if name is not None and price is not None:
                            if InDatabase:
                                item.Update()
                            else:
                                item.Insert()
                        name,price = None,None
                    except:
                        #If the product shows a "This product is currently unavailable" text, another exception is raised and the product is skipped
                        pass

    def ScrapeSainsbury(self):            
        # Configure webdriver
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("start-maximized")
        driver = webdriver.Chrome(options=options)
        #driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36'})
        sleep(1)
        driver.get(self.getSainsburyURL())

        # Load page
        sleep(1) # Let the page load

        # Parse page
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        try: 
            page_number = soup.find("a", attrs={"rel":"last"}).get_text()
        except:
            page_number = 1

        for i in range(1,int(page_number)+1):
            options = webdriver.ChromeOptions()
            options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
            options.add_argument("start-maximized")  # ensure window is full-screen
            driver = webdriver.Chrome(options=options)
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
            driver.get(self.getSainsburyURL() + "/opt/page:" + str(i))
            sleep(5)

            # Parse page
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            grid = soup.find("ul", attrs={"class":"ln-o-grid ln-o-grid--matrix ln-o-grid--equal-height"})
            products = grid.find_all("li")

            for product in products:
                try:
                    #As each supermarket website is different, each piece of information is located differently in the element
                    name = product.find("a", class_ = "pt__link").get("title")
                    price = product.find("span", class_ = "pt__cost__retail-price").get_text().strip().replace("£", "") # remove the £
                    ppi = product.find("span", class_ = "pt__cost__unit-price-per-measure").get_text().strip()

                    #Standardisation of everything before storing it in the database allows for easier comparison later in the project
                    if "p" in price:
                        price = price.replace("p", "")
                        price = Decimal(price)/100
                        price = Decimal(price).quantize(Decimal("0.00"), ROUND_HALF_UP)

                    if "£" in ppi:
                        ppi = ppi.replace("£", "")
                        ppi = ppi.replace(" / ltr", "")
                        ppi = ppi.replace(" / kg", "")
                        if "100g" in ppi:
                            ppi = ppi.replace(" / 100g", "")
                            ppi = Decimal(ppi)*10
                        elif "100ml" in ppi:
                            ppi = ppi.replace(" / 100ml", "")
                            ppi = Decimal(ppi)*10
                        elif "500ml" in ppi:
                            ppi = ppi.replace(" / 500ml", "")
                            ppi = Decimal(ppi)*2 
                        elif "500ml" in ppi:
                            ppi = ppi.replace(" / 500ml", "")
                            ppi = Decimal(ppi)*2

                    elif "p" in ppi:
                        ppi = ppi.replace("p / ea", "")
                        ppi = ppi.replace("p / ltr", "")
                        if "100g" in ppi:
                            ppi = ppi.replace("p / 100g", "")
                            ppi = Decimal(ppi)*10
                        elif "100ml" in ppi:
                            ppi = ppi.replace("p / 100ml", "")
                            ppi = Decimal(ppi)*10
                        elif "500ml" in ppi:
                            ppi = ppi.replace("p / 500ml", "")
                            ppi = Decimal(ppi)*2       
                        elif "500g" in ppi:
                            ppi = ppi.replace("p / 500g", "")
                            ppi = Decimal(ppi)*2 

                        ppi = Decimal(ppi)/100
                        
                    ppi = Decimal(ppi).quantize(Decimal("0.00"), ROUND_HALF_UP)
                    image = product.img.get("src")

                    InDatabase = Product.CheckProduct(name)

                    offer = product.find("span", class_ = "pt__cost--price").get_text()

                    item = Product("", self.getCategoryName(), name, "Sainsbury", price, ppi, image, date.today(), offer)

                    if name is not None and price is not None:
                        if InDatabase:
                            item.Update()
                        else:
                            item.Insert()
                    name,price = None,None

                except:
                    try:
                        item = Product("", self.getCategoryName(), name, "Sainsbury", price, ppi, image, date.today(), None)
                        if name is not None and price is not None:
                            if InDatabase:
                                item.Update()
                            else:
                                item.Insert()
                        name,price = None,None
                    except:
                        pass
    #Creates all categories as objects from the category table in the database and appends them to the list
    @staticmethod
    def getCategories(CategoryList):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "Select * FROM Category"
        connection.execute(Query)
        categories = connection.fetchall()
        for category in categories:
            category = Category(category[0], category[1], category[2])
            CategoryList.append(category)
        connection.close()
        return CategoryList