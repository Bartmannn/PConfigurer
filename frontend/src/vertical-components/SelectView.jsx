import { useState, useEffect } from "react";
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

  // aktualizuj stan lokalny po zmianie kategorii lub zewnętrznego wyboru
  useEffect(() => {
    setSelectedItem(selected[category] || null);
  }, [category, selected]);

  const handleSelectItem = (item) => {
    setSelectedItem(item);
    setSelected((prev) => ({ ...prev, [category]: item }));
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
            onSelect={handleSelectItem}
            selectedItem={selectedItem}
          />
        ) : (
          <p>Wybierz kategorię z listy.</p>
        )}
      </div>

      <div className="select-right">
        <ComponentDetails category={category} selectedItem={selectedItem} />
      </div>
    </div>
  );
}

export default SelectView;
