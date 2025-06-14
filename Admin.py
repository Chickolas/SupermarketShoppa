from User import User
from Product import Connect_db

class Admin(User):
    #Inheritance of all methods and attributes of the User class
    def __init__(self, id_, UserName, Email, Hash, Salt, __admin=True):
        super().__init__(id_, UserName, Email, Hash, Salt, __admin)
    
    #Polymorphism of the setAdmin method to make another user an admin
    def setAdmin(self, UserID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "Update Users SET Admin = %s WHERE UserID = %s"
        values = (True, UserID)
        connection.execute(Query, values)
        db.commit()
        connection.close()

    def removeAdmin(self, UserID):
        if UserID == 1:
            pass
        else:
            db = Connect_db()
            connection = db.cursor(buffered=True)
            Query = "Update Users SET Admin = %s WHERE UserID = %s"
            values = (False, UserID)
            connection.execute(Query, values)
            db.commit()
            connection.close()