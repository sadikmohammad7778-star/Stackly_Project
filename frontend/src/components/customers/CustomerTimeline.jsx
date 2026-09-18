import { useEffect, useState } from "react";
import { customerTimeline } from "../../api/customerApi";

export default function CustomerTimeline({ customerId }) {
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (customerId) {
      loadTimeline();
    }
  }, [customerId]);

  const loadTimeline = async () => {
    try {
      setLoading(true);

      const data = await customerTimeline(customerId);

      console.log("Customer Timeline:", data);

      setTimeline(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error(
        "Error loading timeline:",
        error
      );

      setTimeline([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div>
        <h3>Customer Timeline</h3>
        <p>Loading timeline...</p>
      </div>
    );
  }

  return (
    <div className="customer-timeline">

      <h3>Customer Timeline</h3>

      {timeline.length === 0 ? (
        <p>No timeline available.</p>
      ) : (
        <ul>
          {timeline.map((item) => (
            <li key={item.id}>

              <strong>
                {item.event || "-"}
              </strong>

              <br />

              <span>
                {item.description || "-"}
              </span>

              <br />

              <small>
                {item.created_at
                  ? new Date(
                      item.created_at
                    ).toLocaleString("en-IN")
                  : "-"}
              </small>

              <hr />

            </li>
          ))}
        </ul>
      )}

    </div>
  );
}