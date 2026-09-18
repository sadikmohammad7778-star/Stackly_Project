import API from "./axios";

export const getCategories = async () => {
  const response = await API.get("/categories/");
  return response.data;
};

export const createCategory = async (category) => {
  const response = await API.post("/categories/", category);
  return response.data;
};

export const updateCategory = async (id, category) => {
  const response = await API.put(`/categories/${id}`, category);
  return response.data;
};

export const deleteCategory = async (id) => {
  const response = await API.delete(`/categories/${id}`);
  return response.data;
};