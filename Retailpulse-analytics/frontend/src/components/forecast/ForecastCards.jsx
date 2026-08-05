import "./ForecastCards.css";

const ForecastCards = ({ dashboard }) => {
    const cards = [
        {
            title: "Total Predicted Demand",
            value: dashboard.total_predicted_demand || 0,
        },
        {
            title: "Products Expected to Run Out",
            value: dashboard.products_expected_to_run_out || 0,
        },
        {
            title: "High Growth Products",
            value: dashboard.high_growth_products || 0,
        },
        {
            title: "Slow Moving Products",
            value: dashboard.slow_moving_products || 0,
        },
        {
            title: "Forecast Accuracy",
            value: `${dashboard.forecast_accuracy || 0}%`,
        },
    ];

    return (
        <div className="forecast-cards">

            {cards.map((card, index) => (
                <div
                    className="forecast-card"
                    key={index}
                >
                    <h4>{card.title}</h4>

                    <h2>{card.value}</h2>
                </div>
            ))}

        </div>
    );
};

export default ForecastCards;