import {
  FiDownload,
  FiFileText,
  FiFile,
} from "react-icons/fi";

import "./Reports.css";

const reports = [
  {
    id: 1,
    name: "Employee Report",
    type: "PDF",
    date: "15 Jul 2026",
  },
  {
    id: 2,
    name: "Attendance Report",
    type: "Excel",
    date: "15 Jul 2026",
  },
  {
    id: 3,
    name: "Company Report",
    type: "PDF",
    date: "15 Jul 2026",
  },
];

export default function Reports() {

  return (

    <div className="reports-page">

      <div className="reports-header">

        <h2>Reports</h2>

      </div>

      <div className="reports-card">

        <table>

          <thead>

            <tr>

              <th>Report</th>

              <th>Format</th>

              <th>Generated On</th>

              <th>Download</th>

            </tr>

          </thead>

          <tbody>

            {

              reports.map((report) => (

                <tr key={report.id}>

                  <td>

                    <div className="report-name">

                      <FiFileText />

                      {report.name}

                    </div>

                  </td>

                  <td>{report.type}</td>

                  <td>{report.date}</td>

                  <td>

                    <button className="download-btn">

                      <FiDownload />

                      Download

                    </button>

                  </td>

                </tr>

              ))

            }

          </tbody>

        </table>

      </div>

    </div>

  );

}