import "./CategoryForecastTable.css";

const CategoryForecastTable = ({ categories }) => {

    return (

        <div className="category-forecast-table">

            <h3>Category Forecast</h3>

            <table>

                <thead>

                    <tr>

                        <th>Category</th>

                        <th>Total Historical Sales</th>

                        <th>Predicted Demand</th>

                        <th>Growth %</th>

                        <th>Forecast Period</th>

                    </tr>

                </thead>

                <tbody>

                    {categories.length > 0 ? (

                        categories.map((category) => (

                            <tr key={category.category_id}>

                                <td>
                                    {category.category_name}
                                </td>

                                <td>
                                    {category.total_historical_sales}
                                </td>

                                <td>
                                    {category.predicted_demand}
                                </td>

                                <td>
                                    {category.expected_growth_percentage}%
                                </td>

                                <td>
                                    {category.forecast_period}
                                </td>

                            </tr>

                        ))

                    ) : (

                        <tr>

                            <td colSpan="5">

                                No Category Forecast Found

                            </td>

                        </tr>

                    )}

                </tbody>

            </table>

        </div>

    );

};

export default CategoryForecastTable;