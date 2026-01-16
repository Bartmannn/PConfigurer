import { useEffect, useState } from "react";
import "./details.css";

const RAM_BASE_REGEX = /(DDR[345])[^0-9]*([0-9]{3,5})/i;

const formatUnit = (value, unit) => {
  if (value === null || value === undefined || value === "") return "-";
  return `${value} ${unit}`.trim();
};

const formatPrice = (value) => {
  if (value === null || value === undefined || value === "") return "-";
  return `${value} zł`;
};

const normalizeRamBase = (value) => {
  if (!value) return null;
  if (typeof value === "string") {
    const match = value.match(RAM_BASE_REGEX);
    if (!match) return null;
    return { type: match[1].toUpperCase(), mts: Number(match[2]) };
  }
  if (typeof value === "object") {
    const type = value.type || value.base_type || value.kind;
    const mts = value.mts || value.frequency || value.speed;
    if (!type || !mts) return null;
    return { type, mts: Number(mts) };
  }
  return null;
};

const formatRamFrequency = (base) => {
  if (!base) return "-";
  return `${base.type} ${base.mts}MHz`;
};

const buildRecommendedRam = (supportedRam) => {
  if (!Array.isArray(supportedRam)) return [];
  const byType = new Map();
  supportedRam.forEach((entry) => {
    const base = normalizeRamBase(entry);
    if (!base) return;
    const current = byType.get(base.type);
    if (!current || base.mts > current) {
      byType.set(base.type, base.mts);
    }
  });
  const order = ["DDR3", "DDR4", "DDR5"];
  return Array.from(byType.entries())
    .sort((a, b) => order.indexOf(a[0]) - order.indexOf(b[0]))
    .map(([type, mts]) => `${type} ${mts}MHz`);
};

const formatSupportedPcie = (supported) => {
  if (!Array.isArray(supported) || supported.length === 0) return "-";
  const versions = new Map();
  supported.forEach((entry) => {
    if (!entry) return;
    const version = entry.version ?? null;
    const lanes = entry.lanes;
    const quantity = entry.quantity ?? 1;
    if (!version) return;
    const bucket = versions.get(version) || [];
    if (lanes) {
      for (let i = 0; i < quantity; i += 1) {
        bucket.push(lanes);
      }
    }
    versions.set(version, bucket);
  });
  if (versions.size === 0) return "-";
  return Array.from(versions.entries())
    .sort((a, b) => Number(b[0]) - Number(a[0]))
    .map(([version, lanesList]) => {
      const lanesText = lanesList.length ? ` (${lanesList.join("+")})` : "";
      return `PCIe ${version}${lanesText}`;
    });
};

const formatStorageConnector = (connector) => {
  if (!connector) return "-";
  const version = connector.version ?? null;
  const lanes = connector.lanes ?? null;
  if (version && lanes) {
    return `PCIe ${version} x${lanes}`;
  }
  if (connector.category) {
    return connector.category;
  }
  return "-";
};

const formatPsuConnectors = (connectors) => {
  if (!connectors) return "-";
  const items = [];
  if (Array.isArray(connectors)) {
    connectors.forEach((item) => {
      if (!item || typeof item !== "object") return;
      const name = item.name || item.category || item.connector;
      const count = item.quantity ?? item.count ?? item.value;
      if (name && count !== undefined && count !== null) {
        items.push(`${name} - ${count} szt.`);
      }
    });
  } else if (typeof connectors === "object") {
    Object.entries(connectors).forEach(([name, count]) => {
      if (count !== undefined && count !== null) {
        items.push(`${name} - ${count} szt.`);
      }
    });
  }
  return items.length ? items : "-";
};

const formatGpuOutputs = (outputs, fallback) => {
  if (outputs === null || outputs === undefined || outputs === "") {
    return fallback && Array.isArray(fallback) && fallback.length ? fallback : "-";
  }
  if (Array.isArray(outputs)) {
    return outputs.length ? outputs : "-";
  }
  if (typeof outputs === "object") {
    return Object.entries(outputs).map(([name, count]) => `${name} - ${count} szt.`);
  }
  return String(outputs);
};

const formatPowerConnectors = (connectors) => {
  if (!Array.isArray(connectors) || connectors.length === 0) return "-";
  const items = connectors
    .filter((item) => item && item.pins)
    .map((item) => `${item.pins} pin - ${item.quantity ?? 1} szt.`);
  return items.length ? items : "-";
};

const formatClockGhz = (base, boost) => {
  if (!base && !boost) return "-";
  const baseText = base ? `${base} GHz` : "—";
  const boostText = boost ? ` (${boost} GHz w trybie boost)` : "";
  return `${baseText}${boostText}`;
};

const formatClockMhz = (base, boost) => {
  if (!base && !boost) return "-";
  const baseText = base ? `${base} MHz` : "—";
  const boostText = boost ? ` (${boost} MHz w trybie boost)` : "";
  return `${baseText}${boostText}`;
};

const buildRows = (category, details) => {
  if (!details) return [];
  const manufacturer = details.manufacturer || details.manufacturer_name || "-";

  switch (category) {
    case "ram": {
      const base = normalizeRamBase(details.base) || normalizeRamBase(details.type_info);
      return [
        { key: "name", label: "Nazwa", value: details.name || details.short_name },
        { key: "manufacturer", label: "Producent", value: manufacturer },
        { key: "base", label: "Typ", value: base?.type || "-" },
        { key: "frequency", label: "Częstotliwość", value: formatRamFrequency(base) },
        { key: "modules_count", label: "Liczba modułów", value: details.modules_count },
        { key: "total_capacity", label: "Pojemność", value: formatUnit(details.total_capacity, "GB") },
        { key: "price", label: "Cena", value: formatPrice(details.price) },
      ];
    }
    case "cpu": {
      const isIntel = manufacturer.toLowerCase().includes("intel");
      const ramRecommendations = buildRecommendedRam(details.supported_ram || details.ram_support_info);
      const pcieSupport = formatSupportedPcie(details.supported_pcie);
      const coreRows = isIntel
        ? [
            { key: "p_cores", label: "Rdzenie performance", value: details.p_cores },
            { key: "e_cores", label: "Rdzenie efficient", value: details.e_cores },
          ]
        : [{ key: "p_cores", label: "Rdzenie", value: details.p_cores }];
      return [
        { key: "manufacturer", label: "Producent", value: manufacturer },
        { key: "name", label: "Nazwa", value: details.name || details.short_name },
        { key: "family", label: "Rodzina", value: details.family },
        { key: "generation", label: "Generacja", value: details.generation },
        { key: "socket", label: "Socket", value: details.socket || details.socket_name },
        ...coreRows,
        { key: "threads", label: "Liczba wątków", value: details.threads },
        {
          key: "clock_speed",
          label: "Taktowanie rdzenia",
          value: formatClockGhz(details.base_clock_ghz, details.boost_clock_ghz),
        },
        { key: "cache_mb", label: "Cache", value: formatUnit(details.cache_mb, "MB") },
        {
          key: "integrated_gpu",
          label: "Zintegrowany układ graficzny",
          value: details.integrated_gpu,
        },
        {
          key: "ram_support",
          label: "Rekomendowany RAM",
          value: ramRecommendations.length ? ramRecommendations : "-",
        },
        {
          key: "max_internal_memory_gb",
          label: "Maksymalna pojemność RAM",
          value: formatUnit(details.max_internal_memory_gb, "GB"),
        },
        { key: "supported_pcie", label: "Wspierane PCIe", value: pcieSupport },
        { key: "tdp", label: "Pobór mocy", value: formatUnit(details.tdp, "W") },
        { key: "price", label: "Cena", value: formatPrice(details.price) },
      ];
    }
    case "mem": {
      return [
        { key: "manufacturer", label: "Producent", value: manufacturer },
        { key: "name", label: "Nazwa", value: details.name || details.short_name },
        { key: "connector", label: "Złącze", value: formatStorageConnector(details.connector) },
        { key: "capacity_gb", label: "Pojemność", value: formatUnit(details.capacity_gb, "GB") },
        { key: "price", label: "Cena", value: formatPrice(details.price) },
      ];
    }
    case "psu": {
      return [
        { key: "manufacturer", label: "Producent", value: manufacturer },
        { key: "name", label: "Nazwa", value: details.name || details.short_name },
        { key: "wattage", label: "Moc", value: formatUnit(details.wattage, "W") },
        { key: "connectors", label: "Złącza", value: formatPsuConnectors(details.connectors) },
        { key: "form_factor", label: "Standard", value: details.form_factor || details.form_factor_name },
        { key: "price", label: "Cena", value: formatPrice(details.price) },
      ];
    }
    case "gpu": {
      const chip = details.graphics_chip || {};
      const memoryType = chip.memory_type ? ` (${chip.memory_type})` : "";
      const pcieLabel =
        chip.pcie_max_gen && chip.pcie_max_width
          ? `PCIe ${chip.pcie_max_gen} x${chip.pcie_max_width}`
          : "-";
      return [
        { key: "manufacturer", label: "Producent", value: manufacturer },
        { key: "model_name", label: "Nazwa", value: details.model_name || details.short_name },
        { key: "chip", label: "Układ", value: chip.marketing_name || details.chip_name },
        {
          key: "vram",
          label: "Pamięć",
          value: details.vram_size_gb ? `${details.vram_size_gb}GB${memoryType}` : "-",
        },
        {
          key: "clock_speed",
          label: "Taktowanie rdzenia",
          value: formatClockMhz(details.base_clock_mhz, details.boost_clock_mhz),
        },
        { key: "pcie", label: "Rodzaj złącza", value: pcieLabel },
        {
          key: "outputs",
          label: "Wyjścia",
          value: formatGpuOutputs(details.outputs, details.ports_info),
        },
        { key: "length_mm", label: "Długość", value: formatUnit(details.length_mm, "mm") },
        { key: "slot_width", label: "Zajmowane sloty", value: details.slot_width ?? "-" },
        {
          key: "tdp",
          label: "Pobór mocy",
          value: details.tdp
            ? `${details.tdp} W (rekomendowany zasilacz: ${details.recommended_system_power_w || "—"} W)`
            : "-",
        },
        {
          key: "power_connectors",
          label: "Złącze zasilania",
          value: formatPowerConnectors(details.power_connectors),
        },
        { key: "price", label: "Cena", value: formatPrice(details.price) },
      ];
    }
    case "chassis": {
      return [
        { key: "manufacturer", label: "Producent", value: manufacturer },
        { key: "name", label: "Nazwa", value: details.name || details.short_name },
        {
          key: "mobo_form_factor_support",
          label: "Obsługiwany format płyt głównych",
          value: details.mobo_form_factor_support || details.mobo_support_info || "-",
        },
        {
          key: "psu_form_factor_support",
          label: "Obsługiwany format zasilaczy",
          value: details.psu_form_factor_support || "-",
        },
        {
          key: "max_gpu_length_mm",
          label: "Maksymalna długość karty graficznej",
          value: formatUnit(details.max_gpu_length_mm, "mm"),
        },
        { key: "price", label: "Cena", value: formatPrice(details.price) },
      ];
    }
    case "mobo": {
      const ramRecommendations = buildRecommendedRam(details.supported_ram);
      const connectors = Array.isArray(details.connectors)
        ? details.connectors.map((item) => {
            if (!item) return null;
            const version = item.version ? ` ${item.version}` : "";
            const lanes = item.lanes ? ` x${item.lanes}` : "";
            const label = `${item.category || "Złącze"}${version}${lanes}`.trim();
            return `${label} - ${item.quantity ?? 1} szt.`;
          }).filter(Boolean)
        : [];
      return [
        { key: "manufacturer", label: "Producent", value: manufacturer },
        { key: "name", label: "Nazwa", value: details.name || details.short_name },
        { key: "socket", label: "Socket", value: details.socket || details.socket_name },
        { key: "form_factor", label: "Format", value: details.form_factor || details.form_factor_name },
        {
          key: "supported_ram",
          label: "Wspierana pamięć RAM",
          value: ramRecommendations.length ? ramRecommendations : "-",
        },
        {
          key: "max_ram_capacity",
          label: "Maksymalna obsługiwana pamięć RAM",
          value: formatUnit(details.max_ram_capacity, "GB"),
        },
        { key: "dimm_slots", label: "Liczba slotów DIMM", value: details.dimm_slots },
        { key: "connectors", label: "Złącza", value: connectors.length ? connectors : "-" },
        { key: "price", label: "Cena", value: formatPrice(details.price) },
      ];
    }
    default:
      return [];
  }
};

function ComponentDetails({ category, selectedItem, onSelect, onBack }) {
  const [details, setDetails] = useState(null);

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
        const res = await fetch(`http://localhost:8000/api/${endpoint}/${selectedItem.id}/`);  // pobieranie szczegółowych danych
        const data = await res.json();
        setDetails(data);
      } catch (err) {
        console.error("Błąd pobierania szczegółów:", err);
      }
    };

    fetchData();
  }, [category, selectedItem]);

  if (!details)
    return <div className="component-details">Wybierz podzespół z listy.</div>;

  const rows = buildRows(category, details);

  return (
    <div className="component-details">
      <h3 className="details-title">{details.full_name || details.name || details.short_name}</h3>
      <table className="details-table">
        <thead>
          <tr>
            <th>Parametr</th>
            <th>Wartość</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(({ key, label, value }) => {
            const renderValue = () => {
              if (Array.isArray(value)) {
                return value.map((item, index) => <div key={`${key}-${index}`}>{item}</div>);
              }
              if (value === null || value === undefined || value === "") {
                return "-";
              }
              if (typeof value === "boolean") {
                return value ? "Tak" : "Nie";
              }
              return String(value);
            };

            return (
              <tr key={key}>
                <td className="param">{label}</td>
                <td className="value">{renderValue()}</td>
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
