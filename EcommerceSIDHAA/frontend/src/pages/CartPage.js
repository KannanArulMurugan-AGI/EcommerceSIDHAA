import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

const CartPage = () => {
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user, isAuthenticated } = useAuth();

  const fetchCart = useCallback(async () => {
    if (!isAuthenticated) {
      setError('Please log in to view your cart.');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const config = {
        headers: {
          'x-user-id': user.userId,
        },
      };
      const { data } = await axios.get('http://127.0.0.1:5000/cart', config);
      setCart(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch cart');
      setLoading(false);
    }
  }, [user, isAuthenticated]);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const updateQuantityHandler = async (productId, quantity) => {
    try {
      const config = {
        headers: {
          'Content-Type': 'application/json',
          'x-user-id': user.userId,
        },
      };
      await axios.put(
        `http://127.0.0.1:5000/cart/update/${productId}`,
        { quantity },
        config
      );
      fetchCart(); // Refetch cart to show updated state
    } catch (err) {
      setError('Failed to update cart');
    }
  };

  const removeFromCartHandler = async (productId) => {
    try {
      const config = {
        headers: {
          'x-user-id': user.userId,
        },
      };
      await axios.delete(`http://127.0.0.1:5000/cart/remove/${productId}`, config);
      fetchCart(); // Refetch cart
    } catch (err) {
      setError('Failed to remove item from cart');
    }
  };

  return (
    <div>
      <h1>Shopping Cart</h1>
      {loading ? (
        <h2>Loading...</h2>
      ) : error ? (
        <h2>{error}</h2>
      ) : cart.items.length === 0 ? (
        <div>
          <p>Your cart is empty.</p>
          <Link to="/">Go Shopping</Link>
        </div>
      ) : (
        <div>
          {cart.items.map((item) => (
            <div key={item.id}>
              <h2>{item.name}</h2>
              <p>Price: ${item.price}</p>
              <input
                type="number"
                value={item.quantity}
                onChange={(e) => updateQuantityHandler(item.product_id, Number(e.target.value))}
                min="1"
              />
              <p>Subtotal: ${item.price * item.quantity}</p>
              <button onClick={() => removeFromCartHandler(item.product_id)}>Remove</button>
            </div>
          ))}
          <h2>Total: ${cart.total}</h2>
        </div>
      )}
    </div>
  );
};

export default CartPage;
