#Imports the plotly library in order to plot the relevent data in a Graphical
from Product import Connect_db
import plotly.graph_objects as plot


class Spending():
    def __init__(self, SpendingID, BasketID, SainsburyTotal, TescoTotal):
        self.SpendingID = SpendingID
        self.BasketID = BasketID
        self.SainsburyTotal = SainsburyTotal
        self.TescoTotal = TescoTotal
    
    #Uses the object data to insert a record into the Spending table
    def CreateSpending(self):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "INSERT INTO Spending(SpendingID, BasketID, SainsburyTotal, TescoTotal) VALUES(%s,%s,%s,%s)"
        values = (self.SpendingID, self.BasketID, self.SainsburyTotal, self.TescoTotal)
        connection.execute(Query,values)
        db.commit()
        connection.close()
    
    #Uses Crosstable SQL to grab the Start of the week from the EditDate attribute in the Basket table, BasketIDs and the Total spending from Tesco and Sainsbury of baskets "checked out" in the last month
    @staticmethod
    def getWeeklySpendingData(UserID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT DATE_FORMAT(DATE_SUB(Basket.EditDate, INTERVAL WEEKDAY(Basket.EditDate) DAY), '%d-%m-%Y') AS StartOfWeek, Spending.BasketID, SUM(Spending.SainsburyTotal), SUM(Spending.TescoTotal) FROM Spending, Basket WHERE Basket.IsActive = False AND Basket.UserID = %s AND Basket.BasketID = Spending.BasketID GROUP BY StartOfWeek, Spending.BasketID ORDER BY MIN(Basket.EditDate) ASC"
        values = (UserID,)
        connection.execute(Query,values)
        SpendingData = connection.fetchall()
        connection.close()
        return SpendingData
    
    #Grabs Total from each of the month and the Editdate by month and year, ordered by the Date gotten
    @staticmethod
    def getSpendingTotal(UserID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT DATE_FORMAT(Basket.EditDate, '%M %Y') AS MonthName, SUM(Spending.SainsburyTotal + Spending.TescoTotal) FROM Spending, Basket WHERE Basket.IsActive = False AND Basket.BasketID = Spending.BasketID AND Basket.UserID = %s GROUP BY MonthName ORDER BY MonthName DESC"
        values = (UserID,)
        connection.execute(Query,values)
        SpendingData = connection.fetchall()
        connection.close()
        return SpendingData
    
    #Grabs the quantity of items brought from Tesco and the quantity of items brought from Sainsbury as well as the basket EditDate where the basket is owned by a user ordered by the Month
    @staticmethod
    def getPieChartQuantityData(UserID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT DATE_FORMAT(Basket.EditDate, '%M %Y') AS MonthName, SUM(CASE WHEN Product.SuperMarket = 'Tesco' THEN OrderDetails.Quantity ELSE 0 END) AS TescoQuantity, SUM(CASE WHEN Product.SuperMarket = 'Sainsbury' THEN OrderDetails.Quantity ELSE 0 END) AS SainsburyQuantity FROM Basket, OrderDetails, Product, Spending WHERE Basket.BasketID = OrderDetails.BasketID AND Product.ProductID = OrderDetails.ProductID AND Basket.BasketID = Spending.BasketID AND Basket.UserID = %s GROUP BY MonthName ORDER BY MonthName DESC"
        values = (UserID,)
        connection.execute(Query,values)
        SpendingData = connection.fetchall()
        connection.close()
        return SpendingData

    #Grabs the quantatity spent in each supermarket for the month using inactive baskets owned by the user
    @staticmethod   
    def getPieChartSpendingData(UserID):
        db = Connect_db()
        connection = db.cursor(buffered=True)
        Query = "SELECT DATE_FORMAT(Basket.EditDate, '%M %Y') AS MonthName, SUM(Spending.SainsburyTotal), SUM(Spending.TescoTotal) FROM Spending, Basket WHERE Basket.IsActive = False AND Basket.BasketID = Spending.BasketID AND Basket.UserID = %s GROUP BY MonthName ORDER BY MonthName DESC"
        values = (UserID,)
        connection.execute(Query,values)
        SpendingData = connection.fetchall()
        connection.close()
        return SpendingData

    #Uses plotly to graph a barchart with the getWeeklySpendingData method to grab the spending each week. Fraphs each individual basket as a bar seperating by supermarket
    @staticmethod
    def WeeklyPlot(UserID):
        WeeklySpending = Spending.getWeeklySpendingData(UserID)
        Weeks = [row[0] for row in WeeklySpending]
        BasketIDs = [row[1] for row in WeeklySpending]
        SainsBasketTotal = [row[2] for row in WeeklySpending]
        TescoBasketTotal = [row[3] for row in WeeklySpending]
        WeeklySpendingGraph = plot.Figure()
        WeeklySpendingGraph.add_trace(plot.Bar(x=Weeks, y=SainsBasketTotal, name='Sainsbury', text=["Basket: " + str(BasketID) for BasketID in BasketIDs]))
        WeeklySpendingGraph.add_trace(plot.Bar(x=Weeks, y=TescoBasketTotal, name='Tesco', text=["Basket: " + str(BasketID) for BasketID in BasketIDs]))
        WeeklySpendingGraph.update_layout(title='Weekly Spending', xaxis_title='Week', yaxis_title='Total Spending', uniformtext_minsize=10000, uniformtext_mode='hide')
        WeeklySpendingGraph.update_yaxes(tickprefix='£', tickformat='.2f')
        WeeklySpendingGraph.update_xaxes(type='category')
        WeeklySpendingGraph.update_traces(hoverinfo="y+text", textposition='inside') 
        GraphHTML = [WeeklySpendingGraph.to_html(full_html=False)]
        return GraphHTML, BasketIDs

    #Graphs the spending throughout the year as a line graph seperating it by months
    @staticmethod    
    def MonthlyTotal(UserID):
        WeeklySpending = Spending.getSpendingTotal(UserID)
        Months = [row[0] for row in WeeklySpending]
        Total = [row[1] for row in WeeklySpending]
        MonthlyTotalGraph = plot.Figure()
        MonthlyTotalGraph.add_trace(plot.Line(x=Months, y=Total))
        MonthlyTotalGraph.update_layout(title='Yearly Spending', xaxis_title='Week', yaxis_title='Total Spending')
        MonthlyTotalGraph.update_yaxes(tickprefix='£', tickformat='.2f')
        MonthlyTotalGraph.update_xaxes(type='category')
        MonthlyTotalGraph.update_traces(hoverinfo="y")
        GraphHTML = [MonthlyTotalGraph.to_html(full_html=False)]
        return GraphHTML

    #Displays the quantity of items brought and total spent at each supermarket for each month in pie chart form for comparison
    @staticmethod
    def MonthlyPieChart(UserID):
        WeeklyQuantity = Spending.getPieChartQuantityData(UserID)
        Months = [row[0] for row in WeeklyQuantity]
        SainsQuantity = [row[1] for row in WeeklyQuantity]
        TescoQuantity = [row[2] for row in WeeklyQuantity]
        GraphList = []
        WeeklySpending = Spending.getPieChartSpendingData(UserID)
        SainsTotal = [row[1] for row in WeeklySpending]
        TescoTotal = [row[2] for row in WeeklySpending]
        for month, sains_quantity, tesco_quantity, sains_total, tesco_total in zip(Months, SainsQuantity, TescoQuantity, SainsTotal, TescoTotal):
            PieChartQuantity = plot.Figure()
            PieChartQuantity.add_trace(plot.Pie(labels=["Tesco", "Sainsbury"], values=[tesco_quantity, sains_quantity], name=str(month), marker=dict(colors=('rgb(0, 83, 159)', 'rgb(237, 139, 1)'))))
            PieChartQuantity.update_layout(title=f'Monthly Quantity Comparison - {month}')
            PieChartQuantity.update_traces(textposition='inside', textinfo='percent+label', hovertemplate = "Shop:%{label} <br>Quantity: %{value}")
            GraphHTML = PieChartQuantity.to_html(full_html=False)
            GraphList.append(GraphHTML)

            PieChartSpending = plot.Figure()
            PieChartSpending.add_trace(plot.Pie(labels=["Tesco", "Sainsbury"], values=[tesco_total, sains_total], name=str(month), marker=dict(colors=('rgb(0, 83, 159)', 'rgb(237, 139, 1)'))))
            PieChartSpending.update_layout(title=f'Monthly Spending Comparison - {month}', yaxis=dict(tickprefix="£"))
            PieChartSpending.update_traces(textposition='inside', textinfo='percent+label', hovertemplate = "Shop:%{label} <br>Spending: £%{value}")
            GraphHTML = PieChartSpending.to_html(full_html=False)
            GraphList.append(GraphHTML)            
        return GraphList