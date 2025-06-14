import mysql.connector
import os

#Establishes connection to the remote database
def Connect_db():
    # db = mysql.connector.connect(
    #     host = "database-1.cruuhuufksbu.eu-north-1.rds.amazonaws.com",
    #     user = "admin",
    #     password = "Tamer2006",
    #     database = "Shopper"
    # )
    # return db
    try:
        db = mysql.connector.connect(
            host = "localhost",
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database = "Shopper",
            use_pure=True,
        )
        print("✅ Connection Successful!")
    except mysql.connector.Error as err:
        print("❌ Connection Failed:", err)
    return db

class Product():
    def __init__(self, ProductID, CategoryName, ProductName, SuperMarket, ProductPrice, ProductPPI, Image, UpdateDate, Offer = None):
        self.ProductID = ProductID
        self.CategoryName = CategoryName
        self.ProductName = ProductName
        self.SuperMarket = SuperMarket
        self.ProductPrice = ProductPrice
        self.ProductPPI = ProductPPI
        self.Image = Image
        self.__Offer = Offer
        self.UpdateDate = UpdateDate

    #Getters and setters
    def getProductID(self):
        return self.ProductID

    def getCategoryName(self):
        return self.CategoryName

    def getProductName(self):
        return self.ProductName 

    def getSuperMarket(self):
        return self.SuperMarket
    
    def getProductPrice(self):
        return self.ProductPrice
    
    def getProductPPI(self):
        return self.ProductPPI
    
    def getImage(self):
        return self.Image
    
    def getOffer(self):
        return self.__Offer

    def getUpdateDate(self):
        return self.UpdateDate

    #Insert, update and delete products using object data
    def Insert(self):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "INSERT INTO Product(CategoryName, ProductName, SuperMarket, ProductPrice, ProductPPI, Image, Offer, UpdateDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (self.getCategoryName(), self.getProductName(), self.getSuperMarket(), self.getProductPrice(), self.getProductPPI(), self.getImage(), self.getOffer(), self.getUpdateDate())
        connection.execute(Query, values)
        db.commit()
        connection.close()

    def Update(self):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "Update Product SET CategoryName = %s, SuperMarket = %s, ProductPrice = %s, ProductPPI = %s, Image = %s, Offer = %s, UpdateDate = %s WHERE ProductName = %s"
        values = (self.getCategoryName(), self.getSuperMarket(), self.getProductPrice(), self.getProductPPI(), self.getImage(), self.getOffer(), self.getUpdateDate(), self.getProductName())
        connection.execute(Query, values)
        db.commit()
        connection.close()

    @staticmethod
    def DeleteOldProducts():
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "DELETE FROM Product WHERE UpdateDate < DATE_SUB(NOW(), INTERVAL 1 MONTH)"
        connection.execute(Query)
        db.commit()
        connection.close()

    #Select product based of of it's ID
    @staticmethod
    def SelectProduct(ProductID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "Select * FROM Product WHERE ProductID = %s"
        Values = (ProductID,)
        connection.execute(Query, Values)
        product = connection.fetchone()
        product = Product(product[0],product[1],product[2],product[3],product[4],product[5],product[6],product[8],product[7])
        connection.close()
        return product
    
    @staticmethod
    def CheckProduct(ProductName):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT ProductName FROM Product WHERE ProductName = %s"
        Value = (ProductName,)
        connection.execute(Query, Value)
        result = connection.fetchone()
        connection.close()
        if result:
            return True
        else:
            return False

    @staticmethod
    def SelectAllProducts(ProductIDs, BasketID):
        #Selects all product objects based on the ID connected with the BasketID in the OrderDetails and returns it's array
        #Also selects the quantity of the product from the orderDetails table
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = """
        SELECT DISTINCT Product.*, OrderDetails.Quantity
        FROM Product
        JOIN OrderDetails ON Product.ProductID = OrderDetails.ProductID
        JOIN Basket ON OrderDetails.BasketID = Basket.BasketID
        WHERE Product.ProductID IN ({}) AND Basket.BasketID = %s
        ORDER BY Product.ProductPrice ASC
        """.format(', '.join(['%s'] * len(ProductIDs)))
        #As MySQL requires the parameters to be stored in a %s, the .format function appends a %s in the ({}) WHERE condition, as the ProductID's list can be any length.
        connection.execute(Query, tuple(ProductIDs + [BasketID]))
        ProductList = connection.fetchall()
        products = [Product(product[0],product[1],product[2],product[3],product[4],product[5],product[6],product[8],product[7]) for product in ProductList]
        Quantities = [product[9] for product in ProductList]
        connection.close()
        return products, Quantities

    #Selectors for both supermarkets based off of the similarity to the ProductName or CategoryName and if the data was scraped today
    @staticmethod
    def SelectTesco(ProductList, ProductName):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        
        Query = "SELECT DISTINCT * FROM Product INNER JOIN Category ON Product.CategoryName = Category.CategoryName WHERE (Product.SuperMarket = 'Tesco' AND Product.ProductName LIKE CONCAT('%', %s, '%')) OR (Product.SuperMarket = 'Tesco' AND Category.CategoryName LIKE CONCAT('%', %s, '%')) ORDER BY ProductID ASC"
        # Query = "SELECT DISTINCT * FROM Product INNER JOIN Category ON Product.CategoryName = Category.CategoryName WHERE (Product.SuperMarket = 'Tesco' AND Product.ProductName LIKE CONCAT('%', %s, '%')) AND DATE(UpdateDate) = CURDATE() OR (Product.SuperMarket = 'Tesco' AND Category.CategoryName LIKE CONCAT('%', %s, '%')) AND DATE(UpdateDate) = CURDATE() ORDER BY ProductID ASC"
        Values = (ProductName, ProductName)
        connection.execute(Query, Values)
        productlist = connection.fetchall()
        for product in productlist:
            ProductList.append(Product(product[0],product[1],product[2],product[3],product[4],product[5],product[6],product[8],product[7]))
        connection.close()
        return ProductList
    
    @staticmethod
    def SelectSainsbury(ProductList, ProductName):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT DISTINCT * FROM Product INNER JOIN Category ON Product.CategoryName = Category.CategoryName WHERE (Product.SuperMarket = 'Sainsbury' AND Product.ProductName LIKE CONCAT('%', %s, '%')) OR (Product.SuperMarket = 'Sainsbury' AND Category.CategoryName LIKE CONCAT('%', %s, '%')) ORDER BY ProductID ASC"
        # Query = "SELECT DISTINCT * FROM Product INNER JOIN Category ON Product.CategoryName = Category.CategoryName WHERE (Product.SuperMarket = 'Sainsbury' AND Product.ProductName LIKE CONCAT('%', %s, '%')) AND DATE(UpdateDate) = CURDATE() OR (Product.SuperMarket = 'Sainsbury' AND Category.CategoryName LIKE CONCAT('%', %s, '%')) AND DATE(UpdateDate) = CURDATE() ORDER BY ProductID ASC"
        Values = (ProductName, ProductName)
        connection.execute(Query, Values)
        productlist = connection.fetchall()
        for product in productlist:
            ProductList.append(Product(product[0],product[1],product[2],product[3],product[4],product[5],product[6],product[8],product[7]))
        connection.close()
        
        return ProductList

    #Same but for offers
    @staticmethod
    def SelectTescoOffers(ProductList, ProductName):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT DISTINCT * FROM Product INNER JOIN Category ON Product.CategoryName = Category.CategoryName WHERE (Product.SuperMarket = 'Tesco' AND Product.ProductName LIKE CONCAT('%', %s, '%')) AND Offer IS NOT NULL OR (Product.SuperMarket = 'Tesco' AND Category.CategoryName LIKE CONCAT('%', %s, '%')) AND Offer IS NOT NULL ORDER BY ProductPrice ASC"
        # Query = "SELECT DISTINCT * FROM Product INNER JOIN Category ON Product.CategoryName = Category.CategoryName WHERE (Product.SuperMarket = 'Tesco' AND Product.ProductName LIKE CONCAT('%', %s, '%')) AND DATE(UpdateDate) = CURDATE() AND Offer IS NOT NULL OR (Product.SuperMarket = 'Tesco' AND Category.CategoryName LIKE CONCAT('%', %s, '%')) AND Offer IS NOT NULL AND DATE(UpdateDate) = CURDATE() ORDER BY ProductPrice ASC"
        Values = (ProductName, ProductName)
        connection.execute(Query, Values)
        productlist = connection.fetchall()
        for product in productlist:
            ProductList.append(Product(product[0],product[1],product[2],product[3],product[4],product[5],product[6],product[8],product[7]))
        connection.close()
        return ProductList
    
    @staticmethod
    def SelectSainsburyOffers(ProductList, ProductName):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT DISTINCT * FROM Product INNER JOIN Category ON Product.CategoryName = Category.CategoryName WHERE (Product.SuperMarket = 'Sainsbury' AND Product.ProductName LIKE CONCAT('%', %s, '%')) AND Offer IS NOT NULL OR (Product.SuperMarket = 'Sainsbury' AND Category.CategoryName LIKE CONCAT('%', %s, '%')) AND Offer IS NOT NULL ORDER BY ProductPrice ASC"
        # Query = "SELECT DISTINCT * FROM Product INNER JOIN Category ON Product.CategoryName = Category.CategoryName WHERE (Product.SuperMarket = 'Sainsbury' AND Product.ProductName LIKE CONCAT('%', %s, '%')) AND Offer IS NOT NULL AND DATE(UpdateDate) = CURDATE() OR (Product.SuperMarket = 'Sainsbury' AND Category.CategoryName LIKE CONCAT('%', %s, '%')) AND Offer IS NOT NULL AND DATE(UpdateDate) = CURDATE() ORDER BY ProductPrice ASC"
        Values = (ProductName, ProductName)
        connection.execute(Query, Values)
        productlist = connection.fetchall()
        for product in productlist:
            ProductList.append(Product(product[0],product[1],product[2],product[3],product[4],product[5],product[6],product[8],product[7]))
        connection.close()
        return ProductList

    #Merge sort of the 2 products based off of the price or the unit price of each item
    @staticmethod
    def MergeSort(ProductList, Order):
        if len(ProductList) > 1:
            halfway = len(ProductList)//2
            Left = ProductList[:halfway]
            Right = ProductList[halfway:]
            Product.MergeSort(Left, Order)
            Product.MergeSort(Right, Order)
            i = 0
            j = 0
            k = 0
            while i < len(Left) and j < len(Right):
                if Order == "Price" or Order == "ReversePrice":
                    if Left[i].getProductPrice()< Right[j].getProductPrice():
                        ProductList[k] = Left[i]
                        i += 1
                    else:
                        ProductList[k] = Right[j]
                        j += 1
                    k += 1
                elif Order == "PPI" or Order == "ReversePPI":
                    if Left[i].getProductPPI()< Right[j].getProductPPI():
                        ProductList[k] = Left[i]
                        i += 1
                    else:
                        ProductList[k] = Right[j]
                        j += 1
                    k += 1
            while i < len(Left):
                ProductList[k] = Left[i]
                i += 1
                k += 1
            while j < len(Right):
                ProductList[k] = Right[j]
                j += 1
                k += 1
        return ProductList
    
    #Reverses the stack to allow to search from high to low
    @staticmethod
    def ReverseStack(Products):
        tempStack = []
        while len(Products) > 0:
            tempStack.append(Products.pop())
        return tempStack