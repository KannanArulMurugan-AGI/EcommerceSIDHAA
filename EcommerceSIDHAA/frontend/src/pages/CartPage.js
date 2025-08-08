import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const CartPage = () => {
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Hardcoded user ID for demonstration purposes, as there is no global auth state
  const userId = 1;
  const apiHeaders = { 'x-user-id': userId };

  const fetchCart = useCallback(async () => {
    try {
      setLoading(true);
      const { data } = await axios.get('http://127.0.0.1:5000/cart', { headers: apiHeaders });
      setCart(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch cart. Please login or add items to your cart.');
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const handleUpdateQuantity = async (productId, newQuantity) => {
    try {
      await axios.put(`http://127.0.0.1:5000/cart/update/${productId}`,
        { quantity: newQuantity },
        { headers: apiHeaders }
      );
      fetchCart(); // Refetch cart to show updated state
    } catch (err) {
      setError('Failed to update cart item.');
    }
  };

  const handleRemoveItem = async (productId) => {
    try {
      await axios.delete(`http://127.0.0.1:5000/cart/remove/${productId}`, { headers: apiHeaders });
      fetchCart(); // Refetch cart
    } catch (err) {
      setError('Failed to remove cart item.');
    }
  };

  if (loading) {
    return <div className="text-center py-10"><h2>Loading Cart...</h2></div>;
  }

  if (error) {
    return <div className="text-center py-10 text-red-500"><h2>{error}</h2></div>;
  }

  return (
    <div className="bg-gray-100 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Your Shopping Cart</h1>

        {cart.items.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow-md text-center">
            <h2 className="text-2xl font-semibold mb-4">Your cart is empty.</h2>
            <Link to="/products" className="text-indigo-600 hover:text-indigo-800 font-medium">
              Continue Shopping &rarr;
            </Link>
          </div>
        ) : (
          <div className="lg:grid lg:grid-cols-3 lg:gap-8">
            {/* Cart Items */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-md">
                <ul className="divide-y divide-gray-200">
                  {cart.items.map((item) => (
                    <li key={item.product_id} className="p-6 flex">
                      {/* In a real app, you'd have an image here */}
                      <div className="ml-4 flex-1 flex flex-col">
                        <div>
                          <div className="flex justify-between text-base font-medium text-gray-900">
                            <h3>{item.name}</h3>
                            <p className="ml-4">${(item.price * item.quantity).toFixed(2)}</p>
                          </div>
                          <p className="mt-1 text-sm text-gray-500">${item.price.toFixed(2)} each</p>
                        </div>
                        <div className="flex-1 flex items-end justify-between text-sm mt-4">
                          <div className="flex items-center">
                            <button onClick={() => handleUpdateQuantity(item.product_id, item.quantity - 1)} className="px-2 py-1 border rounded-l">-</button>
                            <span className="px-4 py-1 border-t border-b">{item.quantity}</span>
                            <button onClick={() => handleUpdateQuantity(item.product_id, item.quantity + 1)} className="px-2 py-1 border rounded-r">+</button>
                          </div>
                          <div className="flex">
                            <button onClick={() => handleRemoveItem(item.product_id)} type="button" className="font-medium text-indigo-600 hover:text-indigo-500">Remove</button>
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Order Summary */}
            <div className="mt-8 lg:mt-0">
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-lg font-medium text-gray-900">Order summary</h2>
                <div className="mt-6 space-y-4">
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-gray-600">Subtotal</p>
                    <p className="text-sm font-medium text-gray-900">${cart.total.toFixed(2)}</p>
                  </div>
                  {/* Add more lines for shipping, taxes etc. here */}
                  <div className="border-t border-gray-200 pt-4 flex items-center justify-between">
                    <p className="text-base font-medium text-gray-900">Order total</p>
                    <p className="text-base font-medium text-gray-900">${cart.total.toFixed(2)}</p>
                  </div>
                </div>
                <div className="mt-6">
                  <button className="w-full bg-indigo-600 text-white py-3 px-6 rounded-md font-medium hover:bg-indigo-700">
                    Proceed to Checkout
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CartPage;
