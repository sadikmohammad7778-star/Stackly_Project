import "./RecommendationTable.css";

const RecommendationTable = ({ recommendations }) => {
    return (
        <div className="recommendation-table">

            <h3>Inventory Recommendations</h3>

            <table>

                <thead>

                    <tr>
                        <th>Product</th>
                        <th>Available Stock</th>
                        <th>Reorder Level</th>
                        <th>Predicted Demand</th>
                        <th>Recommendation</th>
                    </tr>

                </thead>

                <tbody>

                    {recommendations.length > 0 ? (

                        recommendations.map((item) => (

                            <tr key={item.product_id}>

                                <td>{item.product_name}</td>

                                <td>{item.current_stock}</td>

                                <td>{item.reorder_level}</td>

                                <td>{item.predicted_demand}</td>

                                <td>

                                    <span
                                        className={`status ${item.recommendation
                                            .replace(/\s+/g, "-")
                                            .toLowerCase()}`}
                                    >
                                        {item.recommendation}
                                    </span>

                                </td>

                            </tr>

                        ))

                    ) : (

                        <tr>

                            <td colSpan="5">
                                No Recommendations Found
                            </td>

                        </tr>

                    )}

                </tbody>

            </table>

        </div>
    );
};

export default RecommendationTable;