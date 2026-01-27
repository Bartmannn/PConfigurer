const normalizeRamBase = (value) => {
  if (!value) return null;
  if (typeof value === "string") {
    const match = value.match(/(DDR[345])[^0-9]*([0-9]{3,5})/i);
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

const getBuildPart = (build, key, fallbackKey) => {
  if (!build) return null;
  return build[key] || (fallbackKey ? build[fallbackKey] : null) || null;
};

const getCpu = (build) => getBuildPart(build, "cpu");
const getGpu = (build) => getBuildPart(build, "gpu");
const getRam = (build) => getBuildPart(build, "ram");
const getPsu = (build) => getBuildPart(build, "psu");
const getMobo = (build) => getBuildPart(build, "mobo", "motherboard");
const getChassis = (build) => getBuildPart(build, "chassis", "case");
const getStorage = (build) => getBuildPart(build, "mem", "storage");

const isSelectedValue = (value) => {
  if (!value) return false;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === "object") return Object.keys(value).length > 0;
  return true;
};

const hasAnySelectedComponent = (build) => {
  if (!build) return false;
  const ram = getRam(build);
  if (isSelectedValue(ram)) return true;
  return [
    getCpu(build),
    getGpu(build),
    getMobo(build),
    getPsu(build),
    getChassis(build),
    getStorage(build),
  ].some(isSelectedValue);
};

const toNumber = (value) => {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
};

const parsePsuConnectorCategory = (value) => {
  if (!value) return null;
  const lowered = String(value).toLowerCase();
  if (lowered.includes("pcie") || lowered.includes("pci-e")) {
    return "PCIe Power";
  }
  return null;
};

const parsePsuConnectorPins = (value) => {
  if (!value) return null;
  const text = String(value);
  const pinMatch = text.match(/(\d+)\s*-?\s*pin/i);
  if (pinMatch) return toNumber(pinMatch[1]);
  const plusMatch = text.match(/(\d+)\s*\+\s*(\d+)/);
  if (plusMatch) {
    const left = toNumber(plusMatch[1]);
    const right = toNumber(plusMatch[2]);
    if (left !== null && right !== null) return left + right;
  }
  return null;
};

const normalizePsuConnector = (item) => {
  if (!item) return null;
  if (typeof item === "string") {
    return {
      category: parsePsuConnectorCategory(item),
      pins: parsePsuConnectorPins(item),
      quantity: 1,
    };
  }
  if (typeof item === "object") {
    const name = item.name || item.label || item.connector;
    const category = item.category || parsePsuConnectorCategory(name);
    if (!category) return null;
    const quantity = toNumber(item.quantity ?? item.count ?? item.value) ?? 1;
    const pins = toNumber(item.lanes ?? item.pins ?? item.pin_count) ?? parsePsuConnectorPins(name);
    return { category, pins, quantity };
  }
  return null;
};

const getPsuPciePinsList = (psu) => {
  if (!psu || !psu.connectors) return null;
  const connectors = Array.isArray(psu.connectors)
    ? psu.connectors
    : typeof psu.connectors === "object"
      ? Object.entries(psu.connectors).map(([name, count]) => ({ name, quantity: count }))
      : [];
  const pins = [];
  let hasData = false;
  let hasMissing = false;

  connectors.forEach((item) => {
    const normalized = normalizePsuConnector(item);
    if (!normalized || normalized.category !== "PCIe Power") return;
    const connectorPins = toNumber(normalized.pins);
    const quantity = toNumber(normalized.quantity) ?? 1;
    hasData = true;
    if (connectorPins === null) {
      hasMissing = true;
      return;
    }
    for (let i = 0; i < quantity; i += 1) {
      pins.push(connectorPins);
    }
  });

  if (!hasData) return [];
  if (hasMissing) return null;
  return pins;
};

const getGpuRequiredPinsList = (gpu) => {
  if (!gpu || !Array.isArray(gpu.power_connectors)) return null;
  if (gpu.power_connectors.length === 0) return [];
  const pins = [];

  for (const item of gpu.power_connectors) {
    if (!item) continue;
    const connectorPins = toNumber(item.pins);
    const quantity = toNumber(item.quantity) ?? 1;
    if (connectorPins === null) {
      return null;
    }
    for (let i = 0; i < quantity; i += 1) {
      pins.push(connectorPins);
    }
  }

  return pins;
};

const findBestSubsetIndices = (values, target) => {
  let bestSum = Infinity;
  let best = null;

  const walk = (start, sum, chosen) => {
    if (sum >= target) {
      if (sum < bestSum) {
        bestSum = sum;
        best = [...chosen];
      }
      return;
    }
    if (start >= values.length) return;
    if (sum >= bestSum) return;

    for (let i = start; i < values.length; i += 1) {
      chosen.push(i);
      walk(i + 1, sum + values[i], chosen);
      chosen.pop();
    }
  };

  walk(0, 0, []);
  return best;
};

const canSatisfyGpuPower = (availablePins, requiredPins) => {
  if (availablePins === null || requiredPins === null) return null;
  if (requiredPins.length === 0) return true;
  if (availablePins.length === 0) return false;

  let available = [...availablePins].sort((a, b) => b - a);
  const required = [...requiredPins].sort((a, b) => b - a);

  for (const req of required) {
    const subset = findBestSubsetIndices(available, req);
    if (!subset) return false;
    const toRemove = new Set(subset);
    available = available.filter((_, index) => !toRemove.has(index));
  }

  return true;
};

const formatPinList = (pins) => {
  if (pins === null) return "brak danych";
  if (pins.length === 0) return "brak";
  const counts = new Map();
  pins.forEach((pin) => {
    if (pin === null || pin === undefined) return;
    const key = Number(pin);
    counts.set(key, (counts.get(key) || 0) + 1);
  });

  return Array.from(counts.entries())
    .sort((a, b) => b[0] - a[0])
    .map(([pin, count]) => `${pin}-pin x${count}`)
    .join(", ");
};

const buildRamSupportMap = (supportedRam) => {
  const map = new Map();
  if (!Array.isArray(supportedRam)) return map;
  supportedRam.forEach((entry) => {
    const base = normalizeRamBase(entry);
    if (!base) return;
    const current = map.get(base.type);
    if (current === undefined || base.mts > current) {
      map.set(base.type, base.mts);
    }
  });
  return map;
};

const getRamSupportMap = (component) => {
  if (!component) return new Map();
  const map = buildRamSupportMap(component.supported_ram);
  if (map.size > 0) return map;

  if (Array.isArray(component.supported_ram_types)) {
    const fallback = new Map();
    component.supported_ram_types.forEach((type) => {
      if (type) fallback.set(type, null);
    });
    return fallback;
  }

  return new Map();
};

const formatRamSupportMap = (map) => {
  if (!map || map.size === 0) return null;
  return Array.from(map.entries())
    .map(([type, mts]) => (mts ? `${type} ${mts} MHz` : `${type}`))
    .join(", ");
};

const getRamBase = (ram) => {
  if (!ram) return null;
  return normalizeRamBase(ram.base) || normalizeRamBase(ram.type_info);
};

const getMaxMtsForType = (map, type) => {
  if (!map || !type) return null;
  return map.get(type) ?? null;
};

const buildRamSupportRemarkText = ({ cpuMap, moboMap, cpu, mobo }) => {
  const parts = [];
  if (cpu) {
    const cpuText = formatRamSupportMap(cpuMap);
    parts.push(`CPU max: ${cpuText || "brak danych"}`);
  } else {
    parts.push("CPU: nie wybrany");
  }

  if (mobo) {
    const moboText = formatRamSupportMap(moboMap);
    parts.push(`Płyta max: ${moboText || "brak danych"}`);
  } else {
    parts.push("Płyta: nie wybrana");
  }

  return parts.join(", ");
};

const buildRamTypeRemarkText = ({ cpuMap, moboMap, cpu, mobo, ramBase }) => {
  const parts = [];
  const cpuTypes = cpuMap ? Array.from(cpuMap.keys()) : [];
  const moboTypes = moboMap ? Array.from(moboMap.keys()) : [];
  if (cpu) {
    parts.push(`CPU: ${cpuTypes.length ? cpuTypes.join(", ") : "brak danych"}`);
  } else {
    parts.push("CPU: nie wybrany");
  }

  if (mobo) {
    parts.push(`Płyta: ${moboTypes.length ? moboTypes.join(", ") : "brak danych"}`);
  } else {
    parts.push("Płyta: nie wybrana");
  }

  if (ramBase?.type) {
    parts.push(`RAM: ${ramBase.type}`);
  } else {
    parts.push("RAM: nie wybrany");
  }

  return parts.join(", ");
};

const getMaxPcieVersionFromCpu = (cpu) => {
  if (!cpu || !Array.isArray(cpu.supported_pcie)) return null;
  let maxVersion = null;
  cpu.supported_pcie.forEach((entry) => {
    const version = toNumber(entry?.version);
    if (version === null) return;
    if (maxVersion === null || version > maxVersion) {
      maxVersion = version;
    }
  });
  return maxVersion;
};

const getMaxPcieVersionFromMobo = (mobo) => {
  if (!mobo || !Array.isArray(mobo.connectors)) return null;
  let maxVersion = null;
  mobo.connectors.forEach((entry) => {
    if (entry?.category !== "PCIe") return;
    const version = toNumber(entry?.version);
    if (version === null) return;
    if (maxVersion === null || version > maxVersion) {
      maxVersion = version;
    }
  });
  return maxVersion;
};

const getGpuPcieVersion = (gpu) => {
  if (!gpu) return null;
  const version = gpu.graphics_chip?.pcie_max_gen ?? gpu.graphics_chip_pcie_max_gen;
  return toNumber(version);
};

const getStoragePcieVersion = (mem) => {
  if (!mem || !mem.connector) return null;
  const category = mem.connector?.category || mem.connector?.connector?.category || "";
  if (!category.toLowerCase().includes("pcie")) return null;
  return toNumber(mem.connector?.version);
};

const buildPcieContextText = ({ cpuMax, moboMax, gpuVer, storageVer }) => {
  const parts = [];
  if (cpuMax !== null) {
    parts.push(`CPU max: PCIe ${cpuMax}`);
  } else {
    parts.push("CPU: brak danych PCIe");
  }

  if (moboMax !== null) {
    parts.push(`Płyta max: PCIe ${moboMax}`);
  } else {
    parts.push("Płyta: brak danych PCIe");
  }

  if (gpuVer !== null) {
    parts.push(`GPU: PCIe ${gpuVer}`);
  }
  if (storageVer !== null) {
    parts.push(`SSD: PCIe ${storageVer}`);
  }

  return parts.join(", ");
};

const generateCpuRemarks = (cpu, build) => {
  const remarks = {};
  const mobo = getMobo(build);
  const ram = getRam(build);
  const gpu = getGpu(build);
  const storage = getStorage(build);
  const buildEmpty = !hasAnySelectedComponent(build);

  if (mobo?.socket && cpu.socket) {
    if (cpu.socket === mobo.socket) {
      remarks.socket = { score: "good", text: "Gniazdo procesora jest kompatybilne." };
    } else {
      remarks.socket = { score: "bad", text: "Niezgodne gniazdo procesora!" };
    }
  } else if (!mobo) {
    remarks.socket = {
      score: "good",
      text: "Płyta główna nie została wybrana.",
    };
  }

  const cpuMap = getRamSupportMap(cpu);
  const moboMap = getRamSupportMap(mobo);
  const ramBase = getRamBase(ram);
  const ramContext = buildRamSupportRemarkText({ cpuMap, moboMap, cpu, mobo });
  const typeContext = buildRamTypeRemarkText({ cpuMap, moboMap, cpu, mobo, ramBase });
  const cpuTypes = Array.from(cpuMap.keys());
  const moboTypes = Array.from(moboMap.keys());

  let typeScore = "good";
  if (ramBase?.type) {
    if (!cpuTypes.includes(ramBase.type)) {
      typeScore = "bad";
    } else if (mobo && (!moboTypes.length || !moboTypes.includes(ramBase.type))) {
      typeScore = "bad";
    }
  } else if (mobo) {
    if (!cpuTypes.length || !moboTypes.length || !cpuTypes.some((item) => moboTypes.includes(item))) {
      typeScore = "bad";
    }
  }

  remarks.ram_type = { score: typeScore, text: typeContext };

  if (ramBase) {
    const cpuMax = getMaxMtsForType(cpuMap, ramBase.type);
    const moboMax = getMaxMtsForType(moboMap, ramBase.type);
    let score = "good";
    if (cpuMax === null || (mobo && moboMax === null)) {
      score = "bad";
    } else {
      const limit = mobo ? Math.min(cpuMax ?? Infinity, moboMax ?? Infinity) : cpuMax;
      if (limit !== null && ramBase.mts > limit) {
        score = "ok";
      }
    }
    remarks.ram_frequency = { score, text: `${ramContext}, Wybrany RAM: ${ramBase.mts} MHz` };
  } else {
    remarks.ram_frequency = { score: "good", text: `${ramContext}, RAM: nie wybrany` };
  }

  const cpuMax = getMaxPcieVersionFromCpu(cpu);
  const moboMax = getMaxPcieVersionFromMobo(mobo);
  const gpuVer = getGpuPcieVersion(gpu);
  const storageVer = getStoragePcieVersion(storage);
  if (cpuMax !== null || moboMax !== null || gpuVer !== null || storageVer !== null) {
    const text = buildPcieContextText({ cpuMax, moboMax, gpuVer, storageVer });
    const limited =
      (gpuVer !== null && cpuMax !== null && gpuVer > cpuMax) ||
      (storageVer !== null && cpuMax !== null && storageVer > cpuMax);
    remarks.supported_pcie = {
      score: limited ? "ok" : "good",
      text: limited ? `${text} (ograniczenie przez CPU)` : text,
    };
  }

  return remarks;
};

const generateRamRemarks = (ram, build) => {
  const remarks = {};
  const mobo = getMobo(build);
  const cpu = getCpu(build);

  if (mobo) {
    const ramType = getRamBase(ram)?.type;
    const supportedTypes = Array.from(getRamSupportMap(mobo).keys());
    if (ramType && supportedTypes.length) {
      const match = supportedTypes.map((item) => item.toLowerCase()).includes(ramType.toLowerCase());
      if (match) {
        remarks.base = { score: "good", text: "Standard RAM jest kompatybilny." };
      } else {
        remarks.base = { score: "bad", text: "Standard RAM nie jest wspierany przez płytę." };
      }
    }

    if (ram.total_capacity && mobo.max_ram_capacity && ram.total_capacity > mobo.max_ram_capacity) {
      remarks.total_capacity = {
        score: "bad",
        text: `Pojemność RAM przekracza limit plyty (${mobo.max_ram_capacity}GB).`,
      };
    }
  } else {
    remarks.base = { score: "good", text: "Płyta główna nie została wybrana." };
  }

  const cpuMap = getRamSupportMap(cpu);
  const moboMap = getRamSupportMap(mobo);
  const ramBase = getRamBase(ram);
  const context = buildRamSupportRemarkText({ cpuMap, moboMap, cpu, mobo });
  if (ramBase) {
    const cpuMax = getMaxMtsForType(cpuMap, ramBase.type);
    const moboMax = getMaxMtsForType(moboMap, ramBase.type);
    let score = "good";
    if ((cpu && cpuMax === null) || (mobo && moboMax === null)) {
      score = "bad";
    } else if (
      (cpuMax !== null && ramBase.mts > cpuMax) ||
      (moboMax !== null && ramBase.mts > moboMax)
    ) {
      score = "ok";
    }
    remarks.frequency = { score, text: context };
  } else {
    remarks.frequency = { score: null, text: `${context}, RAM: brak danych` };
  }

  return remarks;
};

const generateGpuRemarks = (gpu, build) => {
  const remarks = {};
  const chassis = getChassis(build);
  const psu = getPsu(build);
  const cpu = getCpu(build);
  const mobo = getMobo(build);

  if (chassis && gpu.length_mm && chassis.max_gpu_length_mm) {
    if (gpu.length_mm > chassis.max_gpu_length_mm) {
      remarks.length_mm = {
        score: "bad",
        text: `Karta jest za długa do obudowy (max ${chassis.max_gpu_length_mm}mm).`,
      };
    } else {
      remarks.length_mm = {
        score: "good",
        text: `Długość GPU: ${gpu.length_mm}mm, limit obudowy: ${chassis.max_gpu_length_mm}mm.`,
      };
    }
  }

  if (psu?.wattage) {
    if (gpu?.recommended_system_power_w) {
      const recommended = toNumber(gpu.recommended_system_power_w);
      const psuWattage = toNumber(psu.wattage);
      const score =
        recommended !== null && psuWattage !== null && psuWattage < recommended
          ? "bad"
          : "good";
      remarks.tdp = {
        score,
        text: `Zasilacz: ${psu.wattage} W, GPU rekomenduje: ${
          recommended ?? gpu.recommended_system_power_w
        } W.`,
      };
    } else {
      remarks.tdp = { score: "good", text: `Zasilacz: ${psu.wattage} W.` };
    }
  } else {
    remarks.tdp = { score: "good", text: "Zasilacz nie został jeszcze wybrany." };
  }

  if (psu) {
    const requiredPins = getGpuRequiredPinsList(gpu);
    const availablePins = getPsuPciePinsList(psu);
    if (requiredPins === null || availablePins === null) {
      remarks.power_connectors = {
        score: "bad",
        text: "Brak danych o złączach zasilania GPU lub PSU.",
      };
    } else if (requiredPins.length === 0) {
      remarks.power_connectors = {
        score: "good",
        text: "GPU nie wymaga dodatkowego zasilania.",
      };
    } else if (canSatisfyGpuPower(availablePins, requiredPins)) {
      remarks.power_connectors = {
        score: "good",
        text: `Dostępne złącza PCIe: ${formatPinList(availablePins)}, wymagane: ${formatPinList(
          requiredPins
        )}.`,
      };
    } else {
      remarks.power_connectors = {
        score: "bad",
        text: `Za mało złączy PCIe (dostępne ${formatPinList(availablePins)}, wymagane ${formatPinList(
          requiredPins
        )}).`,
      };
    }
  } else {
    remarks.power_connectors = { score: "good", text: "Zasilacz nie został jeszcze wybrany." };
  }

  const cpuMax = getMaxPcieVersionFromCpu(cpu);
  const moboMax = getMaxPcieVersionFromMobo(mobo);
  const gpuVer = getGpuPcieVersion(gpu);
  if (gpuVer !== null || cpuMax !== null || moboMax !== null) {
    const text = buildPcieContextText({ cpuMax, moboMax, gpuVer, storageVer: null });
    const limited =
      (gpuVer !== null && cpuMax !== null && gpuVer > cpuMax) ||
      (gpuVer !== null && moboMax !== null && gpuVer > moboMax);
    remarks.pcie = {
      score: limited ? "ok" : "good",
      text: limited ? `${text} (GPU ograniczona do niższej wersji)` : text,
    };
  }

  return remarks;
};

const generateMotherboardRemarks = (mobo, build) => {
  const remarks = {};
  const cpu = getCpu(build);
  const chassis = getChassis(build);
  const ram = getRam(build);
  const gpu = getGpu(build);
  const storage = getStorage(build);

  if (cpu?.socket && mobo.socket) {
    if (mobo.socket !== cpu.socket) {
      remarks.socket = { score: "bad", text: "Gniazdo plyty nie pasuje do CPU!" };
    } else {
      remarks.socket = { score: "good", text: "Gniazdo plyty jest kompatybilne." };
    }
  } else if (!cpu) {
    remarks.socket = { score: "good", text: "Procesor nie został wybrany." };
  }

  if (chassis?.mobo_form_factor_support && mobo.form_factor) {
    if (!chassis.mobo_form_factor_support.includes(mobo.form_factor)) {
      remarks.form_factor = {
        score: "ok",
        text: `Format plyty (${mobo.form_factor}) moze nie pasowac do obudowy.`,
      };
    }
  }

  const cpuMap = getRamSupportMap(cpu);
  const moboMap = getRamSupportMap(mobo);
  const ramBase = getRamBase(ram);
  const context = buildRamSupportRemarkText({ cpuMap, moboMap, cpu, mobo });
  const typeContext = buildRamTypeRemarkText({ cpuMap, moboMap, cpu, mobo, ramBase });
  const cpuTypes = Array.from(cpuMap.keys());
  const moboTypes = Array.from(moboMap.keys());

  let typeScore = "good";
  if (!moboTypes.length) {
    typeScore = "bad";
  } else if (ramBase?.type) {
    if (!moboTypes.includes(ramBase.type)) {
      typeScore = "bad";
    } else if (cpu && (!cpuTypes.length || !cpuTypes.includes(ramBase.type))) {
      typeScore = "bad";
    }
  } else if (cpu) {
    if (!cpuTypes.length || !cpuTypes.some((item) => moboTypes.includes(item))) {
      typeScore = "bad";
    }
  }

  remarks.ram_type = { score: typeScore, text: typeContext };

  if (ramBase) {
    const cpuMax = getMaxMtsForType(cpuMap, ramBase.type);
    const moboMax = getMaxMtsForType(moboMap, ramBase.type);
    let score = "good";
    if (mobo && moboMax === null) {
      score = "bad";
    } else if (cpu && cpuMax === null) {
      score = "bad";
    } else {
      const limit = cpu ? Math.min(cpuMax ?? Infinity, moboMax ?? Infinity) : moboMax;
      if (limit !== null && ramBase.mts > limit) {
        score = "ok";
      }
    }
    remarks.ram_frequency = {
      score,
      text: `${context}, Wybrany RAM: ${ramBase.mts} MHz`,
    };
  } else {
    remarks.ram_frequency = { score: "good", text: `${context}, RAM: nie wybrany` };
  }

  const cpuMax = getMaxPcieVersionFromCpu(cpu);
  const moboMax = getMaxPcieVersionFromMobo(mobo);
  const gpuVer = getGpuPcieVersion(gpu);
  const storageVer = getStoragePcieVersion(storage);
  if (cpuMax !== null || moboMax !== null || gpuVer !== null || storageVer !== null) {
    const text = buildPcieContextText({ cpuMax, moboMax, gpuVer, storageVer });
    const limited =
      (gpuVer !== null && moboMax !== null && gpuVer > moboMax) ||
      (storageVer !== null && moboMax !== null && storageVer > moboMax);
    remarks.connectors = {
      score: limited ? "ok" : "good",
      text: limited ? `${text} (ograniczenie przez płytę)` : text,
    };
  }

  return remarks;
};

const generatePsuRemarks = (psu, build) => {
  const remarks = {};
  const chassis = getChassis(build);
  const gpu = getGpu(build);

  if (gpu?.recommended_system_power_w) {
    const recommended = toNumber(gpu.recommended_system_power_w);
    const psuWattage = toNumber(psu.wattage);
    let score = "good";
    if (recommended !== null && psuWattage !== null && psuWattage < recommended) {
      score = "bad";
    }
    remarks.wattage = {
      score,
      text: `GPU rekomenduje: ${recommended ?? gpu.recommended_system_power_w} W.`,
    };
  } else if (gpu) {
    remarks.wattage = { score: null, text: "GPU nie podaje rekomendowanej mocy." };
  } else {
    remarks.wattage = { score: "good", text: "Karta graficzna nie została wybrana." };
  }

  if (gpu) {
    const requiredPins = getGpuRequiredPinsList(gpu);
    const availablePins = getPsuPciePinsList(psu);
    if (requiredPins === null || availablePins === null) {
      remarks.connectors = {
        score: "bad",
        text: "Brak danych o złączach zasilania GPU lub PSU.",
      };
    } else if (requiredPins.length === 0) {
      remarks.connectors = {
        score: "good",
        text: "GPU nie wymaga dodatkowego zasilania.",
      };
    } else if (canSatisfyGpuPower(availablePins, requiredPins)) {
      remarks.connectors = {
        score: "good",
        text: `Dostępne złącza PCIe: ${formatPinList(availablePins)}, wymagane: ${formatPinList(
          requiredPins
        )}.`,
      };
    } else {
      remarks.connectors = {
        score: "bad",
        text: `Za mało złączy PCIe (dostępne ${formatPinList(availablePins)}, wymagane ${formatPinList(
          requiredPins
        )}).`,
      };
    }
  } else {
    remarks.connectors = { score: "good", text: "Karta graficzna nie została wybrana." };
  }

  if (chassis?.psu_form_factor_support && psu.form_factor) {
    if (!chassis.psu_form_factor_support.includes(psu.form_factor)) {
      remarks.form_factor = {
        score: "bad",
        text: `Format zasilacza (${psu.form_factor}) nie pasuje do obudowy.`,
      };
    } else {
      remarks.form_factor = { score: "good", text: `Format PSU pasuje do obudowy.` };
    }
  } else if (!chassis) {
    remarks.form_factor = { score: "good", text: "Obudowa nie została wybrana." };
  }

  return remarks;
};

const generateMemRemarks = (mem, build) => {
  const remarks = {};
  const mobo = getMobo(build);
  const cpu = getCpu(build);
  let connectorText = null;
  let connectorScore = null;

  if (mobo) {
    const moboConnectors = Array.isArray(mobo.connectors)
      ? mobo.connectors.map((item) => item?.category).filter(Boolean)
      : [];
    const memConnector = mem.connector?.category || mem.connector?.connector?.category;
    if (memConnector && moboConnectors.length && !moboConnectors.includes(memConnector)) {
      connectorText = `Płyta główna nie posiada złącza ${memConnector}.`;
      connectorScore = "bad";
    }
  }

  const cpuMax = getMaxPcieVersionFromCpu(cpu);
  const moboMax = getMaxPcieVersionFromMobo(mobo);
  const storageVer = getStoragePcieVersion(mem);
  if (storageVer !== null || cpuMax !== null || moboMax !== null) {
    const text = buildPcieContextText({ cpuMax, moboMax, gpuVer: null, storageVer });
    const limited =
      (storageVer !== null && cpuMax !== null && storageVer > cpuMax) ||
      (storageVer !== null && moboMax !== null && storageVer > moboMax);
    const pcieText = limited ? `${text} (SSD ograniczony do niższej wersji)` : text;
    if (connectorText) {
      connectorText = `${connectorText} ${pcieText}`;
      connectorScore = connectorScore || (limited ? "ok" : "good");
    } else {
      connectorText = pcieText;
      connectorScore = limited ? "ok" : "good";
    }
  }

  if (connectorText) {
    remarks.connector = { score: connectorScore || "ok", text: connectorText };
  }

  return remarks;
};

const generateChassisRemarks = (chassis, build) => {
  const remarks = {};
  const mobo = getMobo(build);
  const gpu = getGpu(build);
  const psu = getPsu(build);

  if (mobo?.form_factor) {
    const score = chassis.mobo_form_factor_support?.includes(mobo.form_factor) ? "good" : "bad";
    remarks.mobo_form_factor_support = {
      score,
      text: `Wybrana płyta: ${mobo.form_factor}.`,
    };
  } else {
    remarks.mobo_form_factor_support = {
      score: "good",
      text: "Płyta główna nie została wybrana.",
    };
  }

  if (psu?.form_factor) {
    const score = chassis.psu_form_factor_support?.includes(psu.form_factor) ? "good" : "bad";
    remarks.psu_form_factor_support = {
      score,
      text: `Wybrany zasilacz: ${psu.form_factor}.`,
    };
  } else {
    remarks.psu_form_factor_support = {
      score: "good",
      text: "Zasilacz nie został wybrany.",
    };
  }

  if (gpu?.length_mm) {
    const width = gpu.slot_width ? `${gpu.slot_width} slotu` : "brak danych";
    const score =
      chassis.max_gpu_length_mm && gpu.length_mm > chassis.max_gpu_length_mm ? "bad" : "good";
    remarks.max_gpu_length_mm = {
      score,
      text: `GPU: ${gpu.length_mm}mm, szerokość: ${width}.`,
    };
  } else {
    remarks.max_gpu_length_mm = {
      score: "good",
      text: "Karta graficzna nie została wybrana.",
    };
  }

  return remarks;
};

export const generateRemarksForComponent = (component, componentType, currentBuild) => {
  if (!component) return {};

  switch (componentType) {
    case "cpu":
      return generateCpuRemarks(component, currentBuild);
    case "ram":
      return generateRamRemarks(component, currentBuild);
    case "gpu":
      return generateGpuRemarks(component, currentBuild);
    case "mobo":
      return generateMotherboardRemarks(component, currentBuild);
    case "psu":
      return generatePsuRemarks(component, currentBuild);
    case "mem":
      return generateMemRemarks(component, currentBuild);
    case "chassis":
      return generateChassisRemarks(component, currentBuild);
    default:
      return {};
  }
};
