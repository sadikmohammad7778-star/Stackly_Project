import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { getDashboard, getInventory } from "../api/inventoryApi";

import InventoryCards from "../components/Inventory/InventoryCards";
import InventoryTable from "../components/Inventory/InventoryTable";
import SearchFilter from "../components/Inventory/SerachFilter";
import InventoryCharts from "../components/Inventory/InventoryCharts";
import StockModal from "../components/Inventory/StockModal";

import "./Inventory.css";

export default function Inventory() {
    const [searchParams] = useSearchParams();
    const inventoryId = searchParams.get("inventory_id");

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
    const [highlightedInventoryId, setHighlightedInventoryId] = useState(null);

    useEffect(() => {
        loadDashboard();
        loadInventory();
    }, [inventoryId]);

    const loadDashboard = async () => {
        try {
            const data = await getDashboard();
            setDashboard(data);
        } catch (error) {
            console.error("Error loading inventory dashboard:", error);
        }
    };

    const loadInventory = async () => {
        try {
            const data = await getInventory(search, status);
            const inventoryData = Array.isArray(data) ? data : [];

            setInventory(inventoryData);

            if (inventoryId) {
                const targetInventory = inventoryData.find(
                    (item) => item.id === Number(inventoryId)
                );

                if (targetInventory) {
                    setHighlightedInventoryId(targetInventory.id);

                    setTimeout(() => {
                        const element = document.getElementById(
                            `inventory-row-${targetInventory.id}`
                        );

                        if (element) {
                            element.scrollIntoView({
                                behavior: "smooth",
                                block: "center",
                            });
                        }
                    }, 200);
                }
            }
        } catch (error) {
            console.error("Error loading inventory:", error);
            setInventory([]);
        }
    };

    return (
        <div className="inventory-page">
            <div className="page-header">
                <h1>Inventory Management</h1>

                <p>
                    Manage stock levels and inventory.
                </p>
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

            <InventoryTable
                inventory={inventory}
                highlightedInventoryId={highlightedInventoryId}
            />

            <StockModal
                isOpen={openModal}
                onClose={() => setOpenModal(false)}
                onSuccess={loadInventory}
                inventory={inventory}
            />
        </div>
    );
}