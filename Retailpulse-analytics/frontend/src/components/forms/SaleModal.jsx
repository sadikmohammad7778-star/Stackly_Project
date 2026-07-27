import { useEffect, useState } from "react";
import { createSale } from "../../api/salesApi";
import { getCompanies } from "../../api/companyApi";
import { getProducts } from "../../api/productApi";
import { getCategories } from "../../api/categoryApi";
import "./CompanyModal.css";

export default function SaleModal({
  isOpen,
  onClose,
  onSuccess,
}) {

  const [companies, setCompanies] = useState([]);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);

  const [formData, setFormData] = useState({
    company_id: "",
    customer_name: "",
    sales_channel: "Offline",
    payment_method: "Cash",

    items: [
      {
        product_id: "",
        category_id: "",
        quantity: "",
        unit_price: "",
        discount: 0,
        tax: 0,
      },
    ],
  });

  // ==========================
  // Load dropdown data
  // ==========================

  useEffect(() => {
    loadDropdowns();
  }, []);

  const loadDropdowns = async () => {
    try {
      const companyData = await getCompanies();
      const productData = await getProducts();
      const categoryData = await getCategories();

      setCompanies(companyData);
      setProducts(productData);
      setCategories(categoryData);
    } catch (error) {
      console.error(error);
    }
  };

  if (!isOpen) return null;

  // ==========================
  // Main Form Change
  // ==========================

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // ==========================
  // Item Change
  // ==========================

  const handleItemChange = (e) => {
    const { name, value } = e.target;

    const items = [...formData.items];

    items[0][name] = value;

    setFormData({
      ...formData,
      items,
    });
  };

  // ==========================
  // Product Change
  // Auto Fill Category & Price
  // ==========================

  const handleProductChange = (e) => {
    const productId = Number(e.target.value);

    const selected = products.find(
      (product) => product.id === productId
    );

    const items = [...formData.items];

    items[0].product_id = productId;
    items[0].category_id = selected?.category_id || "";
    items[0].unit_price = selected?.unit_price || "";

    setFormData({
      ...formData,
      items,
    });
  };

  // ==========================
  // Submit
  // ==========================

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await createSale({
        company_id: Number(formData.company_id),
        customer_name: formData.customer_name,
        sales_channel: formData.sales_channel,
        payment_method: formData.payment_method,

        items: [
          {
            product_id: Number(formData.items[0].product_id),
            category_id: Number(formData.items[0].category_id),
            quantity: Number(formData.items[0].quantity),
            unit_price: Number(formData.items[0].unit_price),
            discount: Number(formData.items[0].discount),
            tax: Number(formData.items[0].tax),
          },
        ],
      });

      alert("Sale created successfully.");

      onSuccess();
      onClose();

    } catch (err) {
      console.error(err);

      alert(
        err.response?.data?.detail ||
        "Failed to create sale."
      );
    }
  };


  return (
  <div className="modal-overlay">
    <div className="modal">
      <h2>Add Sale</h2>

      <form onSubmit={handleSubmit}>

        {/* Company */}

        <select
          name="company_id"
          value={formData.company_id}
          onChange={handleChange}
          required
        >
          <option value="">Select Company</option>

          {companies.map((company) => (
            <option key={company.id} value={company.id}>
              {company.company_name}
            </option>
          ))}
        </select>

        {/* Customer */}

        <input
          type="text"
          name="customer_name"
          placeholder="Customer Name"
          value={formData.customer_name}
          onChange={handleChange}
          required
        />

        {/* Sales Channel */}

        <select
          name="sales_channel"
          value={formData.sales_channel}
          onChange={handleChange}
        >
          <option value="Offline">Offline</option>
          <option value="Online">Online</option>
        </select>

        {/* Payment */}

        <select
          name="payment_method"
          value={formData.payment_method}
          onChange={handleChange}
        >
          <option value="Cash">Cash</option>
          <option value="Card">Card</option>
          <option value="UPI">UPI</option>
        </select>

        <hr />

        <h3>Sale Item</h3>

        {/* Product */}

        <select
          name="product_id"
          value={formData.items[0].product_id}
          onChange={handleProductChange}
          required
        >
          <option value="">Select Product</option>

          {products.map((product) => (
            <option key={product.id} value={product.id}>
              {product.name}
            </option>
          ))}
        </select>

        {/* Category */}

        <select
          name="category_id"
          value={formData.items[0].category_id}
          onChange={handleItemChange}
          required
        >
          <option value="">Select Category</option>

          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>

        {/* Quantity */}

        <input
          type="number"
          name="quantity"
          placeholder="Quantity"
          value={formData.items[0].quantity}
          onChange={handleItemChange}
          required
        />

        {/* Unit Price */}

        <input
          type="number"
          name="unit_price"
          placeholder="Unit Price"
          value={formData.items[0].unit_price}
          readOnly
        />

        {/* Discount */}

        <input
          type="number"
          name="discount"
          placeholder="Discount"
          value={formData.items[0].discount}
          onChange={handleItemChange}
        />

        {/* Tax */}

        <input
          type="number"
          name="tax"
          placeholder="Tax"
          value={formData.items[0].tax}
          onChange={handleItemChange}
        />

        <div className="modal-buttons">
          <button
            type="button"
            onClick={onClose}
          >
            Cancel
          </button>

          <button type="submit">
            Save Sale
          </button>
        </div>

      </form>
    </div>
  </div>
);
}