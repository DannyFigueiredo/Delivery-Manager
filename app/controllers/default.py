from flask import *
from app import app
from app.models import dataManipulation as dm
import sqlite3, hashlib
import requests
from datetime import *


##############################
# Area do Cliente
##############################

# Obtem os dados relevantes do loggin
def getLoggin():
	if 'clientId' not in session:
			isClient = False
			clientName = ''
			numProducts = 0
	else:
		clientId = session['clientId']
		isClient = True
		with sqlite3.connect('storage.db') as db:
			cur = db.cursor()
			sql = dm.selectClients('client_id', clientId)
			cur.execute(sql)
			clientId, _, clientName, _, _, _ = cur.fetchone()
		db.close()
		numProducts = dm.countProductsOnCart(clientId)
		numProducts = numProducts[0]
		clientName = clientName.split()
		clientName = clientName[0]

	return (isClient, clientName, numProducts)


# Página inicial da aplicacao
@app.route('/')
def home():
	isClient, clientName, numProducts = getLoggin()
	
	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.selectProducts()
		cur.execute(sql)
		productData = cur.fetchall()
		sql = dm.selectCategories()
		cur.execute(sql)
		categoryData = cur.fetchall()
	productData = iterator(productData)

	return render_template('home.html', productData=productData, isClient=isClient, clientName=clientName, numProducts=numProducts, categoryData=categoryData)


# Obtem os itens da lista de compra
@app.route('/carrinho')
def order():
	if 'clientId' not in session:
		shoppingCart = True
		url = render_template('errorMessage.html', shoppingCart=shoppingCart)
	else:
		orderId = session['orderId']
		clientId = session['clientId']

		with sqlite3.connect('storage.db') as db:
			cur = db.cursor()
			sql = dm.selectClients('client_id', clientId)
			cur.execute(sql)
			_, _, clientName, clientAddress, clientNeighborhood, clientLandmark = cur.fetchone()
			sql = dm.selectShoppingCart(orderId)
			cur.execute(sql)
			cartData = cur.fetchall()
		cartData = iterator(cartData)

		totalOrder = dm.totalOrder(orderId)
		totalOrder = totalOrder[0]

		url = render_template('shopCart.html', orderId=orderId, cartData=cartData, totalOrder=totalOrder, clientName=clientName, clientAddress=clientAddress, clientNeighborhood=clientNeighborhood, clientLandmark=clientLandmark)

	return url 


# Filtra os produtos por categoria
@app.route('/categoria/<categoryName>')
def filterCategory(categoryName):
	isClient, clientName, numProducts = getLoggin()

	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.selectProducts('category', categoryName)
		cur.execute(sql)
		productData = cur.fetchall()
		sql = dm.selectCategories()
		cur.execute(sql)
		categoryData = cur.fetchall()
	productData = iterator(productData)

	return render_template('displayCategory.html', productData=productData, isClient=isClient, clientName=clientName, numProducts=numProducts, categoryData=categoryData, categoryName=categoryName)


# Obtem as características do produto
@app.route('/produto/<productId>')
def showProduct(productId):
	isClient, clientName, numProducts = getLoggin()

	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.selectProducts('product_id', productId)
		cur.execute(sql)
		_, productImage, productName, productCategory, productDescription, productUnitPrice = cur.fetchone()
	db.close()
	
	return render_template('product.html', clientName=clientName, numProducts=numProducts, isClient=isClient, productImage=productImage, productName=productName, productDescription=productDescription, productId=productId, productCategory=productCategory, productUnitPrice=productUnitPrice)	


# Adiciona o Produto ao Carrinho
@app.route('/adicionarAoCarrinho/<productId>', methods=["GET", "POST"])
def addToCart(productId):
	isClient, clientName, numProducts = getLoggin()

	amountProduct = request.form.get('amountProduct')

	if 'clientId' not in session:
		session['amountProduct'] = amountProduct
		session['productId'] = productId
		
		url = render_template('searchClient.html')

	else:
		orderId = session['orderId']		

		with sqlite3.connect('storage.db') as db:
			cur = db.cursor()
			sql = dm.selectExistsProduct(orderId, productId)
			cur.execute(sql)
			existProduct = cur.fetchone()
			existProduct = existProduct[0]
			if (existProduct == 'Y'):
				sql = dm.updateOrderProduct(orderId, productId, amountProduct)
			else:
				sql = dm.insertOrderProducts(orderId, productId, amountProduct)
			cur.execute(sql)
			db.commit()
		db.close()

		url = redirect(url_for('home'))

	return url


# Remove item do carrinho
@app.route('/removeProduto/<productId>')
def removeProduct(productId):
	orderId = session['orderId']

	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.deleteOrderProducts(orderId, productId)
		cur.execute(sql)
		db.commit()
	db.close()

	return redirect(url_for('order'))


@app.route('/finalizarCompra', methods=["GET", "POST"])
def checkOut():
	paymentMethodOrder = request.form.get('paymentMethodOrder')
	changeOrder = request.form.get('changeOrder')
	notesOrder = request.form.get('notesOrder')

	orderId = session['orderId']

	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.updateOrder(orderId, paymentMethodOrder, notesOrder, changeOrder)
		cur.execute(sql)
		db.commit()
	db.close()

	return redirect(url_for('success'))

# Verifica se o cliente já está na base
@app.route('/cliente', methods=["GET", "POST"])
def searchClient():
	clientPhone = request.form.get('clientPhone')
	for i in '() -':
		clientPhone = clientPhone.replace(i, '')

	status = dm.findClient(clientPhone)

	if (status == 'Cliente cadastrado'):
		amountProduct = session['amountProduct']
		productId = session['productId']

		with sqlite3.connect('storage.db') as db:
			cur = db.cursor()
			sql = dm.selectClients('client_phone', clientPhone)
			cur.execute(sql)
			clientId, _, clientName, _, _, _ = cur.fetchone()
			sql = dm.insertOrder(clientId)
			cur.execute(sql)
			db.commit()
			orderId = dm.maxOrder(clientId)
			sql = dm.insertOrderProducts(orderId, productId, amountProduct)
			cur.execute(sql)
			db.commit()
		db.close()

		session['clientId'] = clientId
		session['clientName'] = clientName.split()[0]
		session['orderId'] = orderId

		url = redirect(url_for('showClientDetails'))

	else:
		with sqlite3.connect('storage.db') as db:
			cur = db.cursor()
			sql = dm.insertClient(clientPhone)
			cur.execute(sql)
			db.commit()
			sql = dm.selectClients('client_phone', clientPhone)
			cur.execute(sql)
			clientId, _, _, _, _, _ = cur.fetchone()
		db.close()

		session['clientId'] = clientId

		url = redirect(url_for('registerPage'))
	
	return url


# Registra o cliente
@app.route('/registro')
def registerPage():
	clientId = session['clientId']

	if 'isUpdate' in session:
		isUpdate = session['isUpdate']
	else:
		isUpdate = False

	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.selectClients('client_id', clientId)
		cur.execute(sql)
		_, clientPhone, clientName, clientAddress, clientNeighborhood, clientLandmark = cur.fetchone()
	db.close()

	clientPhone = clientPhone[0:2] + ' ' + clientPhone[2:7] + '-' + clientPhone[7:]

	return render_template('register.html', clientPhone=clientPhone, isUpdate=isUpdate, clientName=clientName, clientAddress=clientAddress, clientNeighborhood=clientNeighborhood, clientLandmark=clientLandmark)


# Finalização do cadastro do cliente
@app.route('/finalizaCadastroCliente', methods=["GET", "POST"])
def registerClient():
	clientName = request.form.get('clientName').upper()
	clientAddress = request.form.get('clientAddress')
	clientNeighborhood = request.form.get('clientNeighborhood')
	clientLandmark = request.form.get('clientLandmark')

	clientId = session['clientId']

	if ('isUpdate' in session):
		with sqlite3.connect('storage.db') as db:
			cur = db.cursor()
			sql = dm.updateClient(clientId, clientName, clientAddress, clientNeighborhood, clientLandmark)
			cur.execute(sql)
			db.commit()
		db.close()

	else:	
		productId = session['productId']
		amountProduct = session['amountProduct']

		with sqlite3.connect('storage.db') as db:
			cur = db.cursor()
			# Fazer update do cadastro do cliente
			sql = dm.updateClient(clientId, clientName, clientAddress, clientNeighborhood, clientLandmark)
			cur.execute(sql)
			db.commit()
			# Criar um novo numero de pedido
			sql = dm.insertOrder(clientId)
			cur.execute(sql)
			db.commit()
			# Cadastrar o primeiro produto no pedido
			orderId = dm.maxOrder(clientId)
			sql = dm.insertOrderProducts(orderId, productId, amountProduct)
			cur.execute(sql)
			db.commit()
		db.close()

		session['orderId'] = orderId

	return redirect(url_for('home'))


# Expõe as informações que que temos do cliente
@app.route('/mostrarCadastro')
def showClientDetails():
	clientId = session['clientId']

	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.selectClients('client_id', clientId)
		cur.execute(sql)
		_, clientPhone, clientName, clientAddress, clientNeighborhood, clientLandmark = cur.fetchone()
	db.close()

	clientPhone = clientPhone[0:2] + ' ' + clientPhone[2:7] + '-' + clientPhone[7:]

	return render_template('descriptionClient.html', clientPhone=clientPhone, clientName=clientName, clientAddress=clientAddress, clientNeighborhood=clientNeighborhood, clientLandmark=clientLandmark)


@app.route('/editarCliente')
def updateClient():
	session['isUpdate'] = True
	return redirect(url_for('registerPage'))

@app.route('/success')
def success ():
	orderId = session['orderId']

	del session['amountProduct']
	del session['clientId']
	del session['orderId']
	del session['productId']
	if 'isUpdate' in session:
		del session['isUpdate']
	
	return render_template('success.html', orderId=orderId)



##############################
# Area do Administrador
##############################

# Menu principal
@app.route('/manager')
def userMenu():
	return render_template('userMenu.html')

@app.route('/pedidosHoje')
def getpedidos():
	today = datetime.today().strftime('%d/%m/%Y')

	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.productsToBuy(today)
		cur.execute(sql)
		productsToday = cur.fetchall()
		# Todos os pedidos do dia
		sql = dm.ordersForToday(today)
		cur.execute(sql)
		ordersData = cur.fetchall()
	ordersData = iterator(ordersData)

	return render_template('orders.html', today=today, productsToday=productsToday, ordersData=ordersData)


@app.route('/pedidoDetalhado/<orderId>')
def orderDetails(orderId):
	today = datetime.today().strftime('%d/%m/%Y')

	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.orderDetails(orderId)
		cur.execute(sql)
		orderDate, clientName, clientPhone, clientAddress, clientNeighborhood, clientLandmark, paymentMethodOrder, changeOrder, notesOrder = cur.fetchone()
		sql = dm.selectShoppingCart(orderId)
		cur.execute(sql)
		cartData = cur.fetchall()
	cartData = iterator(cartData)

	clientPhone = clientPhone[0:2] + ' ' + clientPhone[2:7] + '-' + clientPhone[7:]

	totalOrder = dm.totalOrder(orderId)
	totalOrder = totalOrder[0]

	return render_template('orderDetails.html', totalOrder=totalOrder, cartData=cartData, orderId=orderId, orderDate=orderDate, clientName=clientName, clientPhone= clientPhone, clientAddress=clientAddress, clientNeighborhood=clientNeighborhood, clientLandmark=clientLandmark, paymentMethodOrder=paymentMethodOrder, changeOrder=changeOrder, notesOrder=notesOrder)


@app.route('/editarProdutos')
def showProducts():
	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.getProducts()
		cur.execute(sql)
		productData = cur.fetchall()
	productData = iterator(productData)

	return render_template('showRegisteredProduct.html', productData=productData)


@app.route('/updateProduct/<productId>')
def updatePage(productId):
	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.selectProducts('product_id', productId, unavailable=True)
		cur.execute(sql)
		_, _, _, _, descriptionProduct, unitPriceProduct, availableProduct = cur.fetchone()
	db.close()

	return render_template('updateProduct.html', productId=productId, descriptionProduct=descriptionProduct, unitPriceProduct=unitPriceProduct, availableProduct=availableProduct)


@app.route('/commit/<productId>', methods=["GET", "POST"])
def productForm(productId):
	descriptionProduct = request.form.get('descriptionProduct')
	unitPriceProduct = request.form.get('unitPriceProduct')
	availableProduct = request.form.get('availableProduct')

	print(availableProduct)

	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.updateProduct(productId, descriptionProduct, unitPriceProduct, availableProduct)
		cur.execute(sql)
		db.commit()
	db.close()

	return redirect(url_for('showProducts'))


@app.route('/adicionarProduto')
def addProductPage():
	return render_template('addProduct.html')


@app.route('/commitInsertProduct', methods=["GET", "POST"])
def addProduct():
	imageProduct = request.form.get('imageProduct')
	nameProduct = request.form.get('nameProduct')
	categoryProduct = request.form.get('categoryProduct')
	descriptionProduct = request.form.get('descriptionProduct')
	unitPriceProduct = request.form.get('unitPriceProduct')
	availableProduct = request.form.get('availableProduct')
	create_by = 1

	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.insertProdut(imageProduct, nameProduct, categoryProduct, descriptionProduct, unitPriceProduct, availableProduct, create_by)
		cur.execute(sql)
		db.commit()
	db.close()

	return redirect(url_for('showProducts'))

@app.route('/historico')
def history():
	with sqlite3.connect('storage.db') as db:
		cur = db.cursor()
		sql = dm.history()
		cur.execute(sql)
		faturamento = cur.fetchall()
	faturamento = iterator(faturamento)

	return render_template('history.html', faturamento=faturamento)



##############################
# Area de Testes 
##############################

@app.route('/limparCookie/<cookieName>')
def delCookie(cookieName):
	if cookieName in session:
		del session[cookieName]
		m = "Cookie removido"
	else:
		m = "Não deu certo"

	return m

@app.route('/mostrarCookies')
def showCookies():
	m = '''
	<table border='1'>
	    <tr>
	        <td>Chave    </td>
	        <td>Valor    </td>
	    </tr>'''

	for key in session:
		m = m + '''<tr>
        		<td>{}     </td>
        		<td>{}     </td>
    		</tr>'''
		m = m.format(key, session[key])

	m = m + '</table>'

	return m






##############################
# Funções de Apoio
##############################

def iterator(data):
	ans = []
	x = 0

	while (x < len(data)):
		cur = []

		for y in range(11):
			if (x >= len(data)):
				break
			cur.append(data[x])
			x += 1

		ans.append(cur)
	return ans



####################
# High Lights
####################
# Criar novas linha em pedido a cada fez que o usuário:
# 	for encontrado na base de clientes
# 	terminar de se registrar