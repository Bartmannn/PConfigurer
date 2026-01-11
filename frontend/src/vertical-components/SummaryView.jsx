import FiltersPanel from "./FiltersPanel";

const CATEGORY_LABELS = {
  cpu: "Procesory",
  mobo: "Płyty główne",
  ram: "Pamięć RAM",
  gpu: "Karty graficzne",
  psu: "Zasilacze",
  mem: "Dyski",
  chassis: "Obudowy",
};

import BuildEvaluation from './BuildEvaluation';

function SummaryView({
  selected,
  onSelectCategory,
  filtersOpen,
  onOpenFilters,
  onCloseFilters,
  onFilterChange,
  onClearFilters,
  filterOptions,
  filters,
  activeFilterCategory,
  onSelectFilterCategory,
}) {
  const components = Object.keys(CATEGORY_LABELS);

  return (
    <div className="summary-view">
      <div className="summary-toolbar">
        <button className="filters-toggle" onClick={onOpenFilters} aria-label="Otworz filtry">
          Filtry
        </button>
      </div>
      <h2>Twój zestaw</h2>
      <div className="summary-content">
        <div className="summary-left">
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
                    ? `${selected[key].short_name}`
                    : "Nie wybrano podzespołu"}
                </p>
              </div>
            ))}
          </div>
        </div>
        <div className="summary-right">
          <BuildEvaluation />
        </div>
      </div>
      <FiltersPanel
        isOpen={filtersOpen}
        activeCategory={activeFilterCategory}
        onSelectCategory={onSelectFilterCategory}
        filters={filters}
        filterOptions={filterOptions}
        onChange={onFilterChange}
        onClear={onClearFilters}
        onClose={onCloseFilters}
        onApply={onCloseFilters}
      />
    </div>
  );
}

export default SummaryView;
