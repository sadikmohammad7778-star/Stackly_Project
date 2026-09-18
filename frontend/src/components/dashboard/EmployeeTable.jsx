import { useEffect, useState } from "react";
import "./EmployeeTable.css";

import { getTopProducts } from "../../api/DashboardApi";

export default function EmployeeTable() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    loadTopProducts();
  }, []);

  const loadTopProducts = async () => {
    try {
      const response = await getTopProducts();
      setProducts(response);
    } catch (error) {
      console.error("Error loading top products:", error);
    }
  };

  return (
    <div className="employee-table">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Product Name</th>
            <th>Quantity Sold</th>
          </tr>
        </thead>

        <tbody>
          {products.length > 0 ? (
            products.map((product, index) => (
              <tr key={index}>
                <td>{index + 1}</td>
                <td>{product.product_name}</td>
                <td>{product.quantity_sold}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="3" style={{ textAlign: "center" }}>
                No product data available
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}