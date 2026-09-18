import API from "./axios";

export const getProducts = async () => {
  const response = await API.get("/products/");
  return response.data;
};

export const createProduct = async (product) => {
  const response = await API.post("/products/", product);
  return response.data;
};

export const updateProduct = async (id, product) => {
  const response = await API.put(`/products/${id}`, product);
  return response.data;
};

export const deleteProduct = async (id) => {
  const response = await API.delete(`/products/${id}`);
  return response.data;
};

export const searchProducts = async (keyword) => {
  const response = await API.get(`/products/search/${keyword}`);
  return response.data;
};