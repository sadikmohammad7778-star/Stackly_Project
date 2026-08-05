import {
  exportCustomersCSV,
  exportCustomersPDF,
} from "../../api/customerApi";

export default function CustomerExport() {

  const downloadFile = (data, filename) => {
    const url = window.URL.createObjectURL(new Blob([data]));

    const link = document.createElement("a");

    link.href = url;
    link.download = filename;

    document.body.appendChild(link);
    link.click();
    link.remove();

    window.URL.revokeObjectURL(url);
  };

  const handleCSV = async () => {
    try {
      const response = await exportCustomersCSV();
      downloadFile(response.data, "customers.csv");
    } catch (error) {
      console.error(error);
    }
  };

  const handlePDF = async () => {
    try {
      const response = await exportCustomersPDF();
      downloadFile(response.data, "customers.pdf");
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="customer-export">
      <button onClick={handleCSV}>
        Export CSV
      </button>

      <button
        onClick={handlePDF}
      >
        Export PDF
      </button>
    </div>
  );
}