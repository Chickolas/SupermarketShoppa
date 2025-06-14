CREATE database IF NOT EXISTS Shopper;
Use Shopper;
CREATE TABLE IF NOT EXISTS Users (
    UserID INT PRIMARY KEY NOT NULL auto_increment,
    UserName VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    EmailVerified BOOL NOT NULL,
    Hash VARCHAR(32) NOT NULL,
    Salt VARCHAR(32) NOT NULL,
    Admin BOOL NOT NULL
);
CREATE TABLE IF NOT EXISTS Category (
    CategoryName VARCHAR(255) PRIMARY KEY NOT NULL,
    TescoURL VARCHAR(255) NOT NULL,
    SainsburyURL VARCHAR(511) NOT NULL
);
CREATE TABLE IF NOT EXISTS Product (
    ProductID INT PRIMARY KEY NOT NULL auto_increment,
    CategoryName VARCHAR(255) NOT NULL,
    ProductName VARCHAR(255) NOT NULL,
    SuperMarket VARCHAR(255) NOT NULL,
    ProductPrice DECIMAL(10, 2) NOT NULL,
    ProductPPI DECIMAL(10, 2) NOT NULL,
    Image VARCHAR(255),
    Offer VARCHAR(255),
    UpdateDate DATE NOT NULL,
    FOREIGN KEY (CategoryName) REFERENCES Category(CategoryName)
);
CREATE TABLE IF NOT EXISTS Basket (
    BasketID INT PRIMARY KEY NOT NULL auto_increment,
    UserID INT NOT NULL,
    EditDate DATE,
    IsActive BOOLEAN,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);
CREATE TABLE IF NOT EXISTS OrderDetails (
    BasketID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    PRIMARY KEY (ProductID, BasketID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (BasketID) REFERENCES Basket(BasketID)
);

CREATE TABLE IF NOT EXISTS Spending (
    SpendingID INT Primary Key NOT NULL auto_increment,
    BasketID INT NOT NULL,
    TescoTotal Decimal(10, 2) NOT NULL,
    SainsburyTotal Decimal(10, 2) NOT NULL,
    FOREIGN KEY (BasketID) REFERENCES Basket(BasketID)
);
CREATE TABLE IF NOT exists Type (
	TypeID INT Primary Key NOT NULL,
    TypeName VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS Friend (
    UserID INT,
    FriendID INT,
    TypeID INT,
    PRIMARY KEY (UserID, FriendID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (FriendID) REFERENCES Users(UserID),
    FOREIGN KEY (TypeID) REFERENCES Type(TypeID)
);

SELECT * FROM Users;
SELECT * FROM Category;
SELECT * FROM Product;
SELECT * FROM Basket;
SELECT * FROM OrderDetails;
SELECT * FROM Spending;
SELECT * FROM Type;
SELECT * FROM Friend;




