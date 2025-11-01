const CATEGORY_LABELS = {
  cpu: "Procesory",
  mobo: "Płyty główne",
  ram: "Pamięć RAM",
  gpu: "Karty graficzne",
  psu: "Zasilacze",
  mem: "Dyski",
  chassis: "Obudowy",
};

function SummaryView({ selected, onSelectCategory }) {
  const components = Object.keys(CATEGORY_LABELS);

  return (
    <div className="summary-view">
      <h2>Twój zestaw</h2>
      <div className="summary-grid">
        {components.map((key) => (
          <div 
            key={key} 
            className="summary-item" 
            onClick={() => onSelectCategory(key)}
          >
            <h4>{CATEGORY_LABELS[key]}</h4>
            <p>
              {selected[key]
                ? `${selected[key].name}`
                : "Nie wybrano podzespołu"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SummaryView;
