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
    first_name: "",
    last_name: "",

    email: "",
    phone: "",

    address: "",

    country: "",
    state: "",
    city: "",

    postal_code: "",

    segment: "New",

    status: "Active",
  };

  const [formData, setFormData] = useState(emptyForm);
  // Country-State-City
  const countries = Country.getAllCountries();
  const [states, setStates] = useState([]);
  const [cities, setCities] = useState([]);

  useEffect(() => {
  if (selectedCustomer) {
    setFormData({
      first_name: selectedCustomer.first_name || "",
      last_name: selectedCustomer.last_name || "",
      email: selectedCustomer.email || "",
      phone: selectedCustomer.phone || "",
      address: selectedCustomer.address || "",
      city: selectedCustomer.city || "",
      state: selectedCustomer.state || "",
      country: selectedCustomer.country || "",
      postal_code: selectedCustomer.postal_code || "",
      segment: selectedCustomer.segment || "New",
      status: selectedCustomer.status || "Active",
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

    await reload();

    setFormData(emptyForm);
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
      name="first_name"
      placeholder="First Name"
      value={formData.first_name}
      onChange={handleChange}
      required
    />

    <input
      type="text"
      name="last_name"
      placeholder="Last Name"
      value={formData.last_name}
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

    <input
      type="text"
      name="address"
      placeholder="Address"
      value={formData.address}
      onChange={handleChange}
      required
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
            <input
              type="text"
              name="postal_code"
              placeholder="Postal Code"
              value={formData.postal_code}
              onChange={handleChange}
              required
            />

      <select
        name="segment"
        value={formData.segment}
        onChange={handleChange}
      >
        <option value="New">New</option>
        <option value="Regular">Regular</option>
        <option value="Loyal">Loyal</option>
        <option value="VIP">VIP</option>
      </select>

      <select
        name="status"
        value={formData.status}
        onChange={handleChange}
      >
        <option value="Active">Active</option>
        <option value="Inactive">Inactive</option>
      </select>

      <button type="submit">
        {selectedCustomer ? "Update Customer" : "Save Customer"}
      </button>

      {selectedCustomer && (
        <button
          type="button"
          onClick={() => {
            setFormData(emptyForm);
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