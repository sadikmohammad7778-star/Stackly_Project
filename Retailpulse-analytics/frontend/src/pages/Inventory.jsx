import { useEffect, useState } from "react";

import { getDashboard, getInventory } from "../api/inventoryApi";

import InventoryCards from "../components/Inventory/InventoryCards";
import InventoryTable from "../components/Inventory/InventoryTable";
import SearchFilter from "../components/Inventory/SerachFilter";
import InventoryCharts from "../components/Inventory/InventoryCharts";
import StockModal from "../components/Inventory/StockModal";

import "./Inventory.css";

export default function Inventory() {

    const [dashboard, setDashboard] = useState({
        total_products: 0,
        total_inventory_quantity: 0,
        low_stock_products: 0,
        out_of_stock_products: 0,
    });

    const [inventory, setInventory] = useState([]);

    const [search, setSearch] = useState("");

    const [status, setStatus] = useState("");

    const [openModal, setOpenModal] = useState(false);

    useEffect(() => {

        loadDashboard();
        loadInventory();

    }, []);

    const loadDashboard = async () => {

        try {

            const data = await getDashboard();

            setDashboard(data);

        }

        catch (error) {

            console.error(error);

        }

    };

    const loadInventory = async () => {

        try {

            // Temporary Company ID

            const data = await getInventory(3, search, status);

            console.log(data);

            setInventory(data);

        }

        catch (error) {

            console.error(error);

        }

    };

    return (

        <div className="inventory-page">

            <div className="page-header">

                <h1>Inventory Management</h1>

                <p>Manage stock levels and inventory.</p>

            </div>

            <InventoryCards data={dashboard} />

            <InventoryCharts />

            <div
                style={{
                    display: "flex",
                    justifyContent: "flex-end",
                    margin: "20px 0",
                }}
            >

                <button

                    onClick={() => setOpenModal(true)}

                    style={{

                        background: "#2563eb",

                        color: "#fff",

                        border: "none",

                        padding: "10px 18px",

                        borderRadius: "6px",

                        cursor: "pointer",

                    }}

                >

                    Manage Stock

                </button>

            </div>

            <SearchFilter

                search={search}

                setSearch={setSearch}

                status={status}

                setStatus={setStatus}

                onSearch={loadInventory}

            />

            <InventoryTable inventory={inventory} />

            <StockModal

                isOpen={openModal}

                onClose={() => setOpenModal(false)}

                onSuccess={loadInventory}

            />

        </div>

    );

}