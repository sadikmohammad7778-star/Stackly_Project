import "./ForecastTable.css";

const ForecastTable = ({ products }) => {
  return (
    <div className="forecast-table">
      <h3>Product Forecasts</h3>

      <table>
        <thead>
          <tr>
            <th>Product</th>
            <th>Current Stock</th>
            <th>Historical Sales</th>
            <th>Predicted Demand</th>
            <th>Forecast Period</th>
            <th>Confidence</th>
          </tr>
        </thead>

        <tbody>
          {products && products.length > 0 ? (
            products.map((product) => (
              <tr key={product.product_id}>
                <td>{product.product_name}</td>
                <td>{product.current_stock}</td>
                <td>{product.historical_sales}</td>
                <td>{product.predicted_demand}</td>
                <td>{product.forecast_period}</td>
                <td>{product.confidence_score}%</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="6">
                No Forecast Data Found
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ForecastTable;