
"""
cc4889
test
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import traceback
from flask import Flask, redirect, url_for
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



DATABASE_USERNAME = "cc4889"
DATABASE_PASSWRD = "1888"
DATABASE_HOST = "34.28.53.86" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"



# This line creates a database engine that knows how to connect to the URI above.
engine = create_engine(DATABASEURI,future=True)


# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
# with engine.connect() as conn:
# 	create_table_command = """
# 	CREATE TABLE IF NOT EXISTS test (
# 		id serial,
# 		name text
# 	)
# 	"""
# 	res = conn.execute(text(create_table_command))
# 	insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
# 	res = conn.execute(text(insert_table_command))
# 	# you need to commit for create, insert, update queries to reflect
# 	conn.commit()


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data

		#
	# Flask uses Jinja templates, which is an extension to HTML where you can
	# pass data to a template and dynamically generate HTML based on the data
	# (you can think of it as simple PHP)
	# documentation: https://realpython.com/primer-on-jinja-templating/
	#
	# You can see an example template in templates/index.html
	#
	# context are the variables that are passed to the template.
	# for example, "data" key in the context variable defined below will be 
	# accessible as a variable in index.html:
	#
	#     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
	#     <div>{{data}}</div>
	#     
	#     # creates a <div> tag for each element in data
	#     # will print: 
	#     #
	#     #   <div>grace hopper</div>
	#     #   <div>alan turing</div>
	#     #   <div>ada lovelace</div>
	#     #
	#     {% for n in data %}
	#     <div>{{n}}</div>
	#     {% endfor %}
	#
	"""

@app.route('/')
def index():
	# DEBUG: this is debugging code to see what request looks like
	# print(request.args)

	# select_query1 = "SELECT item_name, price from item where "
	# cursor = g.conn.execute(text(select_query1))
	# names = []
	# for result in cursor:
	# 	names.append(result[0])
	# cursor.close()
	# context = dict(data = names)

	#
	# render_template looks in the templates/ folder for files.
	# for example, the below file reads template/index.html
	#
	return render_template("index.html")

@app.route('/staff_list')
def staff_list():
	if len(request.args) == 0:
		# staff_query1 = "SELECT staff_name, salary from staff"
		# cursor = g.conn.execute(text(staff_query1))
		# names = [c for c in cursor]
		# cursor.close()
		context = dict()
	else:
		selected_date = request.args.get('selected_date','2022-01-01')
		staff_query2 = '''SELECT staff_name, count(*) from staff, orders, is_fulfilled 
						where staff.id = is_fulfilled.id and orders.order_id = is_fulfilled.order_id
						and TO_CHAR(orders.order_time, 'YYYY-MM-DD') = \'{}\'
						group by staff.id
						order by 2
						desc
						'''.format(selected_date)
		cursor = g.conn.execute(text(staff_query2))
		names = [c for c in cursor]
		cursor.close()
		context = dict(data = names, selected_date = selected_date)
	return render_template("staff_list.html",**context)
#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

'''
QUERY 1: food search
'''
@app.route('/discover_food')
def discover_food():
	price_low = request.args.get('price_low', '0')
	price_high = request.args.get('price_high', '100000')
	cuisine = request.args.get('cuisine', 'Authentic')
	select_query1 = "SELECT item_name, price from item where price>={} and price<= {} and cuisine = \'{}\'".format(price_low, price_high, cuisine)
	cursor = g.conn.execute(text(select_query1))
	names = [c for c in cursor]
	cursor.close()
	context = dict(data = names)


	return render_template("discover_food.html",**context)

'''
QUERY 2: add order
'''
@app.route('/order_management')
def order_management():
	item_query = 'select item_id from item'
	order_query = 'select order_id from orders'
	cursor = g.conn.execute(text(item_query))
	items = [c[0] for c in cursor]
	cursor = g.conn.execute(text(order_query))
	orders = [c[0] for c in cursor]
	if len(request.args) > 0:
		order_id = request.args.get('order_id', '0')
		query2 = "select item.item_id, item.item_name, item.desci from is_ordered left join item on is_ordered.item_id = item.item_id where is_ordered.order_id = \'{}\'".format(order_id)
		cursor = g.conn.execute(text(query2))
		names = [c for c in cursor]
		context = dict(data = names, order_id = order_id, orders = orders, items = items)

	else:
		#initial 
		query2 = "select item_id, item_name, desci from item where inventory > 0"
		cursor = g.conn.execute(text(query2))
		names = [c for c in cursor]
		context = dict(data = names,orders = orders, items = items, order_id = 'NOT SELECTED')

	return render_template("food_management.html",**context)


# Example of adding new data to the database
@app.route('/add_food', methods=['POST'])
def add():
	# accessing form inputs from user
	order_id = request.form['order_id']
	item_id = request.form['item_id']
	# passing params in for each variable into query
	g.conn.execute(text('INSERT INTO is_ordered VALUES (\'{}\',\'{}\')'.format(order_id, item_id)))
	g.conn.commit()
	return redirect(url_for('order_management', order_id = order_id))

# Example of adding new data to the database
@app.route('/find_top_waiter', methods=['POST'])
def find_top_waiter():
	# accessing form inputs from user
	selected_date = request.form['selected_date']
	# passing params in for each variable into query
	return redirect(url_for('staff_list', selected_date = selected_date))

# Example of adding new data to the database
@app.route('/search_item', methods=['POST'])
def search_item():
	# accessing form inputs from user
	price_low = request.form['price_low']
	price_high = request.form['price_high']
	cuisine = request.form['cuisine']
	# passing params in for each variable into query
	params = {}
	print(price_low)
	if price_low=='':
		price_low = 0

	if price_high == '':
		price_low = 100000

	params["cuisine"] = cuisine
	# cursor = g.conn.execute(text('select item_name, price, cuisine from item where cuisine = :cuisine and price>= :price_low and price<=:price_high'), params)
	# g.conn.commit()
	# names = []
	# for result in cursor:
	# 	names.append(result[0])
	# cursor.close()
	return redirect(url_for('discover_food', price_high = price_high, price_low = price_low, cuisine = cuisine))

# @app.route('/login')
# def login():
# 	abort(401)
# 	this_is_never_executed()


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help
		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
