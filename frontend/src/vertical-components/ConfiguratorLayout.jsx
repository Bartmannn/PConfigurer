import { useState } from "react";
import SummaryView from "./SummaryView";
import SelectView from "./SelectView";
import "./layout.css";

function ConfiguratorLayout() {
  const [activePanel, setActivePanel] = useState("summary");
  const [selectedCategory, setSelectedCategory] = useState(null);

  const [selected, setSelected] = useState({
    cpu: null,
    mobo: null,
    ram: null,
    gpu: null,
    psu: null,
    mem: null,
    chassis: null,
  });

  const handleSelectCategory = (category) => {
    setSelectedCategory(category);
    setActivePanel("select");
  };

  const handleBack = () => setActivePanel("summary");

  return (
    <div className={`configurator-container ${activePanel === "select" ? "show-select" : ""}`}>
      <SummaryView selected={selected} onSelectCategory={handleSelectCategory} />
      <SelectView
        category={selectedCategory}
        selected={selected}
        setSelected={setSelected}
        onBack={handleBack}
      />
    </div>
  );
}

export default ConfiguratorLayout;
