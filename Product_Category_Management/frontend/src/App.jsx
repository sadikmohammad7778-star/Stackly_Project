import AppRoutes from "./routes/AppRoutes";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./index.css"

function App() {
  return (
    <>
      <AppRoutes />
      <ToastContainer position="top-right" />
    </>
  );
}

export default App;