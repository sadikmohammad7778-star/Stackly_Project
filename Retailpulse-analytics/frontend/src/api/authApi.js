import API from "./axios";

export const loginApi = async (email, password) => {
  const response = await API.post("/auth/login", {
    email,
    password,
  });

  return response.data;
};

export const registerApi = async (userData) => {
  const response = await API.post("/auth/register", userData);
  return response.data;
};