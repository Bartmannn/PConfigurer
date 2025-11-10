import { useEffect, useState, useMemo } from "react";

function ComponentList({ category, selected, onPreview, onSelect, selectedItem }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  const map = {
    cpu: { endpoint: "cpus/", params: ["mobo", "ram", "gpu", "psu"] },
    gpu: { endpoint: "gpus/", params: ["psu", "cpu", "mobo", "chassis"] },
    ram: { endpoint: "rams/", params: ["mobo", "cpu"] },
    mobo: { endpoint: "motherboards/", params: ["cpu", "ram", "gpu", "psu", "mem", "chassis"] },
    psu: { endpoint: "psus/", params: ["gpu", "cpu", "mobo", "chassis"] },
    mem: { endpoint: "mems/", params: ["mobo"] },
    chassis: { endpoint: "cases/", params: ["mobo", "gpu", "psu"] },
  };

  // Stwórz listę zależności, aby uniknąć niepotrzebnego odświeżania
  const dependencies = useMemo(() => {
    if (!category || !map[category]) return [category];
    const relevantParams = map[category].params.map(p => selected[p]);
    return [category, ...relevantParams];
  }, [category, selected]);

  useEffect(() => {
    if (!category) return;

    setLoading(true);
    const baseUrl = "http://localhost:8000/api/";

    const conf = map[category];
    if (!conf) return;

    let url = baseUrl + conf.endpoint;
    const query = conf.params
      .filter((p) => selected[p]?.id)
      .map((p) => `${p}=${selected[p].id}`)
      .join("&");

    if (query) url += "?" + query;

    fetch(url)
      .then((res) => res.json())
      .then((data) => setItems(data))
      .catch((err) => console.error("Błąd pobierania:", err))
      .finally(() => setLoading(false));
  }, dependencies);

  if (loading) return <p>Ładowanie danych...</p>;

  return (
    <div className="component-list-container">
      {/* Brak zawsze na górze */}
      <div
        className="component-none"
        onClick={() => onSelect(null)}
        style={{
          background: selectedItem === null ? "#4f5f4f" : "#3a3a3a",
        }}
      >
        ❌ Brak
      </div>

      <ul className="component-list">
        {items.map((item) => (
          <li
            key={item.id}
            onClick={() => onPreview(item)}
            style={{
              background:
                selectedItem?.id === item.id ? "#4f5f4f" : "#2b2b2b",
            }}
          >
            {item.short_name}
          </li>
        ))}
        {items.length === 0 && !loading && (
          <li key="no-results">
            <p>Brak wyników.</p>
          </li>
        )}
      </ul>
    </div>
  );
}

export default ComponentList;
