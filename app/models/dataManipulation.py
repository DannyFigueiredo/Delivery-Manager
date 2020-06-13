################################
# C - Create
# R - Read
# U - Update
# D - Delete
################################
from datetime import *
import sqlite3


################################
# Table: Users
################################
def insertUser(username, password, user_name='', user_phone='', level='deliveryman'):
	sql = """
	INSERT INTO users(username, password, user_name, user_phone, level, available)
	VALUES ('{}', '{}', '{}', '{}', '{}', 1)
	"""
	sql = sql.format(username, password, user_name, user_phone, level)

	return str(sql)

def updateUser(user_id, username, password, user_name, user_phone, level):
	sql = """
	UPDATE users
	SET username = '{}', password = '{}', user_name = '{}', user_phone = '{}', level = '{}'
	WHERE user_id = '{}'
	"""
	sql = sql.format(username, password, user_name, user_phone, level, user_id)

	return str(sql)

def deleteUser(user_id):
	sql = """
	DELETE FROM users
	WHERE user_id = '{}'
	"""
	sql = sql.format(user_id)

	return str(sql)

def selectUsers(field, value):
	sql = """
	SELECT user_id, username, password, user_name, user_phone, level, available
	FROM users
	WHERE available = 1 AND {} = '{}'
	"""
	sql = sql.format(field, value)

	return str(sql)


################################
# Table : Clients
################################
def insertClient(client_phone):
	sql = """
	INSERT INTO clients(client_phone)
	VALUES ('{}')
	"""
	sql = sql.format(client_phone)

	return str(sql)

def updateClient(client_id, client_name, adress, neighborhood, landmark):
	sql = """
	UPDATE clients
	SET client_name = '{}', adress = '{}', neighborhood = '{}', landmark = '{}'
	WHERE client_id = '{}'
	"""
	sql = sql.format(client_name, adress, neighborhood, landmark, client_id)

	return str(sql)

def deleteClient(client_id):
	sql = """
	DELETE FROM clients
	WHERE client_id = '{}'
	"""
	sql = sql.format(client_id)

	return str(sql)

def selectClients(field, value):
	sql = """
	SELECT client_id, client_phone, client_name, adress, neighborhood, landmark
	FROM clients
	WHERE {} = '{}'
	"""
	sql = sql.format(field, value)

	return str(sql)

def findClient(client_phone):
	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()

		sql = """
		SELECT case
			when client_phone = '{}' then 'Cliente cadastrado'
			else 'Cliente não cadastrado'
		end status
		FROM (SELECT '{}' phone) t1 LEFT JOIN clients t2
		ON t1.phone = t2.client_phone
		"""
		sql = sql.format(client_phone, client_phone)

		cur.execute(sql)
		status = cur.fetchone()[0]
	db.close()

	return status

################################
# Table: Products
################################
def insertProdut(image, product_name, category, description, unit_price, available, create_by):
	now = datetime.now().strftime('%d/%m/%Y')

	sql = """
	INSERT INTO products(image, product_name, category, description, unit_price, available, create_by, created_at)
	VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
	"""
	sql = sql.format(image, product_name, category, description, unit_price, available, create_by, now)
	
	return str(sql)

def updateProduct(product_id, description, unit_price, available):
	now = datetime.now().strftime('%d/%m/%Y')

	sql = """
	UPDATE products
	SET description = '{}', unit_price = '{}', available = '{}', modified_by = '{}', modified_at = '{}'
	WHERE product_id = '{}'
	"""
	sql = sql.format(description, unit_price, available, 1, now, product_id)
	print(sql)
	return str(sql)


def deleteProduct(product_id):
	sql = """
	DELETE FROM products
	WHERE product_id = '{}'
	"""
	sql = sql.format(product_id)

	return str(sql)

def selectCategories():
	sql = """
	SELECT category
	FROM products
	GROUP BY category
	"""
	return str(sql)

def selectProducts(field=None, value=None, unavailable=False):
	if (unavailable == True):
		sql = """
		SELECT product_id, image, product_name, category, description, unit_price, available
		FROM products
		WHERE {} = '{}'
		ORDER BY description
		"""
		sql = sql.format(field, value)

	elif (field == None and value == None):
		sql = """
		SELECT product_id, image, product_name, category, description, unit_price
		FROM products
		WHERE available = 1
		ORDER BY description
		"""

	else:		
		sql = """
		SELECT product_id, image, product_name, category, description, unit_price
		FROM products
		WHERE available = 1 AND {} = '{}'
		ORDER BY description
		"""
		sql = sql.format(field, value)

	return """{}""".format(sql)


################################
# Table: Orders
################################
def insertOrder(client_id, deliveryman_id = 1):
	sql = """
	INSERT INTO orders(client_id, deliveryman_id)
	VALUES ('{}', {})
	"""
	sql = sql.format(client_id, deliveryman_id)
	
	return str(sql)

def updateOrder(order_id, paymant_method, notes, change=0):
	now = datetime.now()
	now_str = now.strftime('%d/%m/%Y %H:%M')

	# Regra de delivery:
	# Pedidos feitos após às 18h devem ser entregues no dia seguinte
	if (now.hour >= 18):
		delivery_date = date(now.year, now.month, now.day + 1).strftime('%d/%m/%Y')
	else:
		delivery_date = now_str

	sql = """
	UPDATE orders
	SET order_date = '{}', paymant_method = '{}', change = '{}', notes = '{}', delivery_date = '{}'
	WHERE order_id = '{}'
	"""
	sql = sql.format(now_str, paymant_method, change, notes, delivery_date, order_id)

	''' Quando apagar a tabela da proxima vez
	sql = """
	UPDATE orders
	SET order_date = '{}', paymant_method = '{}', change = '{}', notes = '{}', delivery_date = '{}', finished = '{}'
	WHERE order_id = '{}'
	"""
	sql = sql.format(now_str, paymant_method, change, notes, delivery_date, 1, order_id)

	'''
	return sql

def deleteOrder(order_id):
	sql = """
	DELETE FROM orders
	WHERE order_id = '{}'
	"""
	sql = sql.format(order_id)

	return str(sql)

def selectOrders(field, value):
	sql = """
	SELECT order_id, client_id, deliveryman_id, order_date, paymant_method, change, notes, delivery_date
	FROM orders
	WHERE {} = '{}'
	"""
	sql = sql.format(field, value)

	return str(sql)

def maxOrder(client_id):
	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()

		sql = """
		SELECT max(order_id) order_id
		FROM orders 
		WHERE client_id = '{}'
		"""
		sql = sql.format(client_id)

		cur.execute(sql)
		lastOrder = cur.fetchone()[0]
	db.close()

	return lastOrder


################################
# Table: Orders
################################
def subtotal(amount, product_id):
	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()

		sql = """
		SELECT ({} * unit_price) subtotal
		FROM products 
		WHERE product_id = '{}'
		"""
		sql = sql.format(amount, product_id)

		cur.execute(sql)
		subtotal = cur.fetchone()
		subtotal = subtotal[0]
	db.close()

	return subtotal


def insertOrderProducts(order_id, product_id, amount):
	sub = subtotal(amount, product_id)

	sql = """
	INSERT INTO order_products(order_id, product_id, amount, subtotal)
	VALUES ('{}', '{}', '{}', '{}')

	"""
	sql = sql.format(order_id, product_id, amount, sub)

	return sql


def updateOrderProducts(order_id, product_id, amount):
	subtotal = subtotal(amount, product_id)

	sql = """
	UPDATE order_products
	SET amount = '{}', subtotal = '{}'
	WHERE order_id = '{}' AND product_id = '{}'
	"""
	sql = sql.format(amount, subtotal, order_id, product_id)

	return str(sql)

def deleteOrderProducts(order_id, product_id):
	sql = """
	DELETE FROM order_products
	WHERE order_id = '{}' and product_id = '{}'
	"""
	sql = sql.format(order_id, product_id)

	return str(sql)


def selectExistsProduct(order_id, product_id):
	sql = """
	SELECT case
		when t2.order_id is null then 'N'
		else 'Y'
	end exist_product
	FROM (SELECT '{}' order_id, '{}' product_id) t1 LEFT JOIN order_products t2
	ON t1.order_id = t2.order_id and t1.product_id = t2.product_id
	"""
	sql = sql.format(order_id, product_id)

	return sql

def selectShoppingCart(order_id):
	sql = """
	SELECT t1.amount, t2.description, t1.subtotal, t1.product_id
	FROM order_products as t1 left join products as t2
	ON t1.product_id = t2.product_id
	WHERE t1.order_id = '{}'
	"""
	sql = sql.format(order_id)

	return sql

def countProductsOnCart(client_id):
	lastOrder = maxOrder(client_id)

	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()

		sql = """
		SELECT count(1)
		FROM order_products
		WHERE order_id = '{}'
		"""
		sql = sql.format(lastOrder)

		cur.execute(sql)
		numProducts = cur.fetchone()
	db.close()

	return numProducts

def totalOrder(order_id):
	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()

		sql = """
		SELECT sum(t1.subtotal) total
		FROM order_products as t1 left join products as t2
		ON t1.product_id = t2.product_id
		WHERE t1.order_id = '{}'
		"""
		sql = sql.format(order_id)

		cur.execute(sql)
		total = cur.fetchone()
	db.close()

	return total



# Funções Administrador
##############################
def ordersForToday(today):
	sql = """
	SELECT t2.order_id, substr(t2.order_date, 12), sum(t1.subtotal) TOTAL
	FROM order_products t1 left join orders t2
	ON t1.order_id = t2.order_id
	WHERE substr(t2.delivery_date, 0, 11) = '{}'
	GROUP BY t2.order_id, substr(t2.order_date, 12)
    ORDER BY t2.order_date
    """.format(today)

	return sql


def productsToBuy(today):
	sql = """
	SELECT t3.description ---t2.order_id, substr(t2.order_date, 12 ), sum(t1.subtotal) TOTAL
	FROM order_products t1 left join orders t2
	ON t1.order_id = t2.order_id
	LEFT JOIN products t3
	ON t1.product_id = t3.product_id
	WHERE substr(t2.delivery_date, 0, 11) = '{}'
	GROUP BY t3.description
	""".format(today)

	return sql


def orderDetails(order_id):
	sql = """
	SELECT t1.order_date, t2.client_name, t2.client_phone, t2.adress, t2.neighborhood, t2.landmark, t1.paymant_method, t1.change, t1.notes
	FROM orders t1 LEFT JOIN clients t2
	ON t1.client_id = t2.client_id
	WHERE t1.order_id = '{}'
	""".format(order_id)

	return sql


def getProducts():
	sql = """
	SELECT product_id, description, unit_price, available
	FROM products
	ORDER BY description
	"""

	return sql


def history():
	sql = """
	SELECT substr(t2.delivery_date, 0, 11), sum(t1.subtotal)
	FROM order_products t1 LEFT JOIN orders t2
	ON t1.order_id = t2.order_id
	GROUP BY substr(t2.delivery_date, 0, 11)
	"""
	return sql