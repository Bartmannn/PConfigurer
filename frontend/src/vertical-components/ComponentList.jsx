import { useEffect, useState, useMemo } from "react";

function buildFilterQuery(filters) {
  if (!filters) return "";
  const parts = [];

  Object.entries(filters).forEach(([key, value]) => {
    if (value === null || value === undefined) return;
    if (typeof value === "string" && value.trim() === "") return;
    if (Array.isArray(value)) {
      if (value.length === 0) return;
      if (key === "integrated_gpu") {
        if (value.length !== 1) return;
        parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value[0]))}`);
        return;
      }
      parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value.join(","))}`);
      return;
    }
    if (typeof value === "object" && value !== null) {
      const min = value.min;
      const max = value.max;
      if (min !== "" && min !== null && min !== undefined) {
        parts.push(`${encodeURIComponent(key)}_min=${encodeURIComponent(min)}`);
      }
      if (max !== "" && max !== null && max !== undefined) {
        parts.push(`${encodeURIComponent(key)}_max=${encodeURIComponent(max)}`);
      }
      return;
    }
    parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
  });

  return parts.join("&");
}

function ComponentList({ category, selected, filters, onPreview, onSelect, selectedItem }) {
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
  const filterSignature = useMemo(() => {
    if (!category || !filters) return "";
    return JSON.stringify(filters[category] || {});
  }, [category, filters]);

  const dependencies = useMemo(() => {
    if (!category || !map[category]) return [category];
    const relevantParams = map[category].params.map(p => selected[p]);
    return [category, filterSignature, ...relevantParams];
  }, [category, selected, filterSignature]);

  useEffect(() => {
    if (!category) return;

    setLoading(true);
    const baseUrl = "http://localhost:8000/api/";
    const conf = map[category];

    if (!conf) return;

    let url = baseUrl + conf.endpoint;
    const query = conf.params
      .filter((p) => selected[p]?.id)               // p -> typ podzeposłu (np. CPU), bierzemy pod uwagę niepuste wartości
      .map((p) => `${p}=${selected[p].id}`)         // selected[p].id -> dopisywanie id wybranych wcześniej podzespołów
      .join("&");
    const filterQuery = buildFilterQuery(filters?.[category]);
    const combinedQuery = [query, filterQuery].filter(Boolean).join("&");
    if (combinedQuery) url += "?" + combinedQuery;

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
