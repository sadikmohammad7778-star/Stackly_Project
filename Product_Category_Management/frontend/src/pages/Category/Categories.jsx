import CategoryTable from "../../components/Category/CategoryTable";

function Categories() {
  const loadCategories = async () => {
    try {
      const response = await getCategories();

      console.log("Response:", response);
      console.log("Data:", response.data);

      setCategories(response.data);
    } catch (error) {
      console.error(error);
    }
  };
  return (
    <div>

      <h1 style={{ marginBottom: "20px" }}>
        Category Management
      </h1>

      <CategoryTable />

    </div>
  );
}

export default Categories;