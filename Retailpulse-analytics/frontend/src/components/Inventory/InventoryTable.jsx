import "./InventoryTable.css";

export default function InventoryTable({ inventory }) {

    return (

        <div className="inventory-table-container">

            <table className="inventory-table">

                <thead>

                    <tr>

                        <th>Product</th>

                        <th>Brand</th>

                        <th>Current Stock</th>

                        <th>Available Stock</th>

                        <th>Reserved</th>

                        <th>Reorder Level</th>

                        <th>Status</th>

                    </tr>

                </thead>

                <tbody>

                    {

                        inventory.length > 0 ?

                            inventory.map((item) => (

                                <tr key={item.id}>

                                    <td>{item.product.name}</td>

                                    <td>{item.product.brand}</td>

                                    <td>{item.current_stock}</td>

                                    <td>{item.available_stock}</td>

                                    <td>{item.reserved_stock}</td>

                                    <td>{item.reorder_level}</td>

                                    <td>

                                        <span className={`status ${item.stock_status}`}>

                                            {item.stock_status}

                                        </span>

                                    </td>

                                </tr>

                            ))

                            :

                            <tr>

                                <td colSpan="7">

                                    No Inventory Available

                                </td>

                            </tr>

                    }

                </tbody>

            </table>

        </div>

    );

}