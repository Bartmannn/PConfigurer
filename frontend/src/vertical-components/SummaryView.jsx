import BuildEvaluation from './BuildEvaluation';
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

const PRICE_FORMATTER = new Intl.NumberFormat("pl-PL", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const parsePriceValue = (value) => {
  if (value === null || value === undefined) return null;
  if (typeof value === "number") return Number.isFinite(value) ? value : null;
  if (typeof value === "string") {
    const normalized = value.replace(/\s/g, "").replace(",", ".");
    const parsed = Number(normalized);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
};

const sumSelectedPrices = (selected) => {
  let total = 0;
  const addPrice = (item) => {
    if (!item) return;
    const parsed = parsePriceValue(item.price);
    if (parsed !== null) total += parsed;
  };

  Object.values(selected || {}).forEach((item) => {
    if (Array.isArray(item)) {
      item.forEach(addPrice);
    } else {
      addPrice(item);
    }
  });

  return total;
};

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
  builderOpen,
  onOpenBuilder,
  onCloseBuilder,
  buildBudgets,
  onSelectBudget,
  builderLoading,
  builderError,
}) {
  const components = Object.keys(CATEGORY_LABELS);
  const totalPrice = sumSelectedPrices(selected);
  const formattedPrice = PRICE_FORMATTER.format(totalPrice);

  return (
    <div className="summary-view">
      <div className="summary-toolbar">
        <button className="filters-toggle" onClick={onOpenFilters} aria-label="Otworz filtry">
          Filtry
        </button>
        <button className="builder-toggle" onClick={onOpenBuilder} aria-label="Buduj zestaw">
          Buduj
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
          <div className="summary-suggestions">
            <BuildEvaluation />
          </div>
          <div className="summary-price" aria-live="polite">
            <span className="summary-price-label">Cena zestawu</span>
            <span className="summary-price-value">{formattedPrice} zł</span>
          </div>
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
      {builderOpen && (
        <div className="builder-overlay">
          <div className="builder-modal">
            <button className="builder-close" onClick={onCloseBuilder} aria-label="Zamknij budowanie">
              x
            </button>
            <h3>Wybierz budżet</h3>
            <div className="builder-budgets">
              {buildBudgets.map((budget) => (
                <button
                  key={budget}
                  className="builder-budget"
                  onClick={() => onSelectBudget(budget)}
                  disabled={builderLoading}
                >
                  {budget} zł
                </button>
              ))}
            </div>
            {builderError && <div className="builder-error">{builderError}</div>}
          </div>
        </div>
      )}
    </div>
  );
}

export default SummaryView;
