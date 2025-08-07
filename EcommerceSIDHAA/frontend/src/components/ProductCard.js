import React from 'react';
import { Link } from 'react-router-dom';

const ProductCard = ({ product }) => {
  return (
    <div className="card">
      <Link to={`/product/${product.id}`}>
        <img src={product.image_url} alt={product.name} className="card-img" />
      </Link>
      <div className="card-body">
        <Link to={`/product/${product.id}`}>
          <h2>{product.name}</h2>
        </Link>
        <p>${product.price}</p>
      </div>
    </div>
  );
};

export default ProductCard;
