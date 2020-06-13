import sqlite3

db = sqlite3.connect('storage.db')

db.execute(
	'''
	CREATE table users (
	  user_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
	  username VARCHAR(50) NOT NULL UNIQUE,
	  password varchar(50) NOT NULL,
	  user_name VARCHAR(200),
	  user_phone VARCHAR(11),
	  level varchar(20),
	  available boolean
	)
	'''
	)
print('Tabela users criada com sucesso.')


db.execute(
	'''
	CREATE TABLE clients (
	  client_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
	  client_phone varchar(11) NOT NULL UNIQUE,
	  client_name varchar(200),
	  adress varchar(400),
	  neighborhood varchar(50),
	  landmark varchar(500)
	)
	'''
	)
print('Tabela clients criada com sucesso.')


db.execute(
	'''
	CREATE TABLE products (
	  product_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
	  image TEXT NOT NULL,
	  product_name varchar(50) NOT NULL,
	  category varchar(50) NOT NULL,
	  description varchar(200) NOT NULL,
	  unit_price DOUBLE(10,2) NOT NULL,
	  available boolean NOT NULL,
	  create_by integer NOT NULL,
	  created_at date NOT NULL,
	  modified_by integer,
	  modified_at date,
	  FOREIGN KEY(create_by) REFERENCES user(user_id),
	  FOREIGN KEY(modified_by) REFERENCES user(user_id)
	)
	'''
	)
print('Tabela products criada com sucesso.')


db.execute(
	'''
	CREATE TABLE orders (
	  order_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
	  client_id INTEGER NOT NULL,
	  deliveryman_id integer NOT NULL,
	  order_date datetime,
	  paymant_method varchar(30),
	  change double(10,2),
	  notes varchar(300),
	  delivery_date DATE,
	  finished BOOLEAN DEFAULT 0,
	  FOREIGN KEY(client_id) REFERENCES client(client_id),
	  FOREIGN KEY(deliveryman_id) REFERENCES user(user_id)
	)
	'''
	)
print('Tabela orders criada com sucesso.')


db.execute(
	'''
	CREATE TABLE order_products (
	  order_id integer NOT NULL,
	  product_id integer NOT NULL,
	  amount integer NOT NULL,
	  subtotal double(10,2) NOT NULL,
	  FOREIGN key(order_id) REFERENCES orders(order_id),
	  FOREIGN key(product_id) REFERENCES products(product_id)
	)
	'''
	)
print('Tabela order_products criada com sucesso.')

db.close()

'''
from app import db

class User(db.Model):
	__tablename__ = "users"

	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True)
	password = db.Column(db.String(20))
	user_name = db.Column(db.String(200))
	user_phone = db.Column(db.String(11))
	level = db.Column(db.String(20))
	available = db.Column(db.Boolean)

	delivery = db.relationship('Request', backref='user', lazy=True)

	def __init__ (self, username, password, name, level):
		self.username = username
		self.password = password
		self.name = name
		self.level = level

	def __repr__(self):
		return "<User %r>" %self.username


class Client(db.Model):
	__tablename__ = "clients"

	client_id = db.Column(db.Integer, primary_key=True)
	client_phone = db.Column(db.String(11), unique=True)
	client_name = db.Column(db.String(200))
	address = db.Column(db.String(400))
	neighborhood = db.Column(db.String(50))

	order = db.relationship('Request', backref='client', lazy=True)

	def __init__ (self, client_phone, client_name, address, neighborhood):
		self.client_phone = client_phone
		self.client_name = client_name
		self.address = address
		self.neighborhood = neighborhood

order_product = db.Table('ordered_products',
	db.Column('product_id', db.Integer, db.ForeignKey('products.product_id')),
	db.Column('request_id', db.Integer, db.ForeignKey('requests.request_id')),
	db.Column('amount', db.Integer),
	db.Column('subtotal', db.Float)
	)

class Product(db.Model):
	__tablename__ = "products"

	product_id = db.Column(db.Integer, primary_key=True)
	product_name = db.Column(db.String(50))
	category = db.Column(db.String(20))
	description = db.Column(db.String(200))
	unit_price = db.Column(db.Float)
	available = db.Column(db.Boolean)
	created_by = db.Column(db.String(20))
	created_at = db.Column(db.DateTime)
	modified_by = db.Column(db.String(20))
	modified_at = db.Column(db.DateTime)

	requests = db.relationship('Request', secondary=order_product, backref=db.backref('order', lazy='dynamic'))

	def __init__ (self, product_name, category, description, unit_price, created_by, created_at):
		self.product_name = product_name
		self.category = category
		self.description = description
		self.unit_price = unit_price
		self.available = available
		self.created_by = created_by
		self.created_at = created_at


class Request(db.Model):
	__tablename__ = "requests"

	request_id = db.Column(db.Integer, primary_key=True)
	client_id = db.Column(db.Integer, db.ForeignKey('client_id'), nullable=False)
	deliveryman_id = db.Column(db.Integer, db.ForeignKey('user_id'), nullable=False)
	request_date = db.Column(db.DateTime)
	total_invoice = db.Column(db.Float)
	payment_method = db.Column(db.String(20))
	change = db.Column(db.Float)
	NOTe = db.Column(db.Text)
	delivery_date = db.Column(db.DateTime)

	def __init__(self, client_id, deliveryman_id, request_date, total_invoice, payment_method, change, NOTe, delivery_date):
		self.client_id = client_id
		self.deliveryman_id = deliveryman_id
		self.request_date = request_date
		self.total_invoice = total_invoice
		self.payment_method = payment_method
		self.change = change
		self.NOTe = NOTe
		self.delivery_date = delivery_date
'''