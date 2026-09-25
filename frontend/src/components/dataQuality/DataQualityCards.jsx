const DataQualityCards = ({ dashboard }) => {
  const cards = [
    {
      title: "Total Checked",
      value: dashboard?.total_checked ?? 0,
    },
    {
      title: "Valid Records",
      value: dashboard?.valid_records ?? 0,
    },
    {
      title: "Open Issues",
      value: dashboard?.open_issues ?? 0,
    },
    {
      title: "Errors",
      value: dashboard?.errors ?? 0,
    },
    {
      title: "Warnings",
      value: dashboard?.warnings ?? 0,
    },
    {
      title: "Resolved Issues",
      value: dashboard?.resolved_issues ?? 0,
    },
  ];

  return (
    <div className="data-quality-cards">
      {cards.map((card) => (
        <div className="data-quality-card" key={card.title}>
          <div className="data-quality-card-title">
            {card.title}
          </div>

          <div className="data-quality-card-value">
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
};

export default DataQualityCards;