from Product import Connect_db
from datetime import date

class Basket():
    def __init__(self, BasketID, UserID, EditDate, IsActive):
        self.BasketID = BasketID 
        self.UserID = UserID
        self.EditDate = EditDate
        self.IsActive = IsActive

    #Getters and setters for use of the attributes in the main program
    def getBasketID(self):
        return self.BasketID

    def getUserID(self):
        return self.UserID
    
    def getEditDate(self):
        return self.EditDate
    def getActive(self):
        return self.IsActive

    def setInactive(self):
        self.IsActive = False

    def setEditDate(self):
        self.EditDate = date.today()

    #Updates all values in the basket to the database
    def UpdateBasket(self):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "UPDATE Basket Set EditDate = %s, IsActive = %s Where BasketID = %s"
        values = (self.getEditDate(), self.getActive(), self.getBasketID())
        connection.execute(Query, values)
        db.commit()
        connection.close()

    #Inserts the current basket object into the Basket table in the database.
    @staticmethod
    def CreateBasket(UserID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "INSERT INTO Basket(BasketID, UserID, EditDate, IsActive) VALUES(%s, %s, %s, %s)"
        values = ("", UserID, date.today(), True)
        connection.execute(Query, values)
        db.commit()
        connection.close()

    #Inactivates basket and updates it in table and then creates a new basket record assigned to the user
    def CheckOut(self):
        self.setInactive()
        self.setEditDate()
        self.UpdateBasket()
        self.CreateBasket(self.UserID)

    #Retrieves basket object from database based of of UserID or BasketID
    @staticmethod
    def getBasketFromUserID(UserID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "Select * FROM Basket, Users WHERE Basket.UserID = %s and Users.UserID = Basket.UserID AND Basket.IsActive = true"
        Values = (UserID,)
        connection.execute(Query, Values)
        CurrentBasket = connection.fetchone()
        if CurrentBasket:
            CurrentBasket = Basket(CurrentBasket[0],CurrentBasket[1],CurrentBasket[2],CurrentBasket[3])
        connection.close()
        return CurrentBasket
    
    @staticmethod
    def getBasketFromBasketID(BasketID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "Select * FROM Basket, Users WHERE Basket.BasketID = %s and Users.UserID = Basket.UserID"
        Values = (BasketID,)
        connection.execute(Query, Values)
        CurrentBasket = connection.fetchone()
        if CurrentBasket:
            CurrentBasket = Basket(CurrentBasket[0],CurrentBasket[1],CurrentBasket[2],CurrentBasket[3])
        connection.close()
        return CurrentBasket