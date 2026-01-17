import { useMemo } from "react";

const CATEGORY_LABELS = {
  general: "Ogolne",
  cpu: "Procesory",
  mobo: "Plyty glowne",
  ram: "Pamiec RAM",
  mem: "Dyski",
  gpu: "Karty graficzne",
};

const FILTER_FIELDS = {
  general: [
    {
      key: "keep_incompatible",
      label: "Zachowaj niekompatybilne podzespoly",
      type: "toggle",
    },
  ],
  cpu: [
    { key: "family", label: "Rodzina", type: "multi" },
    { key: "generation", label: "Generacja", type: "multi" },
    { key: "manufacturer", label: "Producent", type: "multi" },
    { key: "socket", label: "Gniazdo", type: "multi" },
    { key: "p_cores", label: "Rdzenie / Performance", type: "multi" },
    { key: "e_cores", label: "Rdzenie efektywne", type: "multi" },
    { key: "threads", label: "Watki", type: "multi" },
    { key: "boost_clock_ghz", label: "Taktowanie boost (GHz)", type: "range" },
    { key: "supported_ram", label: "Wspierany RAM", type: "multi" },
    { key: "max_internal_memory_gb", label: "Max RAM (GB)", type: "multi" },
    { key: "supported_pcie", label: "Wspierane PCIe", type: "multi" },
    { key: "pcie_max_gen", label: "PCIe max gen", type: "multi" },
    { key: "tdp", label: "TDP (W)", type: "range" },
    { key: "price", label: "Cena", type: "range" },
    { key: "cache_mb", label: "Cache (MB)", type: "multi" },
    { key: "integrated_gpu", label: "Zintegrowana grafika", type: "bool-multi" },
  ],
  mobo: [
    { key: "manufacturer", label: "Producent", type: "multi" },
    { key: "socket", label: "Gniazdo", type: "multi" },
    { key: "form_factor", label: "Format", type: "multi" },
    { key: "supported_ram", label: "Wspierany RAM", type: "multi" },
    { key: "max_ram_capacity", label: "Max RAM (GB)", type: "multi" },
    { key: "dimm_slots", label: "Sloty DIMM", type: "multi" },
    { key: "pcie_max_gen", label: "PCIe max gen", type: "multi" },
    { key: "price", label: "Cena", type: "range" },
  ],
  ram: [
    { key: "manufacturer", label: "Producent", type: "multi" },
    { key: "base", label: "Baza", type: "multi" },
    { key: "modules_count", label: "Liczba modulow", type: "multi" },
    { key: "total_capacity", label: "Pojemnosc (GB)", type: "multi" },
    { key: "price", label: "Cena", type: "range" },
  ],
  mem: [
    { key: "manufacturer", label: "Producent", type: "multi" },
    { key: "connector", label: "Zlacze", type: "multi" },
    { key: "capacity_gb", label: "Pojemnosc (GB)", type: "multi" },
    { key: "pcie_max_gen", label: "PCIe max gen", type: "multi" },
    { key: "price", label: "Cena", type: "range" },
  ],
  gpu: [
    { key: "manufacturer", label: "Producent", type: "multi" },
    { key: "vram_size_gb", label: "VRAM (GB)", type: "multi" },
    { key: "base_clock_mhz", label: "Taktowanie bazowe (MHz)", type: "range" },
    { key: "boost_clock_mhz", label: "Taktowanie boost (MHz)", type: "range" },
    { key: "tdp", label: "TDP (W)", type: "range" },
    { key: "recommended_system_power_w", label: "Zalecana moc PSU (W)", type: "range" },
    { key: "length_mm", label: "Dlugosc (mm)", type: "range" },
    { key: "slot_width", label: "Szerokosc slotu", type: "range" },
    { key: "outputs", label: "Wyjscia", type: "multi" },
    { key: "price", label: "Cena", type: "range" },
    { key: "graphics_chip_vendor", label: "Producent chipu", type: "multi" },
    { key: "graphics_chip_marketing_name", label: "Model chipu", type: "multi" },
    { key: "graphics_chip_pcie_max_gen", label: "PCIe max gen", type: "multi" },
    { key: "graphics_chip_memory_type", label: "Typ pamieci", type: "multi" },
    { key: "graphics_chip_ray_tracing_gen", label: "Generacja RT", type: "multi" },
    { key: "graphics_chip_upscaling_technology", label: "Upscaling", type: "multi" },
  ],
};

function FiltersPanel({
  isOpen,
  activeCategory,
  onSelectCategory,
  filters,
  filterOptions,
  onChange,
  onClear,
  onClose,
  onApply,
}) {
  const categories = Object.keys(CATEGORY_LABELS);
  const fields = FILTER_FIELDS[activeCategory] || [];

  const pCoreLabel = useMemo(() => {
    if (activeCategory !== "cpu") return "Rdzenie / Performance";
    const manufacturers = filterOptions?.cpu?.manufacturer || [];
    const selected = filters?.cpu?.manufacturer || [];
    const selectedLabels = manufacturers
      .filter((opt) => selected.includes(String(opt.value)))
      .map((opt) => opt.label.toLowerCase());
    const hasIntel = selectedLabels.some((name) => name.includes("intel"));
    const hasAmd = selectedLabels.some((name) => name.includes("amd"));

    if (hasIntel && !hasAmd) return "Rdzenie performance";
    if (hasAmd && !hasIntel) return "Rdzenie";
    return "Rdzenie / Performance";
  }, [activeCategory, filterOptions, filters]);

  const getFieldLabel = (field) => {
    if (activeCategory === "cpu" && field.key === "p_cores") {
      return pCoreLabel;
    }
    return field.label;
  };

  const renderMultiField = (field) => {
    const options = filterOptions?.[activeCategory]?.[field.key] || [];
    const current = filters?.[activeCategory]?.[field.key] || [];

    return (
      <div className="filters-field" key={field.key}>
        <div className="filters-field-title">{getFieldLabel(field)}</div>
        <div className="filters-options">
          {options.length === 0 && (
            <div className="filters-empty">Brak danych.</div>
          )}
          {options.map((option) => {
            const value = String(option.value);
            const checked = current.includes(value);
            return (
              <label key={value} className="filters-option">
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => {
                    const next = checked
                      ? current.filter((item) => item !== value)
                      : [...current, value];
                    onChange(activeCategory, field.key, next);
                  }}
                />
                <span>{option.label}</span>
              </label>
            );
          })}
        </div>
      </div>
    );
  };

  const renderRangeField = (field) => {
    const current = filters?.[activeCategory]?.[field.key] || { min: "", max: "" };

    return (
      <div className="filters-field" key={field.key}>
        <div className="filters-field-title">{getFieldLabel(field)}</div>
        <div className="filters-range">
          <input
            type="number"
            placeholder="od"
            value={current.min}
            onChange={(event) =>
              onChange(activeCategory, field.key, { ...current, min: event.target.value })
            }
          />
          <span className="filters-range-separator">-</span>
          <input
            type="number"
            placeholder="do"
            value={current.max}
            onChange={(event) =>
              onChange(activeCategory, field.key, { ...current, max: event.target.value })
            }
          />
        </div>
      </div>
    );
  };

  const renderBoolField = (field) => {
    const current = filters?.[activeCategory]?.[field.key];
    const checked = current === true || current === "true";

    return (
      <div className="filters-field" key={field.key}>
        <div className="filters-field-title">{getFieldLabel(field)}</div>
        <label className="filters-option filters-boolean">
          <input
            type="checkbox"
            checked={checked}
            onChange={(event) =>
              onChange(activeCategory, field.key, event.target.checked)
            }
          />
          <span>Tak</span>
        </label>
      </div>
    );
  };

  const renderBoolMultiField = (field) => {
    const current = filters?.[activeCategory]?.[field.key] || [];
    const options = [
      { value: "true", label: "Tak" },
      { value: "false", label: "Nie" },
    ];

    return (
      <div className="filters-field" key={field.key}>
        <div className="filters-field-title">{getFieldLabel(field)}</div>
        <div className="filters-options filters-boolean">
          {options.map((option) => {
            const checked = current.includes(option.value);
            return (
              <label key={option.value} className="filters-option">
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => {
                    const next = checked
                      ? current.filter((item) => item !== option.value)
                      : [...current, option.value];
                    onChange(activeCategory, field.key, next);
                  }}
                />
                <span>{option.label}</span>
              </label>
            );
          })}
        </div>
      </div>
    );
  };

  const renderToggleField = (field) => {
    const current = Boolean(filters?.[activeCategory]?.[field.key]);

    return (
      <div className="filters-field" key={field.key}>
        <div className="filters-field-title">{getFieldLabel(field)}</div>
        <div className="filters-toggle-group">
          <button
            type="button"
            className={`filters-toggle-option ${!current ? "active" : ""}`}
            onClick={() => onChange(activeCategory, field.key, false)}
          >
            NIE
          </button>
          <button
            type="button"
            className={`filters-toggle-option ${current ? "active" : ""}`}
            onClick={() => onChange(activeCategory, field.key, true)}
          >
            TAK
          </button>
        </div>
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="filters-overlay">
      <div className="filters-panel">
        <div className="filters-categories">
          {categories.map((category) => (
            <button
              key={category}
              className={`filters-category ${activeCategory === category ? "active" : ""}`}
              onClick={() => onSelectCategory(category)}
            >
              {CATEGORY_LABELS[category]}
            </button>
          ))}
        </div>
        <div className="filters-content">
          <button className="filters-close" onClick={onClose} aria-label="Zamknij filtry">
            x
          </button>
          <div className="filters-scroll">
            <div className="filters-fields">
              {!filterOptions && activeCategory !== "general" && (
                <div className="filters-empty">Ladowanie filtrow...</div>
              )}
              {(filterOptions || activeCategory === "general") &&
                fields.map((field) => {
                  if (field.type === "range") return renderRangeField(field);
                  if (field.type === "bool") return renderBoolField(field);
                  if (field.type === "bool-multi") return renderBoolMultiField(field);
                  if (field.type === "toggle") return renderToggleField(field);
                  return renderMultiField(field);
                })}
            </div>
          </div>
          <div className="filters-actions-bar">
            <button className="filters-clear" onClick={onClear}>
              Wyczysc filtry
            </button>
            <button className="select-button filters-apply" onClick={onApply}>
              Zatwierdz ustawienia
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FiltersPanel;
