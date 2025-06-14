from Product import Connect_db
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id_, UserName, Email, Hash, Salt, __admin = False):
        #Initialises Users atributes
        self.id = id_
        self.UserName = UserName
        self.Email = Email
        self.__EmailVerified = False
        self.__Hash = Hash
        self.__Salt = Salt
        self.__admin = __admin

    #Getter methods 
    def getHash(self):
        return self.__Hash
    
    def getUserName(self):
        return self.UserName
    
    def getSalt(self):
        return self.__Salt
    
    def getAdmin(self):
        return self.__admin

    def getID(self):
        return self.id
    
    #Sets admin
    def setAdmin(self, Admin):
        self.__admin = Admin

    #Insert the user object into the database
    def CreateUser(self):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "INSERT INTO Users(UserID, UserName, Email, EmailVerified, Hash, Salt, Admin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (self.getID(), self.getUserName(), self.Email, self.__EmailVerified, self.getHash(), self.getSalt(), self.getAdmin())
        connection.execute(Query, values)
        db.commit()
        connection.close()

    #Methods for friend relationships - (add, accept, remove, block) 
    def AddFriend(self, FriendID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "INSERT INTO Friend (UserID, FriendID, TypeID) VALUES (%s ,%s, 1)"
        values = (self.id, FriendID)
        connection.execute(Query,values)
        db.commit()
        connection.close()
    
    def AcceptFriendRequest(self, FriendID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "UPDATE Friend SET TypeID=2 WHERE (UserID=%s AND FriendID=%s) or (UserID=%s AND FriendID=%s)"
        values = (self.id, FriendID, FriendID, self.id)
        connection.execute(Query,values)
        db.commit()
        connection.close()

    def RemoveFriend(self, FriendID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "DELETE FROM Friend WHERE (UserID = %s and FriendID = %s) or (UserID = %s and FriendID = %s)"
        values = (self.id, FriendID, FriendID, self.id)
        connection.execute(Query,values)
        db.commit()
        connection.close()

    def BlockFriend(self, FriendID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "UPDATE Friend SET TypeID=3 WHERE (UserID=%s AND FriendID=%s)"
        values = (self.id, FriendID)
        connection.execute(Query,values)
        Query = "UPDATE Friend SET TypeID=4 WHERE (FriendID=%s AND UserID=%s)"
        values = (self.id, FriendID)
        connection.execute(Query,values)
        db.commit()
        connection.close()

    #Returns true or false after checking if 2 users are
    def CheckFriends(self, FriendID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT * FROM Friend WHERE (UserID = %s AND FriendID = %s AND TypeID = 2) OR (FriendID = %s AND UserID = %s AND TypeID = 2)"
        values = (self.id, FriendID, self.id, FriendID)
        connection.execute(Query, values)
        result = connection.fetchone()
        connection.close()
        if result:
            return True
        else:
            return False

    #Check if the user is blocked    
    def isBlocked(self, FriendID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT * FROM Friend WHERE (UserID = %s AND FriendID = %s AND TypeID = 4) OR (FriendID = %s AND UserID = %s AND TypeID = 3)"
        values = (self.id, FriendID, self.id, FriendID)
        connection.execute(Query, values)
        result = connection.fetchone()
        connection.close()
        if result:
            return True
        else:
            return False
    
    #Returns all users objects that the currentuser has blocked
    def getBlocked(self, Blocked):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT * FROM Friend WHERE (FriendID = %s AND TypeID = 4) OR (UserID = %s AND TypeID = 3)"
        values = (self.id, self.id)
        connection.execute(Query, values)
        userlist = connection.fetchall()
        for user in userlist:
            if user[2] == 4:
                CurrentUser = User.getUser(user[0])
                Blocked.append(CurrentUser)
            else:
                CurrentUser = User.getUser(user[1])
                Blocked.append(CurrentUser)
        connection.close()
        return Blocked        
        

    #Returns all Friends in an array and all Friend request in an array and returns them as User objects
    def getAllFriends(self, Friend, Request):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT * FROM Friend WHERE (UserID = %s OR FriendID = %s) AND (TypeID = 1 or TypeID = 2)"
        values = (self.id, self.id)
        connection.execute(Query, values)
        userlist = connection.fetchall()
        for user in userlist:
            if user[2] == 1 and user[1] == self.id:
                CurrentUser = User.getUser(user[0])
                Request.append(CurrentUser)
            elif user[0] != self.id and user[2] == 2:
                CurrentUser = User.getUser(user[0])
                Friend.append(CurrentUser)
            elif user[1] != self.id and user[2] == 2:
                CurrentUser = User.getUser(user[1])
                Friend.append(CurrentUser)
        connection.close()
        return Friend, Request
    
    #Grabs all Friend requests and returns the objects as an array
    def getAllFriendRequests(self, Request):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT * FROM Friend WHERE (UserID = %s OR FriendID = %s) AND TypeID = %s"
        values = (self.id, self.id, 1)
        connection.execute(Query, values)
        userlist = connection.fetchall()
        for user in userlist:
            if user[2] == 1 and user[1] == self.id:
                CurrentUser = User.getUser(user[0])
                Request.append(CurrentUser)
        connection.close()
        return Request

    #Gets the assigned UserID once the current user is inputted into the database
    @staticmethod
    def getUserIDFromDatabase(Name):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT UserID FROM Users WHERE UserName = %s"
        values = (Name,)
        connection.execute(Query,values)
        UserID = connection.fetchone()
        connection.close()
        return UserID[0]

    #Returns user object from data stored in the database
    @staticmethod
    def getUserFromName(Name):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT * FROM Users WHERE UserName = %s"
        values = (Name,)
        connection.execute(Query,values)
        user = connection.fetchone()
        connection.close()
        if not user:
            return None
        
        CurrentUser = User(id_=user[0], UserName=user[1], Email=user[2], Hash=user[4], Salt=user[5])
        CurrentUser.setAdmin(user[6])
        return CurrentUser

    #Returns user object from the UserID
    @staticmethod
    def getUser(User_ID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT * FROM Users WHERE UserID = %s"
        values = (User_ID,)
        connection.execute(Query,values)
        user = connection.fetchone()
        connection.close()
        if not user:
            return None
        
        CurrentUser = User(id_=user[0], UserName=user[1], Email=user[2], Hash=user[4], Salt=user[5])
        CurrentUser.setAdmin(user[6])
        return CurrentUser

    #Returns all users as objects
    @staticmethod
    def getAllUsers(array):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT * FROM Users"
        connection.execute(Query)
        userlist = connection.fetchall()
        for user in userlist:
            CurrentUser = User(id_=user[0], UserName=user[1], Email=user[2], Hash=user[4], Salt=user[5])
            CurrentUser.setAdmin(user[6])
            array.append(CurrentUser)
        connection.close()
        return array
    
    @staticmethod
    def CheckEmail(Email):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT * FROM Users WHERE Email = %s"
        values = (Email,)
        connection.execute(Query, values)
        result = connection.fetchone()
        connection.close()
        if result:
            return True
        else:
            return False

    @staticmethod        
    def CreateHash(Password,salt):
        prime1 = 4022856527 
        prime2 = 3872603072089  
        #2 Randomly generated prime numbers with 2 different lengths
        Password = Password + salt
        #Addition of salt to password before hashing  stops the use of rainbow tables to crack a hashing algorithm as 2 of the same passwords would have different hashes
        # Initialize list as 1, use a different variable name instead of shadowing the built-in list type
        hash = 1
        for digit in Password:
            hash *= (ord(digit) + prime1 + prime2) * (Password.index(digit) + 1)
            #Using the 2 randomly generated prime numbers and the position of each character in the password to create the hash
        # Convert to hexadecimal
        hash = hex(hash)
        # Convert the hash into a fixed lenth of 32 and return it
        if len(hash) < 36:
            hash = hash[2:] + "0" * (36 - len(hash))
        elif len(hash) > 36:
            hash = hash[2:18] + hash[20:36]
        return hash

    #Generates a string of 16 characters consisting of random characters
    @staticmethod
    def GenerateSalt(length=16):
        import os
        return os.urandom(length)
a = User.GenerateSalt().hex()
print(a, User.CreateHash(str(1234), a))