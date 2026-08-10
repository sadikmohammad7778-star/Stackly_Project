import {
  exportCustomersCSV,
  exportCustomersPDF,
} from "../../api/customerApi";

export default function CustomerExport() {

  const downloadFile = (data, filename) => {
    const blob = new Blob([data]);

    const url = window.URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = filename;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    window.URL.revokeObjectURL(url);
  };

  const handleCSV = async () => {
    try {
      const response = await exportCustomersCSV();

      downloadFile(
        response.data,
        "customers.csv"
      );

      alert("CSV exported successfully.");
    } catch (error) {
      console.error(error);

      alert("Failed to export CSV.");
    }
  };

  const handlePDF = async () => {
    try {
      const response = await exportCustomersPDF();

      downloadFile(
        response.data,
        "customers.pdf"
      );

      alert("PDF exported successfully.");
    } catch (error) {
      console.error(error);

      alert("Failed to export PDF.");
    }
  };

  return (
    <div className="customer-export">

      <button
        type="button"
        onClick={handleCSV}
      >
        Export CSV
      </button>

      <button
        type="button"
        onClick={handlePDF}
      >
        Export PDF
      </button>

    </div>
  );
}