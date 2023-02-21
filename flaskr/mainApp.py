import os
import re
from flask import Flask, render_template, redirect, request
from flaskr.init_db import DBManager


def create_app():
    """Creates and configures the flask app."""
    app = Flask(__name__, instance_relative_config=True, template_folder="..\\flaskr\\templates")
    app.config.from_mapping(
        # This is used by Flask and extensions to keep data safe.
        # Should be overridden with a random value when deploying
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        EXPLAIN_TEMPLATE_LOADING=True
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app


app = create_app()


@app.route('/')
def index():
    """Navigate to the home page."""
    return redirect('/home')


@app.route('/home')
def home():
    """Render the home page."""
    return render_template("home.html")

@app.route('/call', methods=['GET', 'POST'])
def call():
    if request.method == 'GET':
        db_manager = DBManager(app)
        sql_connection = db_manager.get_connection()

        sql_connection.execute("INSERT INTO users (userID, first_name , last_name, password_hash , role)"
                               + " VALUES (69, 'Mahid', 'Gondal', '###', 1)")

        sql_connection.execute("INSERT INTO users (userID, first_name , last_name, password_hash , role)"
                               + " VALUES (96, 'Jhon', 'Snow', '##1', 1)")

        sql_connection.execute("SELECT first_name, last_name FROM users"
                               + " WHERE  role = 1"
                               + " ORDER BY RANDOM()"
                               + "  LIMIT 1;")
        rows = sql_connection.fetchall()

        db_manager.close()

        return render_template('calling.html', rows=rows)


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    """Render the menu page. Get menu items from the database."""
    db_manager = DBManager(app)
    sql_connection = db_manager.get_connection()

    # Gets all the rows from menu or apply the filter if made.
    if not request.form:
        sql_connection.execute("SELECT * FROM menu;")
        rows = sql_connection.fetchall()
    else:
        if request.method == 'GET':
            return render_template('menu.html')
        elif request.method == 'POST':
            rows = filter_menu()

    db_manager.close()

    # Passes the rows of the table to the pages .html file.
    return render_template('menu.html', rows=rows)


@app.route('/addMenuItem', methods=['GET', 'POST'])
def add_menu_item():
    if request.method == 'GET':
        return render_template('addMenuItem.html')
    elif request.method == 'POST':
        # Render the page to add a menu item. Adds an item to menu based on items from an HTML form.
        db_manager = DBManager(app)
        sql_connection = db_manager.get_connection()

        # Stores the items from the form in addMenuItem.html.
        name = request.form['name']
        if not name:
            error = "Name cannot be left blank."
            return render_template('addMenuItem.html', error=error)

        price = request.form['price']
        if not price:
            error = "Price cannot be left blank."
            return render_template('addMenuItem.html', error=error)
        elif not bool(re.match(r'^\d+(\.\d{0,2})?$', price)):
            error = "Price must be a valid decimal number eg. 12.34"
            return render_template('addMenuItem.html', error=error)

        calories = request.form['calories']
        if not calories:
            error = "Calories cannot be left blank."
            return render_template('addMenuItem.html', error=error)
        elif not calories.isdigit():
            error = "Calories must be a valid whole number."
            return render_template('addMenuItem.html', error=error)

        # Changes the list of allergens to a string.
        allergensList = request.form.getlist('options')
        allergens = ', '.join(allergensList)

        # Add an item to the menu table.
        sql_connection.execute("INSERT INTO menu (name, price, calories, allergens)"
                               " VALUES (?, ?, ?, ?)", (name, price, calories, allergens))

        db_manager.get_db().commit()
        db_manager.close()

        return redirect('/menu')


@app.route('/editMenuItem', methods=['GET', 'POST'])
def edit_menu_item():
    if request.method == 'GET':
        # Render the page to edit the menu.
        db_manager = DBManager(app)
        sql_connection = db_manager.get_connection()

        # Gets all the rows in menu.
        sql_connection.execute("SELECT * FROM menu;")
        rows = sql_connection.fetchall()

        db_manager.close()

        # Passes the rows of the table to editMenuItem.html.
        return render_template('/editMenuItem.html', rows=rows)

    elif request.method == 'POST':
        # Renders the page to remove an item from the menu.
        db_manager = DBManager(app)
        sql_connection = db_manager.get_connection()

        # Iterate over data from the form in editMenuItem.html.
        for key, value in request.form.items():

            # Is the checkbox checked.
            if value == 'on':
                # Delete selected rows.
                sql_connection.execute("DELETE FROM menu WHERE itemID = ?", key)
                db_manager.get_db().commit()

        db_manager.close()

        return redirect('/menu')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Renders the page to login."""
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        return redirect('/home')


@app.route('/createLogin', methods=['GET', 'POST'])
def create_login():
    if request.method == 'GET':
        return render_template('createLogin.html')
    elif request.method == 'POST':
        return redirect('/home')


def filter_menu():
    db_manager = DBManager(app)
    sql_connection = db_manager.get_connection()
    # Initial SQL command Built up over filtering
    command = "SELECT * FROM menu "

    # Sort by ranges (both price and calorie)
    pri_min = str(request.form['Price_Min'])
    pri_max = str(request.form['Price_Max'])
    cal_min = str(request.form['Calories_Min'])
    cal_max = str(request.form['Calories_Max'])
    if pri_max or pri_min or cal_max or cal_min:
        command += "WHERE price >= 0 "
        if pri_max:
            command += "AND price <= " + pri_max + " "
        if pri_min:
            command += "AND price >= " + pri_min + " "
        if cal_max:
            command += "AND price <= " + cal_max + " "
        if cal_min:
            command += "AND price >= " + cal_min + " "

    # Sort By Dropdown menu
    sort = request.form['Sort']
    if sort == 'HPrice':
        command += "ORDER BY price DESC"
    elif sort == 'LPrice':
        command += "ORDER BY price"
    elif sort == 'HCalorie':
        command += "ORDER BY calories DESC"
    elif sort == 'LCalorie':
        command += "ORDER BY calories"
    command += ';'
    sql_connection.execute(command)
    rows = sql_connection.fetchall()

    # Allergens removed from menu
    allergies = request.form.getlist('options')
    if not allergies:
        filtered_rows = []
        for row in rows:
            found = False
            allergens = row[4].split(", ")
            for i in range(len(allergens)):
                for j in range(len(allergies)):
                    if allergens[i] == allergies[j]:
                        found = True
            if not found:
                filtered_rows.append(row)
        return filtered_rows
    else:
        return rows
