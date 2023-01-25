import psycopg2
from flask import Flask, render_template, redirect, request


# Method for connecting to the database.
def databaseConnection():

    # !!! - DATABASE NAME, USER AND PASSWORD WILL NEED TO BE CHANGED TO YOUR LOCAL DB AND DETAILS.
    connection = psycopg2.connect(database="rms",
                                  host="localhost",
                                  user="oliver",
                                  password="test",
                                  port="5432")
    return connection


app = Flask(__name__)


# Route for /.
@app.route('/')
def index():
    return redirect('/home')


# Route for the /home page.
@app.route('/home')
def home():
    return render_template('home.html')


# Route for the /menu page.
@app.route('/menu')
def menu():

    # Creates a connection to the database and cursor.
    connection = databaseConnection()
    cursor = connection.cursor()

    # Cursor executes a statement returning all of the rows in menu and stores results in a list.
    cursor.execute("SELECT * FROM menu;")
    rows = cursor.fetchall()

    # Close the connection and the cursor.
    cursor.close()
    connection.close()

    # Passes the rows of the table to the pages .html file.
    return render_template('menu.html', rows=rows)


# Route for /addMenuItem page.
@app.route('/addMenuItem')
def addMenuItem():
    return render_template('addMenuItem.html')


# Route when submitting a new menu item.
@app.route('/addToMenu', methods=['POST'])
def addToMenu():

    # Creates a connection to the database and cursor.
    connection = databaseConnection()
    cursor = connection.cursor()

    # Stores the items from the form in addMenuItem.html.
    name = request.form['name']
    price = int(request.form['price'])
    calories = int(request.form['calories'])
    allergens = request.form['allergens']

    # Executes a SQL statement adding a row to the menu table.
    cursor.execute("INSERT INTO menu (name, price, calories, allergens)"
                   " VALUES (%s, %s, %s, %s)", (name, price, calories, allergens))

    # Commit the changes to the databases.
    connection.commit()

    # Close the connection and the cursor.
    cursor.close()
    connection.close()

    # Return to the /menu page.
    return redirect('/menu')


# Route for the /editMenuItem page.
@app.route('/editMenuItem')
def editMenuItem():

    # Creates a connection to the database and cursor.
    connection = databaseConnection()
    cursor = connection.cursor()

    # Cursor executes a statement returning all the rows in menu and stores results in a list.
    cursor.execute("SELECT * FROM menu;")
    rows = cursor.fetchall()

    # Close the connection and the cursor.
    cursor.close()
    connection.close()

    # Passes the rows of the table to the pages .html file.
    return render_template('editMenuItem.html', rows=rows)


# Route when removing a menu item.
@app.route('/removeMenuItem', methods=['POST'])
def removeMenuItem():

    # Creates a connection to the database and cursor.
    connection = databaseConnection()
    cursor = connection.cursor()

    # Iterate over the form data provided in editMenuItem.html.
    for key, value in request.form.items():

        # Check if the checkbox was checked.
        if value == 'on':

            # Executes a SQL statement deleting rows in menu that have been selected.
            cursor.execute("DELETE FROM menu WHERE itemID = %s", key)
            connection.commit()

    # Close the connection and the cursor.
    cursor.close()
    connection.close()

    # Returns to the /menu page.
    return redirect('/menu')

