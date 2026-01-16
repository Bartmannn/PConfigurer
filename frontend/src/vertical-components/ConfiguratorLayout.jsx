import { useState, useEffect, useContext } from "react";
import SummaryView from "./SummaryView";
import SelectView from "./SelectView";
import "./layout.css";
import { ConfiguratorContext } from "../context/ConfiguratorContext";

const buildRange = () => ({ min: "", max: "" });

const getDefaultFilters = () => ({
  cpu: {
    family: [],
    generation: [],
    manufacturer: [],
    socket: [],
    p_cores: [],
    e_cores: [],
    threads: [],
    boost_clock_ghz: buildRange(),
    supported_ram: [],
    max_internal_memory_gb: [],
    supported_pcie: [],
    pcie_max_gen: [],
    tdp: buildRange(),
    price: buildRange(),
    cache_mb: [],
    integrated_gpu: [],
  },
  mobo: {
    manufacturer: [],
    socket: [],
    form_factor: [],
    supported_ram: [],
    max_ram_capacity: [],
    dimm_slots: [],
    pcie_max_gen: [],
    price: buildRange(),
  },
  ram: {
    manufacturer: [],
    base: [],
    modules_count: [],
    total_capacity: [],
    price: buildRange(),
  },
  mem: {
    manufacturer: [],
    connector: [],
    capacity_gb: [],
    pcie_max_gen: [],
    price: buildRange(),
  },
  gpu: {
    manufacturer: [],
    vram_size_gb: [],
    base_clock_mhz: buildRange(),
    boost_clock_mhz: buildRange(),
    tdp: buildRange(),
    recommended_system_power_w: buildRange(),
    length_mm: buildRange(),
    slot_width: buildRange(),
    outputs: [],
    price: buildRange(),
    graphics_chip_vendor: [],
    graphics_chip_marketing_name: [],
    graphics_chip_pcie_max_gen: [],
    graphics_chip_memory_type: [],
    graphics_chip_ray_tracing_gen: [],
    graphics_chip_upscaling_technology: [],
  },
});

function ConfiguratorLayout() {
  const { updateBuild } = useContext(ConfiguratorContext);
  const [activePanel, setActivePanel] = useState("summary");
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [activeFilterCategory, setActiveFilterCategory] = useState("cpu");
  const [filters, setFilters] = useState(getDefaultFilters());
  const [filterOptions, setFilterOptions] = useState(null);
  const [builderOpen, setBuilderOpen] = useState(false);
  const [builderLoading, setBuilderLoading] = useState(false);
  const [builderError, setBuilderError] = useState("");

  const [selected, setSelected] = useState({
    cpu: null,
    mobo: null,
    ram: null,
    gpu: null,
    psu: null,
    mem: null,
    chassis: null,
  });
  const buildBudgets = [5000, 7000, 9000, 11000, 13000, 15000];

  const handleSelectCategory = (category) => {
    setSelectedCategory(category);
    setActivePanel("select");
  };

  const handleBack = () => setActivePanel("summary");

  useEffect(() => {
    fetch("http://localhost:8000/api/filters/options/")
      .then((res) => res.json())
      .then((data) => setFilterOptions(data))
      .catch((err) => console.error("Błąd pobierania filtrów:", err));
  }, []);

  const handleFilterChange = (category, field, value) => {
    setFilters((prev) => {
      const next = {
        ...prev,
        [category]: { ...prev[category], [field]: value },
      };

      if (field === "socket") {
        if (category !== "cpu") next.cpu = { ...next.cpu, socket: value };
        if (category !== "mobo") next.mobo = { ...next.mobo, socket: value };
      }

      if (field === "supported_ram" || field === "base") {
        next.cpu = { ...next.cpu, supported_ram: value };
        next.mobo = { ...next.mobo, supported_ram: value };
        next.ram = { ...next.ram, base: value };
      }

      if (field === "pcie_max_gen" || field === "graphics_chip_pcie_max_gen") {
        next.cpu = { ...next.cpu, pcie_max_gen: value };
        next.mobo = { ...next.mobo, pcie_max_gen: value };
        next.mem = { ...next.mem, pcie_max_gen: value };
        next.gpu = { ...next.gpu, graphics_chip_pcie_max_gen: value };
      }

      if (field === "modules_count" || field === "dimm_slots") {
        next.ram = { ...next.ram, modules_count: value };
        next.mobo = { ...next.mobo, dimm_slots: value };
      }

      return next;
    });
  };

  const handleClearFilters = () => {
    setFilters(getDefaultFilters());
  };

  const applyBuild = (data) => {
    const next = {
      cpu: data.cpu,
      mobo: data.mobo,
      ram: data.ram,
      gpu: data.gpu,
      psu: data.psu,
      mem: data.mem,
      chassis: data.chassis,
    };
    setSelected(next);
    Object.entries(next).forEach(([key, value]) => {
      updateBuild(key, value);
    });
  };

  const handleBuildRequest = (budget) => {
    setBuilderLoading(true);
    setBuilderError("");
    fetch(`http://localhost:8000/api/builder/?budget=${budget}`)
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          const message = data?.error || "Brak zestawu dla wybranego budzetu.";
          throw new Error(message);
        }
        return data;
      })
      .then((data) => {
        applyBuild(data);
        setBuilderOpen(false);
      })
      .catch((err) => {
        setBuilderError(err.message || "Nie udalo sie zbudowac zestawu.");
      })
      .finally(() => {
        setBuilderLoading(false);
      });
  };

  const handleOpenBuilder = () => {
    setBuilderError("");
    setBuilderOpen(true);
  };

  const handleCloseBuilder = () => {
    if (!builderLoading) {
      setBuilderOpen(false);
    }
  };

  return (
    <div className={`configurator-container ${activePanel === "select" ? "show-select" : ""}`}>
      <SummaryView
        selected={selected}
        onSelectCategory={handleSelectCategory}
        filtersOpen={filtersOpen && activePanel === "summary"}
        onOpenFilters={() => setFiltersOpen(true)}
        onCloseFilters={() => setFiltersOpen(false)}
        onClearFilters={handleClearFilters}
        filterOptions={filterOptions}
        filters={filters}
        activeFilterCategory={activeFilterCategory}
        onSelectFilterCategory={setActiveFilterCategory}
        onFilterChange={handleFilterChange}
        builderOpen={builderOpen && activePanel === "summary"}
        onOpenBuilder={handleOpenBuilder}
        onCloseBuilder={handleCloseBuilder}
        buildBudgets={buildBudgets}
        onSelectBudget={handleBuildRequest}
        builderLoading={builderLoading}
        builderError={builderError}
      />
      <SelectView
        key={selectedCategory} // Resetuj stan komponentu przy zmianie kategorii
        category={selectedCategory}
        selected={selected}
        setSelected={setSelected}
        onBack={handleBack}
        filters={filters}
      />
    </div>
  );
}

export default ConfiguratorLayout;
