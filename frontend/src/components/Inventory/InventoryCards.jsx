import "./InventoryCards.css";

export default function InventoryCards({ data }) {
  const cards = [
    {
      title: "Total Products",
      value: data.total_products || 0,
    },
    {
      title: "Total Stock",
      value: data.total_inventory_quantity || 0,
    },
    {
      title: "Low Stock",
      value: data.low_stock_products || 0,
    },
    {
      title: "Out of Stock",
      value: data.out_of_stock_products || 0,
    },
  ];

  return (
    <div className="inventory-cards">
      {cards.map((card, index) => (
        <div className="inventory-card" key={index}>
          <h3>{card.title}</h3>
          <h2>{card.value}</h2>
        </div>
      ))}
    </div>
  );
}