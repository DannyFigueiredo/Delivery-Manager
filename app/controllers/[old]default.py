''''
@app.route("/<request_id>")
@app.route("/", defaults={"request_id":00})
def index(request_id):
	return render_template('products.html', request_id=request_id)


@app.route("/register")
def register():
	return render_template('register.html')


@app.route("/login", methods=["GET","POST"])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		print(form.username.data)
		print(form.password.data)
	else:
		print(form.errors)

	return render_template('login.html', form=form)


@app.route("/sales")
def sales():
	return render_template('sales.html')

@app.route("/request")
def request():
	return render_template('request.html')

'''