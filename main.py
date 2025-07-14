#Importing Classes from other Files
from Product import Product
from User import User
from Basket import Basket
from Order import OrderDetails
from Category import Category
from Admin import Admin
from Spending import Spending
from PriorityQueue import PriorityQueue

#Additional Libraries used in the main program
#Flask imports
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, current_user, login_user, logout_user

#Basket offer imports
import re
from decimal import Decimal
import pickle

#Scheduler importsr
from apscheduler.schedulers.background import BackgroundScheduler


#Initialises the website in flask and set the scheduler's timezone
app = Flask(__name__, static_url_path='/static')

login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = "L6WKqDVEzu3PFlpjNxlFvmob2j_Shoppa"
scheduler = BackgroundScheduler(timezone="GMT")

#Loads user when website starts
@login_manager.user_loader
def load_user(user_id):
    user = User.getUser(user_id)
    if user.getAdmin() == True:
        #If the user is an admin, The user is converted to an admin object and then returned
        user = Admin(user.getID(), user.getUserName(), user.Email, hash, user.getSalt())
    return user

#Area where products are displayed and able to be added to basket
@app.route('/', methods=['GET', 'POST'])
def home():
    #If user isn't logged in, they are sent to the login page
    print(current_user)
    if current_user is None:
        return redirect(url_for('login'))
    elif not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    CurrentBasket = Basket.getBasketFromUserID(current_user.getID())
    session['Basket'] = pickle.dumps(CurrentBasket)

    if request.method == 'POST' and 'Search' in request.form:
        ProductName = request.form.get('ProductName')
        session['Product'] = ProductName
        #Stores Product choice in the session data to be gotten if the page is reloaded

    elif request.method == 'POST':
        Order = request.form.get('Orderby')
        Offer = request.form.get('Offer')
        session['Order'] = Order
        session['Offer'] = Offer

    Offer = session.get('Offer', None)
    ProductName = session.get('Product', None)
    Order = session.get('Order', None)
    #Stores the Offer selection, ProductName and Order in the session data

    if Order == None:
        Order = "Price"

    TescoProducts = []
    SainsburyProducts = []

    #If the offer box is selected, The SQL query changes to only select items from Sainsbury and Tesco where the product is not "Null"
    if Offer is not None:
        TescoProducts = Product.SelectTescoOffers(TescoProducts, ProductName)
        SainsburyProducts = Product.SelectSainsburyOffers(SainsburyProducts, ProductName)
    else:
        TescoProducts = Product.SelectTesco(TescoProducts, ProductName)
        SainsburyProducts = Product.SelectSainsbury(SainsburyProducts, ProductName)
       
    Products = TescoProducts + SainsburyProducts

    Products = Product.MergeSort(Products, Order)
    #Reverses stack if the user wants to search from High to Low

    if "Reverse" in Order:
        #Use of a stack to invert the product list. This allows the productlist to be saved in session data and not have to be reloaded from the database
        Products = Product.ReverseStack(Products)
    return render_template('home.html',current_user=current_user, Products = Products, Order=Order, Offer=Offer, ProductName=ProductName)

#Sends to login page
@app.route('/login')
def login():
    return render_template('login.html')

#Used to authenticate when login attempted
@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    user = User.getUserFromName(username)
    if user != None:
        #Checks if the user object is able to be created from the username given
        hash = User.CreateHash(request.form.get('password'), user.getSalt())
        if user.getHash() == hash:
            #Hash created and compared to the hash stored from account creation
            #Logs in users using FlaskLoginManager and remembers it between website restarts and when you close and open the website
            if user.getAdmin() == True:
                
                #If admin the user object is converted to an admin object and then logged in
                user = Admin(user.getID(), user.getUserName(), user.Email, hash, user.getSalt())
                login_user(user, remember=True, force=True)
                return redirect(url_for('home'))
            else:
                login_user(user, remember=True, force=True)
                return redirect(url_for('home'))
        else:
            flash('Password incorrect')
            return redirect(url_for('login'))
    flash('User does not exist')
    return redirect(url_for('login'))

#Clears session data and logs out of flask
@app.route('/logout', methods = ['GET'])
def logout():
    session.clear()
    logout_user()
    return redirect(url_for("home"))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('username')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    valid = True

    #Regular expressions to compare login requirements to inputted data
    if not re.search("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        flash("Email is invalid")
        valid = False
    
    if User.CheckEmail(email):
        flash("Email already in use")
        valid = False

    if len(password) < 8:
        flash("Password length must be 8 characters or more")
        valid = False
    if not re.search("[a-z]", password):
        flash("Password does not contain a lowercase letter")
        valid = False
    if not re.search("[A-Z]", password):
        flash("Password does not contain a uppercase letter")
        valid = False
    if not re.search("[0-9]", password):
        flash("Password does not contain number")
        valid = False
    if password != password2:
        flash("Passwords don't match")
        valid = False

    #If any of the requirements are invalid, the user is asked to reinput correct values
    if valid == True:
        #Salt generated and hashed with the password. Both hash and salt stored in database
        salt = User.GenerateSalt().hex()
        password = User.CreateHash(password, salt)
        CurrentUser = User(0, name, email, password, salt)

        #Checks if the User is already stored in the database and creates a new user if not
        if User.getUserFromName(CurrentUser.getUserName()) == None:
            #If the Username is unique, The user is added to the database and assigned a basket
            CurrentUser.CreateUser()
            Basket.CreateBasket(User.getUserIDFromDatabase(name))
            return redirect(url_for('login'))
        else:
            flash('Username already in use')
            return redirect(url_for('signup'))
    else:
        return redirect(url_for('signup')),

@app.route('/basket/<int:UserID>', methods=['GET', 'POST'])
def basket(UserID):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    #Checks if current user is the basket owner or friends with the basket owner
    if current_user.CheckFriends(UserID) == True or current_user.getID() == UserID:
        productIDs, Products, Quantities, Prices, = [], [], [], []
        TescoTotal, SainsburyTotal = 0, 0 
        OfferList, Queue= {}, {}

        try:
            #If an old basket is gotten, the Current basket object is gotten and deserialised
            CurrentBasket = pickle.loads(session.get('OldBasketID', None))
        except:
            CurrentBasket = Basket.getBasketFromUserID(UserID)
            if not CurrentBasket:
                Basket.CreateBasket(current_user.getID())
                CurrentBasket = Basket.getBasketFromUserID(UserID)
            session['Basket'] = pickle.dumps(CurrentBasket)

        Orders = OrderDetails.SelectAllOrders(CurrentBasket.getBasketID())
        session['OldBasketID'] = None
        #Old basket is removed after use
        if len(Orders) > 0:
            for order in Orders:
                productIDs.append(order.getProductID())
            ProductList, Quantities = Product.SelectAllProducts(productIDs, CurrentBasket.getBasketID())
            for index, (CurrentProduct, ItemQuantity) in enumerate(zip(ProductList, Quantities)):
                if CurrentProduct.getOffer() != None:
                    if 'for' in CurrentProduct.getOffer():
                        try:
                            #Regular expression used to identify offer type
                            price_pattern = r'(\d+)\s+for\s+(\d)'
                            Offer = re.search(price_pattern, CurrentProduct.getOffer())
                            if not Offer:
                                raise Exception
                                #If the Offer does not match, an exception is raised so other offer checks can be carried out

                            #Offer stored in a dictionary identified by offer name. 
                            #This stores the offer details, Total item quantity of the offerholders and 
                            if CurrentProduct.getOffer() not in OfferList:
                                OfferList[CurrentProduct.getOffer()] = {
                                    'OfferName': CurrentProduct.getOffer(),
                                    'ItemQuantity': ItemQuantity,
                                    'OfferQuantity': int(Offer.group(1)),
                                    'Offer': int(Offer.group(2)),
                                    'LowestPrice': Decimal(CurrentProduct.getProductPrice()),
                                    'HighestPrice': Decimal(CurrentProduct.getProductPrice()),
                                    'Priority': 1
                                }
                                Queue[CurrentProduct.getOffer()] = PriorityQueue()
                                Queue[CurrentProduct.getOffer()].Add(1, index)
                                #Offer than added to the queue with the highest priority - as selected from the database from lowest to highest price
                            else:
                                OfferList[CurrentProduct.getOffer()]['ItemQuantity'] += ItemQuantity

                                if CurrentProduct.getProductPrice() < OfferList[CurrentProduct.getOffer()]['LowestPrice']:
                                    OfferList[CurrentProduct.getOffer()]['LowestPrice'] = CurrentProduct.getProductPrice()

                                elif CurrentProduct.getProductPrice() > OfferList[CurrentProduct.getOffer()]['HighestPrice']:
                                    OfferList[CurrentProduct.getOffer()]['HighestPrice'] = CurrentProduct.getProductPrice()
                                    OfferList[CurrentProduct.getOffer()]['Priority'] += 1
                                    Queue[CurrentProduct.getOffer()].Add(OfferList[CurrentProduct.getOffer()]['Priority'], index)
                                else:
                                    Queue[CurrentProduct.getOffer()].Add(OfferList[CurrentProduct.getOffer()]['Priority'], index)
                            #Product added to the priority queue based of price with the lowest price having the highest priority
                        except:
                            try:
                                price_pattern = r'(\d+)\s+for\s+£(\d+\.\d{2})'
                                Offer = re.search(price_pattern, CurrentProduct.getOffer())
                                if not Offer:
                                    raise Exception 
                            except:
                                price_pattern = r'(\d+)\s+for\s+£(\d+)'
                                Offer = re.search(price_pattern, CurrentProduct.getOffer())

                            #Same is done if the deal is multiple products for a particular price
                            if CurrentProduct.getOffer() not in OfferList:
                                OfferList[CurrentProduct.getOffer()] = {
                                    'OfferName': CurrentProduct.getOffer(),
                                    'ItemQuantity': ItemQuantity,
                                    'OfferQuantity': int(Offer.group(1)),
                                    'OfferAmount': Decimal(Offer.group(2)),
                                    'LowestPrice': Decimal(CurrentProduct.getProductPrice()),
                                    'HighestPrice': Decimal(CurrentProduct.getProductPrice()),
                                    'Priority': 1
                                }
                                Queue[CurrentProduct.getOffer()] = PriorityQueue()
                                Queue[CurrentProduct.getOffer()].Add(1, index)
                            else:
                                OfferList[CurrentProduct.getOffer()]['ItemQuantity'] += ItemQuantity

                                if CurrentProduct.getProductPrice() < OfferList[CurrentProduct.getOffer()]['LowestPrice']:
                                    OfferList[CurrentProduct.getOffer()]['LowestPrice'] = CurrentProduct.getProductPrice()
                                elif CurrentProduct.getProductPrice() > OfferList[CurrentProduct.getOffer()]['HighestPrice']:
                                    OfferList[CurrentProduct.getOffer()]['HighestPrice'] = CurrentProduct.getProductPrice()
                                    OfferList[CurrentProduct.getOffer()]['Priority'] += 1
                                    Queue[CurrentProduct.getOffer()].Add(OfferList[CurrentProduct.getOffer()]['Priority'], index)
                                else:
                                    Queue[CurrentProduct.getOffer()].Add(OfferList[CurrentProduct.getOffer()]['Priority'], index)
                        ItemPrice = CurrentProduct.getProductPrice() * ItemQuantity
                        Prices.append(ItemPrice)
                        #Regular price added to the ItemPrice array and than manipulated later

                    else:
                        try:
                            #Recalculations of Item price based on the 
                            price_pattern = r'£(\d+\.\d{2})'
                            Offer = re.search(price_pattern, CurrentProduct.getOffer()).group(1)
                            ItemPrice = Decimal(Offer) * ItemQuantity
                        except:
                            price_pattern = r'\d+p'
                            Offer = re.search(price_pattern, CurrentProduct.getOffer()).group(0)
                            ItemPrice = Decimal(CurrentProduct.getOffer()[:2])/100 * ItemQuantity
                        Prices.append(ItemPrice)
                else:
                    #Calculation of the Regular Item price if no offer is applied
                    ItemPrice = CurrentProduct.getProductPrice() * ItemQuantity
                    Prices.append(ItemPrice)

                #Each supermarket's Total is incremented based off of the price and the product is stored in the product array
                if CurrentProduct.getSuperMarket() == "Tesco":
                        TescoTotal += ItemPrice
                elif CurrentProduct.getSuperMarket() == "Sainsbury":
                    SainsburyTotal += ItemPrice
            
                Products.append(CurrentProduct)

            #Iterates through the queue dictionary and grabs the offer and the individual offer's priority queue    
            for offer, queue in Queue.items():
                ItemQuantity = OfferList[offer]['ItemQuantity']
                OfferTotal = ItemQuantity // OfferList[offer]['OfferQuantity']
                while not queue.isEmpty():
                    index = queue.get()[1]               
                    CurrentProduct = Products[index]
                    Quantity = Quantities[index]

                    #If the item's are combined to one price, The offer is verified to check if the total is reached and the correct ammount is applied to the first show product
                    if '£' in CurrentProduct.getOffer():
                        if OfferTotal != 0:
                            if ItemQuantity >= OfferTotal:
                                Prices[index] = Decimal(OfferTotal * OfferList[offer]['OfferAmount']  + (ItemQuantity % OfferList[offer]['OfferQuantity']) * CurrentProduct.getProductPrice())
                                if CurrentProduct.getSuperMarket() == "Tesco":
                                    TescoTotal -= (ItemQuantity*CurrentProduct.getProductPrice() - OfferTotal * OfferList[offer]['OfferAmount'])
                                elif CurrentProduct.getSuperMarket() == "Sainsbury":
                                    SainsburyTotal -= (ItemQuantity*CurrentProduct.getProductPrice() - OfferTotal * OfferList[offer]['OfferAmount'])
                                ItemQuantity = 0
                            else:
                                Prices[index] -= Prices[index]
                                #The price of any later products are than set to 0
                    else:
                        #else the order is changing the price of a number of items to the price of another amount
                        if OfferTotal != 0:
                            if Quantity >= OfferTotal:
                                Prices[index] = Decimal(Quantity * CurrentProduct.getProductPrice() - OfferTotal * CurrentProduct.getProductPrice())
                                if CurrentProduct.getSuperMarket() == "Tesco":
                                    TescoTotal -= OfferTotal * CurrentProduct.getProductPrice()
                                elif CurrentProduct.getSuperMarket() == "Sainsbury":
                                    SainsburyTotal -= OfferTotal * CurrentProduct.getProductPrice()
                            else:
                                if CurrentProduct.getSuperMarket() == "Tesco":
                                    TescoTotal -= Prices[index]
                                elif CurrentProduct.getSuperMarket() == "Sainsbury":
                                    SainsburyTotal -= Prices[index]
                                #New product prices are calculated and the Prices array is than 
                                Prices[index] = Prices[index]-Prices[index]
                            OfferTotal -= Quantity
            session['TescoTotal'] = TescoTotal
            session['SainsburyTotal'] = SainsburyTotal
            #Updates session data for each of the totals
        return render_template('basket.html',SainsburyTotal = SainsburyTotal, TescoTotal = TescoTotal, Products = Products, Quantities = Quantities, Prices = Prices, current_user = current_user, UserID = UserID, CurrentBasket=CurrentBasket)
    else:
        return redirect(url_for('basket', UserID = current_user.getID()))

@app.route('/add/<int:ProductID>', methods=['POST'])
def AddProductToBasket(ProductID):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    #Basket object is deserialized and if the order exists, the quantity is incremented otherwise a new OrderDetail record is added
    CurrentBasket = pickle.loads(session.get('Basket'))
    basketID = CurrentBasket.getBasketID()
    CurrentBasket.setEditDate()
    CurrentBasket.UpdateBasket()
    quantity = int(request.form.get('quantity'))

    ExistingOrder = OrderDetails.SelectOrder(ProductID, basketID)
    if ExistingOrder is not None:
        ExistingOrder.setQuantity(ExistingOrder.getQuantity() + quantity)
        ExistingOrder.UpdateOrder()
    else:
        OrderQuery = OrderDetails(basketID, ProductID, quantity)
        OrderQuery.AddOrder()
    return redirect(url_for('home'))

@app.route('/remove/<int:ProductID>')
def RemoveProductFromBasket(ProductID):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    #Basket object deserialized and the order is removed
    CurrentBasket = pickle.loads(session.get('Basket'))
    BasketID = CurrentBasket.getBasketID()
    CurrentBasket.setEditDate()
    CurrentBasket.UpdateBasket()

    if current_user.getID() == CurrentBasket.getUserID():
        OrderQuery = OrderDetails(BasketID, ProductID, 1)
        OrderQuery.RemoveOrder()
        return redirect(url_for('basket', UserID = current_user.getID()))
    else:
        return redirect(url_for('basket', UserID = current_user.getID()))

#Basket deserialized and the quantity is changed/ Record removed if the quantity is 0
@app.route('/changeQuantity/<int:ProductID>', methods=['POST'])
def ChangeQuantityInBasket(ProductID):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    CurrentBasket = pickle.loads(session.get('Basket'))
    CurrentBasket.setEditDate()
    CurrentBasket.UpdateBasket()

    BasketID = CurrentBasket.getBasketID()
    quantity = int(request.form.get('quantity'))
    ExistingOrder = OrderDetails.SelectOrder(ProductID, BasketID)

    if quantity == 0:
        return redirect(url_for('RemoveProductFromBasket', ProductID = ProductID))
    else:
        ExistingOrder.setQuantity(quantity)
        ExistingOrder.UpdateOrder()
        return redirect(url_for('basket', UserID = current_user.getID()))

#Deactivates current basket, Assigns user a new one and then adds a record to the spending database
@app.route('/checkout')
def CheckOut():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    CurrentBasket = pickle.loads(session.get('Basket'))
    if CurrentBasket.getActive() == True:
        BasketID = CurrentBasket.getBasketID()
        SainsburyTotal = session.get('SainsburyTotal', Decimal(0.00))
        TescoTotal = session.get('TescoTotal', Decimal(0.00))
        if Decimal(SainsburyTotal) + Decimal(TescoTotal) != Decimal(0.00):
            CurrentBasket.CheckOut()
            Spent = Spending("", BasketID, SainsburyTotal, TescoTotal)
            Spent.CreateSpending()
    return redirect(url_for('basket', UserID = current_user.getID()))

#Gets the filter and outputs the relevent graph from data from the basket and spending tables
@app.route('/yourOrders', methods=["POST", "GET"])
def Orders():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    GraphType = "WeeklySplit"
    if request.method == "POST":
        GraphType = request.form.get('GraphType', "WeeklySplit")
    if GraphType == "WeeklySplit":
        GraphHTML, BasketIDs = Spending.WeeklyPlot(current_user.getID())
    elif GraphType == "YearlyTotal":
        GraphHTML, BasketIDs = Spending.MonthlyTotal(current_user.getID()), []
    elif GraphType == "MonthlyPieChart":
        GraphHTML, BasketIDs = Spending.MonthlyPieChart(current_user.getID()), []
    return render_template('orders.html', GraphHTML=GraphHTML, BasketIDs=BasketIDs, GraphType=GraphType)

#Sets the sessionData OldBasketID to a serialised  the old basket object
@app.route('/OldOrder', methods=["POST"])
def OldOrder():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method == "POST":
        BasketID = request.form.get("BasketID")
        Baskets = Basket.getBasketFromBasketID(BasketID)
        session['OldBasketID'] = pickle.dumps(Baskets)
    return redirect(url_for('basket', UserID = current_user.getID()))

#Gets all relevent info for the FriendsList
@app.route('/Friendlist')
def friendlist():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    Friends,FriendRequests, Blocked = [], [], []
    Friends, FriendRequests = current_user.getAllFriends(Friends, FriendRequests)
    Blocked = current_user.getBlocked(Blocked)
    return render_template('friendlist.html', Users=Friends, Requests = FriendRequests, Blocked=Blocked)

#Addition of friend if there is a pending friend request or sends a friend request if the user is not blocked and you aren't trying to add yourself
@app.route('/AddFriend', methods=['POST'])
def addfriend():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    FriendRequests = []
    FriendUsername = request.form.get('FriendUsername')
    Friend = User.getUserFromName(FriendUsername)
    if Friend is not None:
        FriendRequests = current_user.getAllFriendRequests(FriendRequests)
        if (Friend.getID() == FriendReq.getID() for FriendReq in FriendRequests) and len(FriendRequests) > 0:
            current_user.AcceptFriendRequest(Friend.getID())
        elif Friend.CheckFriends(Friend.getID()) == False and Friend.getID() is not current_user.getID():
            if not current_user.isBlocked(Friend.getID()):
                current_user.AddFriend(Friend.getID())
    return redirect(url_for('friendlist'))

@app.route('/AcceptFriendRequest/<string:FriendUsername>', methods=['GET','POST'])
def acceptfriendrequest(FriendUsername):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    Friend = User.getUserFromName(FriendUsername)
    current_user.AcceptFriendRequest(Friend.getID())
    return redirect(url_for('friendlist'))

@app.route('/DenyFriendRequest/<string:FriendUsername>', methods=['GET','POST'])
def denyfriendrequest(FriendUsername):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    DenyOrRemoveFriend(FriendUsername)
    return redirect(url_for('friendlist'))

@app.route('/RemoveFriend/<string:FriendUsername>', methods=['GET','POST'])
def removefriend(FriendUsername):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    DenyOrRemoveFriend(FriendUsername)
    return redirect(url_for('friendlist'))

def DenyOrRemoveFriend(FriendUsername):
    Friend = User.getUserFromName(FriendUsername)
    current_user.RemoveFriend(Friend.getID())

@app.route('/Block/<string:FriendUsername>', methods=['GET','POST'])
def blockfriend(FriendUsername):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    Friend = User.getUserFromName(FriendUsername)
    current_user.BlockFriend(Friend.getID())
    return redirect(url_for('friendlist'))


#Only allows admins to access these pages
@app.route('/Adminpage')
def adminpage():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.getAdmin() == True:
        return render_template("adminpage.html")
    else:
        flash("You are not an Admin!")
        return redirect(url_for("home"))

@app.route('/addAdmin/<int:UserID>')
def addadmin(UserID):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.getAdmin() == True:
        if current_user.getID() != UserID:
            current_user.setAdmin(UserID)
        return redirect(url_for('userlist'))
    else:
        flash("You are not an Admin!")
        return redirect(url_for("home"))

@app.route('/removeAdmin/<int:UserID>')
def removeadmin(UserID):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.getAdmin() == True:
        if current_user.getID() != UserID:
            current_user.removeAdmin(UserID)
        return redirect(url_for('userlist'))
    else:
        flash("You are not an Admin!")
        return redirect(url_for('userlist'))

@app.route('/Userlist')
def userlist():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.getAdmin() == True:
        Users = []
        Users = User.getAllUsers(Users)
        return render_template('userlist.html', Users=Users)
    else:
        flash("You are not an Admin!")
        return redirect(url_for('home'))

#Displays Categories to admins and allows addition of new items or edits to the current item's URL
@app.route('/Categorylist', methods=['GET', 'POST'])
def categorylist():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.getAdmin() == True:
        Catagories = []
        Categories = Category.getCategories(Catagories)
        CategoryName, Supermarket, URL = None, None, None

        #If a POST is sent a new category is added to the Category Table
        if request.method == 'POST':
            CategoryName = request.form.get('CategoryName')
            Supermarket = request.form.get('Supermarket')
            URL = request.form.get('URL')
            CurrentCategory = Category(CategoryName, Supermarket, URL)
            CurrentCategory.CreateCategory()

        #If Get method is sent, The table is updated without the page reloading with the updated values when save is pressed
        if request.method == 'GET':
            index = request.args.get('index')
            Supermarket = request.args.get('column0')
            URL = request.args.get('column1')
            try:
                CurrentCategory = Categories[int(index)-1]
                CurrentCategory.setSupermarket(Supermarket)
                CurrentCategory.setURL(URL)
                CurrentCategory.UpdateCategory()
            except Exception as e:
                print(e)
        return render_template('categorylist.html', user=current_user, categories=Categories)
    else:
        flash("You are not an Admin!")
        return redirect(url_for('home'))

#Scrapes the categories if the user is an admin ore the scheduler is running
@app.route('/ScrapeCategories')
def scrape():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    with app.app_context():
        try:
            if current_user.getAdmin() == True:
                CategoryList = Category.getCategories([])
                for category in CategoryList:
                    if category.getSupermarket() == "Tesco":
                        category.ScrapeTesco()
                    elif category.getSupermarket() == "Sainsbury":
                        category.ScrapeSainsbury()
                Product.DeleteOldProducts()
                return redirect(url_for('adminpage'))
            else:
                flash("You are not an Admin!")
                return redirect(url_for("home"))
        except:
            if scheduler.running == True:
                CategoryList = Category.getCategories([])
                for category in CategoryList:
                    if category.getSupermarket() == "Tesco":
                        category.ScrapeTesco()
                    elif category.getSupermarket() == "Sainsbury":
                        category.ScrapeSainsbury()
                Product.DeleteOldProducts()
                return redirect(url_for('adminpage'))

# scheduler.add_job(scrape, 'cron', hour=00, minute=59)
@app.route('/ping')
def ping():
    return 'pong'

if __name__ == '__main__':
    scheduler.start()
    app.jinja_env.cache = {}
    app.run(debug=True)
