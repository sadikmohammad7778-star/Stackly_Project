import { useEffect, useState } from "react";
import { customerTimeline } from "../../api/customerApi";

export default function CustomerTimeline({ customerId }) {
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadTimeline = async () => {
    try {
      const response = await customerTimeline(customerId);
      setTimeline(response.data);
    } catch (error) {
      console.error("Error loading timeline:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (customerId) {
      loadTimeline();
    }
  }, [customerId]);

  if (loading) {
    return <p>Loading timeline...</p>;
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
              <strong>{item.event}</strong>

              <br />

              <span>{item.description}</span>

              <br />

              <small>
                {new Date(item.created_at).toLocaleString()}
              </small>

              <hr />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}