import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import ProductCard from '../components/ProductCard';
import PaginationControls from '../components/PaginationControls';
const ProductPage = () => {
  const [products, setProducts] = useState([]);
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    hasNext: false,
    hasPrev: false,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchProducts = useCallback(async (page) => {
    try {
      setLoading(true);
      const { data } = await axios.get(`http://127.0.0.1:5000/products?page=${page}&per_page=8`);
      setProducts(data.products);
      setPagination({
        currentPage: data.current_page,
        totalPages: data.total_pages,
        hasNext: data.has_next,
        hasPrev: data.has_prev,
      });
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch products');
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProducts(pagination.currentPage);
  }, [fetchProducts, pagination.currentPage]);

  const handlePageChange = (newPage) => {
    if (newPage > 0 && newPage <= pagination.totalPages) {
      setPagination(prev => ({ ...prev, currentPage: newPage }));
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">All Products</h1>
      {loading ? (
        <div className="text-center"><h2>Loading...</h2></div>
      ) : error ? (
        <div className="text-center text-red-500"><h2>{error}</h2></div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
          <div className="mt-8">
            <PaginationControls pagination={pagination} onPageChange={handlePageChange} />
          </div>
        </>
      )}
    </div>
  );
};

export default ProductPage;
