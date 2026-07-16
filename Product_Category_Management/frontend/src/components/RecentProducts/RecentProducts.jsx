import { useEffect, useState } from "react";
import axios from "axios";
import "./RecentProducts.css";

function RecentProducts() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/products");
      setProducts(response.data);
    } catch (error) {
      console.error("Error fetching products:", error);
    }
  };

  return (
    <div className="recent-products">

      <h3>Recent Products</h3>

      <table>

        <thead>
          <tr>
            <th>Product</th>
            <th>SKU</th>
            <th>Brand</th>
            <th>Price</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>

          {products.map((product) => (
            <tr key={product.id}>
              <td>{product.name}</td>
              <td>{product.sku}</td>
              <td>{product.brand}</td>
              <td>₹ {product.unit_price}</td>
              <td>{product.status}</td>
            </tr>
          ))}

        </tbody>

      </table>

    </div>
  );
}

export default RecentProducts;