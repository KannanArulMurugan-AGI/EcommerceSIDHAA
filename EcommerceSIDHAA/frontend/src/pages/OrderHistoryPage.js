import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const OrderHistoryPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    const fetchOrders = async () => {
      if (!isAuthenticated) {
        setError('Please log in to view your order history.');
        setLoading(false);
        return;
      }

      try {
        const { data } = await axios.get('/api/orders');
        setOrders(data.orders);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch order history');
        setLoading(false);
      }
    };

    fetchOrders();
  }, [user, isAuthenticated]);

  return (
    <div>
      <h1>Order History</h1>
      {loading ? (
        <h2>Loading...</h2>
      ) : error ? (
        <h2>{error}</h2>
      ) : orders.length === 0 ? (
        <p>You have no orders.</p>
      ) : (
        <div>
          {orders.map((order) => (
            <div key={order.id} style={{ border: '1px solid #ccc', margin: '1rem 0', padding: '1rem' }}>
              <h3>Order ID: {order.id}</h3>
              <p>Date: {new Date(order.created_at).toLocaleDateString()}</p>
              <h4>Total: ${order.total_price}</h4>
              <h5>Items:</h5>
              <ul>
                {order.items.map((item) => (
                  <li key={item.product_id}>
                    {item.name} - {item.quantity} x ${item.price}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default OrderHistoryPage;
