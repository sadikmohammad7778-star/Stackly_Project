import { loginApi, registerApi } from "../api/authApi";

export const loginUser = async (email, password) => {
  try {
    return await loginApi(email, password);
  } catch (error) {
    throw error;
  }
};

export const registerUser = async (userData) => {
  try {
    return await registerApi(userData);
  } catch (error) {
    throw error;
  }
};