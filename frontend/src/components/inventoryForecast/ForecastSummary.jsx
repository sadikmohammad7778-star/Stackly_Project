import "./ForecastSummary.css";

const ForecastSummary = ({ summary }) => {

    if (!summary) {
        return null;
    }

    return (
        <div className="forecast-summary-grid">

            <div className="forecast-summary-card">
                <span>Products Requiring Reorder</span>
                <strong>
                    {summary.products_requiring_reorder}
                </strong>
            </div>

            <div className="forecast-summary-card">
                <span>Stockout Risk</span>
                <strong>
                    {summary.products_at_stockout_risk}
                </strong>
            </div>

            <div className="forecast-summary-card">
                <span>Overstocked Products</span>
                <strong>
                    {summary.overstocked_products}
                </strong>
            </div>

            <div className="forecast-summary-card">
                <span>Healthy Products</span>
                <strong>
                    {summary.healthy_products}
                </strong>
            </div>

        </div>
    );
};

export default ForecastSummary;