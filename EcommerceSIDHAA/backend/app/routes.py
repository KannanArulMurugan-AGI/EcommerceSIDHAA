from flask import request, jsonify
from app import app, db
from app.models import User, Product, Cart, CartItem
# No utils needed for now

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not 'username' in data or not 'email' in data or not 'password' in data:
        return jsonify({'message': 'Missing data'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not 'email' in data or not 'password' in data:
        return jsonify({'message': 'Missing data'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    return jsonify({'user_id': user.id}), 200


@app.route('/profile', methods=['GET'])
def profile():
    user_id = request.headers.get('x-user-id')
    if not user_id:
        return jsonify({'message': 'User ID is missing!'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    return jsonify({
        'username': user.username,
        'email': user.email
    })


@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data or not 'name' in data or not 'price' in data:
        return jsonify({'message': 'Missing data'}), 400

    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        image_url=data.get('image_url', '')
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({'message': 'Product created successfully'}), 201


@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    output = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'image_url': product.image_url
        }
        output.append(product_data)

    return jsonify({'products': output})


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    product_data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_url': product.image_url
    }
    return jsonify({'product': product_data})


@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()

        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.image_url = data.get('image_url', product.image_url)

        db.session.commit()

        return jsonify({'message': 'Product updated successfully'})
    except Exception as e:
        app.logger.error(f"Error updating product: {e}")
        return jsonify({'message': 'Internal server error'}), 500


@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully'})


@app.route('/cart', methods=['GET'])
def get_cart():
    user_id = request.headers.get('x-user-id')
    if not user_id:
        return jsonify({'message': 'User ID is missing!'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    cart = user.cart
    if not cart:
        return jsonify({'items': [], 'total': 0})

    output = []
    total = 0
    for item in cart.items:
        item_data = {
            'id': item.id,
            'product_id': item.product_id,
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity
        }
        output.append(item_data)
        total += item.product.price * item.quantity

    return jsonify({'items': output, 'total': total})


@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    user_id = request.headers.get('x-user-id')
    if not user_id:
        return jsonify({'message': 'User ID is missing!'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    data = request.get_json()
    if not data or not 'product_id' in data or not 'quantity' in data:
        return jsonify({'message': 'Missing data'}), 400

    product_id = data['product_id']
    quantity = data['quantity']

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found!'}), 404

    cart = user.cart
    if not cart:
        cart = Cart(user_id=user.id)
        db.session.add(cart)

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({'message': 'Item added to cart successfully'})


@app.route('/cart/update/<int:product_id>', methods=['PUT'])
def update_cart_item(product_id):
    user_id = request.headers.get('x-user-id')
    if not user_id:
        return jsonify({'message': 'User ID is missing!'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    cart = user.cart
    if not cart:
        return jsonify({'message': 'Cart not found!'}), 404

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({'message': 'Item not in cart!'}), 404

    data = request.get_json()
    if not data or not 'quantity' in data:
        return jsonify({'message': 'Missing quantity'}), 400

    quantity = data['quantity']
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity

    db.session.commit()
    return jsonify({'message': 'Cart updated successfully'})


@app.route('/cart/remove/<int:product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    user_id = request.headers.get('x-user-id')
    if not user_id:
        return jsonify({'message': 'User ID is missing!'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    cart = user.cart
    if not cart:
        return jsonify({'message': 'Cart not found!'}), 404

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({'message': 'Item not in cart!'}), 404

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({'message': 'Item removed from cart successfully'})
