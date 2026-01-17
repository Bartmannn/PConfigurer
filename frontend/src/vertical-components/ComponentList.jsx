import { useEffect, useState, useMemo } from "react";
import { generateRemarksForComponent } from "../services/remarksService";

const itemsCache = new Map();

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

const getPriceValue = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : Number.POSITIVE_INFINITY;
};

const getCompatibilityScore = (remarks) => {
  const entries = Object.values(remarks || {});
  if (entries.length === 0) return 1;

  let hasOk = false;
  let hasBad = false;

  entries.forEach((remark) => {
    if (!remark) return;
    if (remark.score === "bad") {
      hasBad = true;
      return;
    }
    if (remark.score === "ok") {
      hasOk = true;
      return;
    }
    if (!remark.score && typeof remark.text === "string") {
      const text = remark.text.toLowerCase();
      if (text.includes("brak danych") || text.includes("nie podaje")) {
        hasBad = true;
      }
    }
  });

  if (hasBad) return -1;
  if (hasOk) return 0;
  return 1;
};

function ComponentList({ category, selected, filters, onPreview, onSelect, selectedItem }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const keepIncompatible = filters?.general?.keep_incompatible === true;
  const buildSnapshot = useMemo(
    () => ({
      ...selected,
      motherboard: selected?.mobo,
      case: selected?.chassis,
      storage: selected?.mem,
    }),
    [selected]
  );

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
    const relevantParams = keepIncompatible ? [] : map[category].params.map(p => selected[p]);
    return [category, filterSignature, keepIncompatible, ...relevantParams];
  }, [category, selected, filterSignature, keepIncompatible]);

  useEffect(() => {
    if (!category) return;

    const cacheKey = `${category}|${filterSignature}`;
    if (keepIncompatible && itemsCache.has(cacheKey)) {
      const cached = itemsCache.get(cacheKey) || [];
      const scored = cached.map((item, index) => {
        const remarks = generateRemarksForComponent(item, category, buildSnapshot);
        return {
          ...item,
          _compatScore: getCompatibilityScore(remarks),
          _index: index,
        };
      });
      scored.sort((a, b) => {
        if (b._compatScore !== a._compatScore) return b._compatScore - a._compatScore;
        const priceDiff = getPriceValue(a.price) - getPriceValue(b.price);
        if (priceDiff !== 0) return priceDiff;
        return a._index - b._index;
      });
      setItems(scored);
      setLoading(false);
      return;
    }

    setLoading(true);
    const baseUrl = "http://localhost:8000/api/";
    const conf = map[category];

    if (!conf) return;

    let url = baseUrl + conf.endpoint;
    const query = keepIncompatible
      ? ""
      : conf.params
          .filter((p) => selected[p]?.id)               // p -> typ podzeposłu (np. CPU), bierzemy pod uwagę niepuste wartości
          .map((p) => `${p}=${selected[p].id}`)         // selected[p].id -> dopisywanie id wybranych wcześniej podzespołów
          .join("&");
    const filterQuery = buildFilterQuery(filters?.[category]);
    const combinedQuery = [query, filterQuery].filter(Boolean).join("&");
    if (combinedQuery) url += "?" + combinedQuery;

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        const list = Array.isArray(data) ? data : [];
        if (keepIncompatible) {
          itemsCache.set(cacheKey, list);
        }
        const scored = list.map((item, index) => {
          const remarks = generateRemarksForComponent(item, category, buildSnapshot);
          return {
            ...item,
            _compatScore: getCompatibilityScore(remarks),
            _index: index,
          };
        });
        scored.sort((a, b) => {
          if (b._compatScore !== a._compatScore) return b._compatScore - a._compatScore;
          const priceDiff = getPriceValue(a.price) - getPriceValue(b.price);
          if (priceDiff !== 0) return priceDiff;
          return a._index - b._index;
        });
        setItems(scored);
      })
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

      <div className="compat-legend">
        <span className="compat-legend-item">
          <span className="compat-icon compat-good">^</span>
          <span>Dopasowane</span>
        </span>
        <span className="compat-legend-item">
          <span className="compat-icon compat-ok">-</span>
          <span>Ograniczaja</span>
        </span>
        <span className="compat-legend-item">
          <span className="compat-icon compat-bad">x</span>
          <span>Niepasujace</span>
        </span>
      </div>

      <ul className="component-list">
        {items.map((item) => {
          const compatScore = item._compatScore ?? 1;
          const compatLabel =
            compatScore === 1 ? "good" : compatScore === 0 ? "ok" : "bad";
          const isSelected = selectedItem?.id === item.id;
          const className = [
            "component-item",
            `compat-${compatLabel}`,
            isSelected ? "selected" : "",
          ]
            .filter(Boolean)
            .join(" ");

          const compatIcon = compatLabel === "good" ? "^" : compatLabel === "ok" ? "-" : "x";

          return (
          <li
            key={item.id}
            onClick={() => onPreview(item)}
            className={className}
          >
            <span className={`compat-icon compat-${compatLabel}`}>{compatIcon}</span>
            <span>{item.short_name}</span>
          </li>
          );
        })}
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
