import "./EmployeeTable.css";

const employees = [
  {
    id: 1,
    name: "Mohammad Sadik",
    department: "Engineering",
    status: "Active",
  },
  {
    id: 2,
    name: "Rahul Kumar",
    department: "Sales",
    status: "Active",
  },
  {
    id: 3,
    name: "Priya Sharma",
    department: "HR",
    status: "Inactive",
  },
];

export default function EmployeeTable() {
  return (
    <div className="employee-table">

      <table>

        <thead>

          <tr>

            <th>ID</th>
            <th>Name</th>
            <th>Department</th>
            <th>Status</th>

          </tr>

        </thead>

        <tbody>

          {employees.map((emp) => (

            <tr key={emp.id}>

              <td>{emp.id}</td>

              <td>{emp.name}</td>

              <td>{emp.department}</td>

              <td>

                <span
                  className={
                    emp.status === "Active"
                      ? "active"
                      : "inactive"
                  }
                >
                  {emp.status}
                </span>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}