import API from "./api";

export const getProducts = () => API.get("/products");

export const createProduct = (data) =>
  API.post("/products", data);

export const updateProduct = (id, data) =>
  API.put(`/products/${id}`, data);

export const deleteProduct = (id) =>
  API.delete(`/products/${id}`);

export const searchProduct = (keyword) =>
  API.get(`/products/search/${keyword}`);

export const filterProducts = (params) =>
  API.get("/products/filter", { params });

export const sortProducts = (sortBy) =>
  API.get(`/products/sort/${sortBy}`);

export const changeProductStatus = (id, status) =>
  API.patch(`/products/${id}/status`, null, {
    params: { status },
  });

