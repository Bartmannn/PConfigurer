import { useState, useContext, useEffect } from "react";
import { ConfiguratorContext } from "../context/ConfiguratorContext";
import ComponentList from "./ComponentList";
import ComponentDetails from "./ComponentDetails";

const CATEGORY_LABELS = {
  cpu: "Procesory",
  gpu: "Karty graficzne",
  ram: "Pamięć RAM",
  mobo: "Płyty główne",
  psu: "Zasilacze",
  mem: "Dyski",
  chassis: "Obudowy",
};

function SelectView({ category, selected, setSelected, onBack }) {
  const [selectedItem, setSelectedItem] = useState(null);
  const { updateBuild } = useContext(ConfiguratorContext);

  useEffect(() => {
    // When the category changes, initialize the previewed item
    // to the one already selected in the build.
    if (category && selected[category]) {
      setSelectedItem(selected[category]);
    } else {
      setSelectedItem(null);
    }
  }, [category, selected]);

  const handlePreviewItem = (item) => {
    setSelectedItem(item);
  };

  const handleSelectItem = (item) => {
    setSelectedItem(item);
    setSelected((prev) => ({ ...prev, [category]: item }));
    updateBuild(category, item); // Synchronizuj globalny stan
  };

  return (
    <div className="select-view">
      <div className="select-left">
        <button onClick={onBack}>← Powrót</button>
        <h3>{category ? CATEGORY_LABELS[category] : "Wybierz kategorię"}</h3>
        {category ? (
          <ComponentList 
            category={category}
            selected={selected}
            onPreview={handlePreviewItem}
            onSelect={handleSelectItem} // Przywrócenie onSelect dla przycisku "Brak"
            selectedItem={selectedItem}
          />
        ) : (
          <p>Wybierz kategorię z listy.</p>
        )}
      </div>

      <div className="select-right">
        <ComponentDetails 
          category={category} 
          selectedItem={selectedItem} 
          onSelect={handleSelectItem}
          onBack={onBack} // Przekaż funkcję onBack
        />
      </div>
    </div>
  );
}

export default SelectView;
