from flask import request, jsonify
from app import app, db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User, Product, Cart, CartItem, Order, OrderItem

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

    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)


@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

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
@jwt_required()
def get_cart():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    cart = user.cart
    if not cart:
        return jsonify({"items": [], "total": 0})

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
@jwt_required()
def add_to_cart():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

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
        db.session.flush() # Use flush to get the cart id before commit

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({'message': 'Item added to cart successfully'})


@app.route('/cart/update/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(product_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

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
@jwt_required()
def remove_from_cart(product_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    cart = user.cart
    if not cart:
        return jsonify({'message': 'Cart not found!'}), 404

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({'message': 'Item not in cart!'}), 404

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({'message': 'Item removed from cart successfully'})


@app.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    data = request.get_json()
    if not data or not 'shipping_address' in data or not 'shipping_city' in data or not 'shipping_postal_code' in data or not 'shipping_country' in data:
        return jsonify({'message': 'Shipping information is missing!'}), 400

    cart = user.cart
    if not cart or not cart.items:
        return jsonify({'message': 'Cart is empty!'}), 400

    total_price = 0
    for item in cart.items:
        total_price += item.product.price * item.quantity

    order = Order(
        user_id=user.id,
        total_price=total_price,
        shipping_address=data['shipping_address'],
        shipping_city=data['shipping_city'],
        shipping_postal_code=data['shipping_postal_code'],
        shipping_country=data['shipping_country']
    )
    db.session.add(order)
    db.session.flush()

    for item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.session.add(order_item)

    # Clear the cart
    for item in cart.items:
        db.session.delete(item)

    db.session.delete(cart)
    db.session.commit()

    return jsonify({'message': 'Checkout successful, order created', 'order_id': order.id}), 201


@app.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    orders = user.orders
    output = []
    for order in orders:
        order_data = {
            'id': order.id,
            'created_at': order.created_at,
            'total_price': order.total_price,
            'items': []
        }
        for item in order.items:
            item_data = {
                'product_id': item.product_id,
                'name': item.product.name,
                'quantity': item.quantity,
                'price': item.price
            }
            order_data['items'].append(item_data)
        output.append(order_data)

    return jsonify({'orders': output})
