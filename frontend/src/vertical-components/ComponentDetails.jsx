import { useEffect, useState } from "react";
import "./details.css";

// Polskie etykiety
const FIELD_LABELS = {
  cpu: {
    name: "Model",
    manufacturer_name: "Producent",
    socket: "Gniazdo",
    cores: "Rdzenie",
    threads: "Wątki",
    base_clock_ghz: "Taktowanie bazowe (GHz)",
    boost_clock_ghz: "Taktowanie boost (GHz)",
    tdp: "TDP [W]",
    supported_ram: "Obsługiwana pamięć RAM",
  },
  gpu: {
    name: "Model",
    manufacturer_name: "Producent",
    vram_type: "Typ VRAM",
    vram_capacity: "Pamięć VRAM [GB]",
    length_mm: "Długość [mm]",
    width_mm: "Szerokość [mm]",
    height_mm: "Wysokość [mm]",
    tdp: "TDP [W]",
    connectors: "Złącza",
  },
  ram: {
    name: "Model",
    manufacturer_name: "Producent",
    base: "Standard RAM",
    modules_count: "Liczba modułów",
    module_memory: "Pojemność modułu [GB]",
    total_capacity: "Całkowita pojemność [GB]",
  },
  mobo: {
    name: "Model",
    manufacturer_name: "Producent",
    socket: "Gniazdo procesora",
    form_factor: "Format płyty",
    supported_ram: "Obsługiwana pamięć RAM",
    max_ram_capacity: "Maksymalna pamięć RAM [GB]",
    dimm_slots: "Liczba slotów DIMM",
    connectors: "Złącza",
  },
  psu: {
    name: "Model",
    manufacturer_name: "Producent",
    wattage: "Moc maksymalna [W]",
    form_factor: "Format zasilacza",
    connectors: "Złącza",
  },
  mem: {
    name: "Model",
    manufacturer_name: "Producent",
    connector: "Złącze",
    capacity_gb: "Pojemność [GB]",
    type: "Typ dysku",
  },
  chassis: {
    name: "Model",
    manufacturer_name: "Producent",
    mobo_form_factor_support: "Obsługiwane formaty płyt",
    psu_form_factor_support: "Obsługiwane formaty zasilaczy",
    max_gpu_length_mm: "Maks. długość GPU [mm]",
  },
};

// mapy endpointów
const FK_ENDPOINTS = {
  form_factor: "psuformfactors",
  socket: "sockets",
  connector: "connectors",
  base: "rambases",
};

const M2M_ENDPOINTS = {
  supported_ram: "rambases",
  mobo_form_factor_support: "motherboardformfactors",
  psu_form_factor_support: "psuformfactors",
};

// prosty cache
const cache = {};

function ComponentDetails({ category, selectedItem }) {
  const [details, setDetails] = useState(null);
  const [resolved, setResolved] = useState(null);

  useEffect(() => {
    if (!category || !selectedItem?.id) {
      setDetails(null);
      setResolved(null);
      return;
    }

    const endpoints = {
      cpu: "cpus",
      gpu: "gpus",
      ram: "rams",
      mobo: "motherboards",
      psu: "psus",
      mem: "mems",
      chassis: "cases",
    };

    const endpoint = endpoints[category];
    if (!endpoint) return;

    const fetchData = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/${endpoint}/${selectedItem.id}/`);
        const data = await res.json();
        setDetails(data);

        const resolvedData = { ...data };

        // --- obsługa ForeignKey ---
        const fkPromises = Object.entries(data)
          .filter(([key, val]) => FK_ENDPOINTS[key] && typeof val === "number")
          .map(async ([key, id]) => {
            const cacheKey = `${FK_ENDPOINTS[key]}_${id}`;
            if (cache[cacheKey]) return [key, cache[cacheKey]];
            const r = await fetch(`http://localhost:8000/api/${FK_ENDPOINTS[key]}/${id}/`);
            const json = await r.json();
            const name = json.name || json.type || json.category || id;
            cache[cacheKey] = name;
            return [key, name];
          });

        // --- obsługa ManyToMany ---
        const m2mPromises = Object.entries(data)
          .filter(([key, val]) => M2M_ENDPOINTS[key] && Array.isArray(val) && val.length)
          .map(async ([key, ids]) => {
            const endpoint = M2M_ENDPOINTS[key];
            const query = `id__in=${ids.join(",")}`;
            const r = await fetch(`http://localhost:8000/api/${endpoint}/?${query}`);
            const json = await r.json();
            const names = [...new Set(json.map((obj) => {
            if (obj.type && obj.mts) return `${obj.type}-${obj.mts}`;
            return obj.name || obj.type || obj.category || "";
            }))].join(", ");
            return [key, names];
          });

        // --- scalanie ---
        const allResolved = await Promise.all([...fkPromises, ...m2mPromises]);
        for (const [key, val] of allResolved) {
          resolvedData[key] = val;
        }

        setResolved(resolvedData);
      } catch (err) {
        console.error("Błąd pobierania szczegółów:", err);
      }
    };

    fetchData();
  }, [category, selectedItem]);

  if (!resolved)
    return <div className="component-details">Ładowanie danych...</div>;

  const labels = FIELD_LABELS[category] || {};
  const visible = Object.entries(resolved).filter(([k]) => labels[k]);

  return (
    <div className="component-details">
      <h3 className="details-title">{resolved.name || resolved.model}</h3>
      <table className="details-table">
        <thead>
          <tr>
            <th>Parametr</th>
            <th>Wartość</th>
            <th>Uwagi</th>
          </tr>
        </thead>
        <tbody>
          {visible.map(([key, value]) => (
            <tr key={key}>
              <td className="param">{labels[key]}</td>
              <td className="value">
                {Array.isArray(value)
                    ? value
                        .map(
                        (v) =>
                            v.connector
                            ? `${v.connector.category} ${v.connector.version || ""}`.trim()
                            : v.name || v.type || ""
                        )
                        .join(", ")
                    : String(value)}
              </td>
              <td className="note">—</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ComponentDetails;


//TODO:
    // PSU - wartość "Obslugiwane formaty zasilaczy" -> "format zasialcza", "Obsługiwane formaty płyt"
    // Nie podoba mi się złącze w Dyskach
    // 