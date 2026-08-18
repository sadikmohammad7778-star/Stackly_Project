import "./RecommendationPanel.css";

const RecommendationPanel = ({ recommendation }) => {

    if (!recommendation) {
        return null;
    }

    return (
        <div className="recommendation-panel">

            <h2>Inventory Recommendation</h2>

            <div className="recommendation-product">
                <strong>{recommendation.product_name}</strong>
                <span>{recommendation.sku}</span>
            </div>

            <div className="recommendation-table">

                <div className="recommendation-row header">
                    <span>Metric</span>
                    <span>Current</span>
                    <span>Recommended</span>
                </div>

                <div className="recommendation-row">
                    <span>Stock</span>
                    <span>{recommendation.current_stock}</span>
                    <span>
                        {recommendation.recommended_reorder_quantity > 0
                            ? recommendation.current_stock +
                              recommendation.recommended_reorder_quantity
                            : recommendation.current_stock}
                    </span>
                </div>

                <div className="recommendation-row">
                    <span>Daily Demand</span>
                    <span>
                        {recommendation.average_daily_sales}
                    </span>
                    <span>
                        {recommendation.average_daily_sales}
                    </span>
                </div>

                <div className="recommendation-row">
                    <span>Reorder Point</span>
                    <span>
                        {recommendation.reorder_point}
                    </span>

                    <span>
                        {recommendation.reorder_point}
                    </span>
                </div>

                <div className="recommendation-row">
                    <span>Safety Stock</span>
                    <span>
                        {recommendation.safety_stock}
                    </span>
                    <span>
                        {recommendation.safety_stock}
                    </span>
                </div>

            </div>

            <div className="recommendation-status">

                <strong>
                    {recommendation.recommendation}
                </strong>

                <span>
                    Risk: {recommendation.stock_risk}
                </span>

            </div>

        </div>
    );
};

export default RecommendationPanel;