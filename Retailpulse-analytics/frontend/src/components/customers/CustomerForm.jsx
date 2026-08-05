import { useState, useEffect } from "react";
import { Country, State, City } from "country-state-city";
import {
  createCustomer,
  updateCustomer, 
} from "../../api/customerApi";

export default function CustomerForm({
  reload,
  selectedCustomer,
  setSelectedCustomer,
}) {

  const emptyForm = {
    full_name: "",
    email: "",
    phone: "",
    gender: "",
    date_of_birth: "",
    address: "",
    city: "",
    state: "",
    country: "",
    customer_type: "Retail",
    preferred_sales_channel: "Store",
  };

  const [formData, setFormData] = useState(emptyForm);

  // Country-State-City
  const countries = Country.getAllCountries();
  const [states, setStates] = useState([]);
  const [cities, setCities] = useState([]);

  useEffect(() => {
    if (selectedCustomer) {
      setFormData({
        full_name: selectedCustomer.full_name || "",
        email: selectedCustomer.email || "",
        phone: selectedCustomer.phone || "",
        gender: selectedCustomer.gender || "",
        date_of_birth: selectedCustomer.date_of_birth || "",
        address: selectedCustomer.address || "",
        city: selectedCustomer.city || "",
        state: selectedCustomer.state || "",
        country: selectedCustomer.country || "",
        customer_type: selectedCustomer.customer_type || "Retail",
        preferred_sales_channel:
          selectedCustomer.preferred_sales_channel || "Store",
      });
    } else {
      setFormData(emptyForm);
    }
  }, [selectedCustomer]);

  // Load States when Country changes

useEffect(() => {
  if (!formData.country) {
    setStates([]);
    setCities([]);
    return;
  }

  const selectedCountry = countries.find(
    (country) => country.name === formData.country
  );

  if (selectedCountry) {
    setStates(
      State.getStatesOfCountry(selectedCountry.isoCode)
    );
  }
}, [formData.country]);
  // Load Cities when State changes
  useEffect(() => {
  if (!formData.country || !formData.state) {
    setCities([]);
    return;
  }

  const selectedCountry = countries.find(
    (country) => country.name === formData.country
  );

  const selectedState = states.find(
    (state) => state.name === formData.state
  );

  if (selectedCountry && selectedState) {
    setCities(
      City.getCitiesOfState(
        selectedCountry.isoCode,
        selectedState.isoCode
      )
    );
  }
}, [formData.country, formData.state, states]);

 const handleChange = (e) => {
  const { name, value } = e.target;

  if (name === "country") {
    setFormData((prev) => ({
      ...prev,
      country: value,
      state: "",
      city: "",
    }));
  } else if (name === "state") {
    setFormData((prev) => ({
      ...prev,
      state: value,
      city: "",
    }));
  } else {
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  }
};

  const handleSubmit = async (e) => {
  e.preventDefault();

    try {
      if (selectedCustomer) {
        await updateCustomer(selectedCustomer.id, formData);
        alert("Customer updated successfully.");
      } else {
        await createCustomer(formData);
        alert("Customer created successfully.");
      }

      // Reload customer list
      await reload();

      // Reset form
      setFormData({ ...emptyForm });
      setStates([]);
      setCities([]);
      setSelectedCustomer(null);

    } catch (error) {
      alert(
        error.response?.data?.detail ||
        "Something went wrong."
      );
    }
  };
  return (
    <form className="customer-form" onSubmit={handleSubmit}>
      <input
        type="text"
        name="full_name"
        placeholder="Full Name"
        value={formData.full_name}
        onChange={handleChange}
        required
      />

      <input
        type="email"
        name="email"
        placeholder="Email"
        value={formData.email}
        onChange={handleChange}
        required
      />

      <input
        type="text"
        name="phone"
        placeholder="Phone Number"
        value={formData.phone}
        onChange={handleChange}
        required
      />

      <select
        name="gender"
        value={formData.gender}
        onChange={handleChange}
      >
        <option value="">Select Gender</option>
        <option value="Male">Male</option>
        <option value="Female">Female</option>
        <option value="Other">Other</option>
      </select>

      <input
        type="date"
        name="date_of_birth"
        value={formData.date_of_birth}
        onChange={handleChange}
      />

      <input
        type="text"
        name="address"
        placeholder="Address"
        value={formData.address}
        onChange={handleChange}
      />

            {/* Country */}

      <select
        name="country"
        value={formData.country}
        onChange={handleChange}
        required
      >
        <option value="">Select Country</option>

        {countries.map((country) => (
          <option
            key={country.isoCode}
            value={country.name}
          >
            {country.name}
          </option>
        ))}
      </select>

      {/* State */}

      <select
        name="state"
        value={formData.state}
        onChange={handleChange}
        required
        disabled={!formData.country}
      >
        <option value="">Select State</option>

        {states.map((state) => (
          <option
            key={state.isoCode}
            value={state.name}
          >
            {state.name}
          </option>
        ))}
      </select>

      {/* City */}

      <select
        name="city"
        value={formData.city}
        onChange={handleChange}
        required
        disabled={!formData.state}
      >
        <option value="">Select City</option>

        {cities.map((city) => (
          <option
            key={city.name}
            value={city.name}
          >
            {city.name}
          </option>
        ))}
      </select>

      <select
        name="customer_type"
        value={formData.customer_type}
        onChange={handleChange}
      >
        <option value="Retail">Retail</option>
        <option value="Wholesale">Wholesale</option>
        <option value="Corporate">Corporate</option>
      </select>

      <select
        name="preferred_sales_channel"
        value={formData.preferred_sales_channel}
        onChange={handleChange}
      >
        <option value="Store">Store</option>
        <option value="Online">Online</option>
      </select>

      <button type="submit">
        {selectedCustomer ? "Update Customer" : "Save Customer"}
      </button>

      {selectedCustomer && (
        <button
         onClick={() => {
          setFormData({ ...emptyForm });
          setStates([]);
          setCities([]);
          setSelectedCustomer(null);
        }}
        >
          Cancel
        </button>
      )}

    </form>
  );
}