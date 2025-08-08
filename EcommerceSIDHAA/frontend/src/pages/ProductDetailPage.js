import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const ProductDetailPage = () => {
  const { id } = useParams();
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const { data } = await axios.get(`/api/products/${id}`);
        setProduct(data.product);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch product');
        setLoading(false);
      }
    };

    fetchProduct();
  }, [id]);

  const addToCartHandler = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    try {
      const config = {
        headers: {
          'Content-Type': 'application/json',
          'x-user-id': user.userId,
        },
      };

      await axios.post(
        '/api/cart/add',
        { product_id: product.id, quantity },
        config
      );

      setMessage('Item added to cart!');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to add item to cart');
    }
  };

  return (
    <div>
      {loading ? (
        <h2>Loading...</h2>
      ) : error ? (
        <h2>{error}</h2>
      ) : product ? (
        <div>
          <h1>{product.name}</h1>
          <img src={product.image_url} alt={product.name} style={{ maxWidth: '400px' }} />
          <p>{product.description}</p>
          <h2>${product.price}</h2>

          <div>
            <label>Qty:</label>
            <input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value))}
              min="1"
            />
            <button onClick={addToCartHandler}>Add to Cart</button>
          </div>
          {message && <p style={{ color: 'green' }}>{message}</p>}
        </div>
      ) : (
        <h2>Product not found</h2>
      )}
    </div>
  );
};

export default ProductDetailPage;
