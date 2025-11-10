import { useEffect, useState, useContext } from "react";
import "./details.css";
import { ConfiguratorContext } from "../context/ConfiguratorContext";
import { generateRemarksForComponent } from "../services/remarksService";

// Polskie etykiety dla nowych, spłaszczonych pól
const FIELD_LABELS = {
  cpu: {
    name: "Model",
    manufacturer_name: "Producent",
    socket_name: "Gniazdo",
    cores_info: "Rdzenie",
    threads_info: "Wątki",
    clock_speed_info: "Taktowanie",
    cache_info: "Pamięć cache",
    integrated_graphics: "Zintegrowana grafika",
    ram_support_info: "Wspierana pamięć RAM",
    tdp: "TDP [W]",
    price: "Cena [zł]",
    tier_score: "Ocena wydajności",
  },
  gpu: {
    name: "Model",
    manufacturer_name: "Producent",
    chip_name: "Chip graficzny",
    chip_manufacturer_name: "Producent chipu",
    vram_info: "Pamięć VRAM",
    clock_speed_info: "Taktowanie rdzenia",
    bus_width_info: "Szyna pamięci",
    dimensions_info: "Wymiary",
    ports_info: "Złącza wideo",
    price: "Cena [zł]",
    tier_score: "Ocena wydajności",
  },
  ram: {
    name: "Model",
    manufacturer_name: "Producent",
    kit_info: "Zestaw",
    capacity_info: "Pojemność",
    type_info: "Typ",
    latency_info: "Opóźnienie",
    price: "Cena [zł]",
  },
  mobo: {
    name: "Model",
    manufacturer_name: "Producent",
    socket_name: "Gniazdo procesora",
    form_factor_name: "Format",
    dimm_slots_count: "Sloty RAM",
    supported_ram_types: "Wspierane typy RAM",
    max_ram_capacity_info: "Maks. pojemność RAM",
    pcie_slots_info: "Sloty PCIe",
    m2_slots_info: "Sloty M.2",
    sata_ports_info: "Porty SATA",
    price: "Cena [zł]",
  },
  psu: {
    name: "Model",
    manufacturer_name: "Producent",
    wattage_info: "Moc",
    form_factor_name: "Format",
    connectors_info: "Złącza",
    price: "Cena [zł]",
  },
  mem: { // 'mem' is used for storage
    name: "Model",
    manufacturer_name: "Producent",
    type_info: "Typ dysku",
    capacity_info: "Pojemność",
    interface_info: "Interfejs",
    price: "Cena [zł]",
  },
  chassis: { // 'chassis' is used for case
    name: "Model",
    manufacturer_name: "Producent",
    mobo_support_info: "Wspierane formaty płyt",
    max_gpu_length_info: "Maks. długość GPU",
    price: "Cena [zł]",
  },
};

function ComponentDetails({ category, selectedItem, onSelect, onBack }) {
  const [details, setDetails] = useState(null);
  const [remarks, setRemarks] = useState({});
  const { currentBuild } = useContext(ConfiguratorContext);

  const handleSelect = () => {
    if (details) {
      onSelect(details);
      onBack(); // Wróć do podsumowania
    }
  };

  useEffect(() => {
    if (!category || !selectedItem?.id) {
      setDetails(null);
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
        // Fetch data from the detail endpoint, which now returns flattened data
        const res = await fetch(`http://localhost:8000/api/${endpoint}/${selectedItem.id}/`);
        const data = await res.json();
        setDetails(data);

        // Generate remarks based on the new flattened data
        const generatedRemarks = generateRemarksForComponent(data, category, currentBuild);
        setRemarks(generatedRemarks);
      } catch (err) {
        console.error("Błąd pobierania szczegółów:", err);
      }
    };

    fetchData();
  }, [category, selectedItem, currentBuild]);

  if (!details)
    return <div className="component-details">Ładowanie danych...</div>;

  const labels = FIELD_LABELS[category] || {};
  const visible = Object.entries(details).filter(([k]) => labels[k]);

  return (
    <div className="component-details">
      <h3 className="details-title">{details.full_name}</h3>
      <table className="details-table">
        <thead>
          <tr>
            <th>Parametr</th>
            <th>Wartość</th>
            <th>Uwagi</th>
          </tr>
        </thead>
        <tbody>
          {visible.map(([key, value]) => {
            const remarkInfo = remarks[key];
            const scoreClass = remarkInfo ? `remark-score-${remarkInfo.score}` : 'remark-score-good';
            
            return (
              <tr key={key} className={scoreClass}>
                <td className="param">{labels[key]}</td>
                <td className="value">
                  {(() => {
                    if (Array.isArray(value)) {
                      return value.map((item, index) => <div key={index}>{item}</div>);
                    }
                    if (value === null) {
                      return '-';
                    }
                    if (typeof value === 'boolean') {
                      return value ? 'Tak' : 'Nie';
                    }
                    if (key === 'price' && value) {
                      return `${value} zł`;
                    }
                    return String(value);
                  })()}
                </td>
                <td className="note">{remarkInfo?.text || '—'}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <button onClick={handleSelect} className="select-button">Wybierz ten podzespół</button>
    </div>
  );
}

export default ComponentDetails;