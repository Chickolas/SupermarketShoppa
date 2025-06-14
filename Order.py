from Product import Connect_db

class OrderDetails():
    def __init__(self, BasketID, ProductID, Quantity):
        self.BasketID = BasketID
        self.__ProductID = ProductID
        self.Quantity = Quantity

    #Getters and setters
    def getProductID(self):
        return self.__ProductID
    
    def getQuantity(self):
        return self.Quantity
    
    def setQuantity(self, Quantity):
        self.Quantity = Quantity
    
    #Manipulation of objects to the OrderDetails database - Add,remove and update
    def AddOrder(self):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "INSERT INTO OrderDetails(BasketID, ProductID, Quantity) VALUES(%s, %s, %s)"
        values = (self.BasketID, self.getProductID(), self.getQuantity())
        connection.execute(Query, values)
        db.commit()
        connection.close()
    
    def RemoveOrder(self):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "DELETE FROM OrderDetails WHERE ProductID = %s"
        values = (self.getProductID(),)
        connection.execute(Query, values)
        db.commit()
        connection.close()

    def UpdateOrder(self):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "Update OrderDetails SET Quantity = %s WHERE BasketID = %s AND ProductID = %s"
        values = (self.getQuantity(), self.BasketID, self.getProductID())
        connection.execute(Query, values)
        db.commit()
        connection.close()

    #Select individual order in a basket and create it's object
    @staticmethod
    def SelectOrder(ProductID, BasketID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT * FROM OrderDetails WHERE ProductID = %s AND BasketID = %s"
        values = (ProductID, BasketID)
        connection.execute(Query, values)
        order = connection.fetchone()
        try:
            Order = OrderDetails(BasketID, ProductID, order[2])
            connection.close()
            return Order
        except:
            connection.close()
            return None

    #Selects all orders in a basket and orders by ProductID
    @staticmethod
    def SelectAllOrders(BasketID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "Select * FROM OrderDetails WHERE BasketID = %s ORDER BY ProductID ASC"
        Values = (BasketID,)
        connection.execute(Query, Values)
        OrderList = connection.fetchall()
        Orders = [OrderDetails(order[0], order[1], order[2]) for order in OrderList]
        connection.close()
        return Orders
    
    #Cross table SQL to select the quantity from the OrderDetails table and the ProductName from the Product table if it matches the BasketID
    @staticmethod
    def SelectAllProductNamesAndQuantities(BasketID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "Select Product.ProductName, OrderDetails.Quantity FROM OrderDetails, Product WHERE OrderDetails.BasketID = %s AND OrderDetails.ProductID = Product.ProductID ORDER BY OrderDetails.Quantity ASC"
        Values = (BasketID,)
        connection.execute(Query, Values)
        OrderList = connection.fetchall()
        connection.close()
        return OrderList