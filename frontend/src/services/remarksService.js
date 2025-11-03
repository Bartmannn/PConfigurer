const generateCpuRemarks = (cpu, build) => {
  const remarks = {};

  // Socket vs Mobo
  if (build.motherboard) {
    if (cpu.socket === build.motherboard.socket) {
      remarks.socket = { score: 'good', text: "Gniazdo procesora jest kompatybilne." };
    } else {
      remarks.socket = { score: 'bad', text: "Niezgodne gniazdo procesora!" };
    }
  }

  // TDP
  if (cpu.tdp > 120) {
    remarks.tdp = { score: 'ok', text: "Wysokie TDP. Wymagane jest wydajne chłodzenie." };
  }

  return remarks;
};

const generateRamRemarks = (ram, build) => {
  const remarks = {};

  if (build.motherboard) {
    // RAM Type vs Mobo
    if (build.motherboard.supported_ram?.toLowerCase().includes(ram.base.toLowerCase())) {
      remarks.base = { score: 'good', text: "Standard RAM jest kompatybilny." };
    } else {
      remarks.base = { score: 'ok', text: "Standard RAM może nie być w pełni wspierany." };
    }
    // RAM Capacity vs Mobo
    if (ram.total_capacity > build.motherboard.max_ram_capacity) {
      remarks.total_capacity = { score: 'bad', text: `Pojemność RAM przekracza limit płyty (${build.motherboard.max_ram_capacity}GB).` };
    }
  }

  return remarks;
};

const generateGpuRemarks = (gpu, build) => {
    const remarks = {};

    // GPU Length vs Case
    if (build.chassis && gpu.length_mm > build.chassis.max_gpu_length_mm) {
        remarks.length_mm = { score: 'bad', text: `Karta jest za długa do obudowy (max ${build.chassis.max_gpu_length_mm}mm).` };
    }

    // GPU Power vs PSU
    if (build.psu) {
        const estimatedPower = (build.cpu?.tdp || 0) + gpu.tdp + 100;
        if (build.psu.wattage < estimatedPower) {
            remarks.tdp = { score: 'ok', text: `Zasilacz może być za słaby (sugerowane ${estimatedPower}W+).` };
        }
    }

    return remarks;
};

const generateMotherboardRemarks = (mobo, build) => {
    const remarks = {};

    // Mobo Socket vs CPU
    if (build.cpu && mobo.socket !== build.cpu.socket) {
        remarks.socket = { score: 'bad', text: "Gniazdo płyty nie pasuje do CPU!" };
    }

    // Mobo Form Factor vs Case
    if (build.chassis && !build.chassis.mobo_form_factor_support?.includes(mobo.form_factor)) {
        remarks.form_factor = { score: 'ok', text: `Format płyty (${mobo.form_factor}) może nie pasować do obudowy.` };
    }

    return remarks;
};

const generatePsuRemarks = (psu, build) => {
    const remarks = {};

    // PSU Power vs Components
    const requiredPower = (build.cpu?.tdp || 0) + (build.gpu?.tdp || 0) + 100;
    if (psu.wattage < requiredPower) {
        remarks.wattage = { score: 'ok', text: `Moc może być niewystarczająca (sugerowane ${requiredPower}W+).` };
    } else {
        remarks.wattage = { score: 'good', text: `Moc ${psu.wattage}W jest wystarczająca.` };
    }

    // PSU Form Factor vs Case
    if (build.chassis && !build.chassis.psu_form_factor_support?.includes(psu.form_factor)) {
        remarks.form_factor = { score: 'bad', text: `Format zasilacza (${psu.form_factor}) nie pasuje do obudowy.` };
    }

    return remarks;
};

const generateMemRemarks = (mem, build) => {
    const remarks = {};

    // Storage Connector vs Mobo
    if (build.motherboard) {
        const moboConnectors = build.motherboard.connectors.map(c => c.connector.category).join(' ');
        if (!moboConnectors.includes(mem.connector)) {
            remarks.connector = { score: 'bad', text: `Płyta główna nie posiada złącza ${mem.connector}.` };
        }
    }

    return remarks;
};

const generateChassisRemarks = (chassis, build) => {
    const remarks = {};

    // Case Form Factor vs Mobo
    if (build.motherboard && !chassis.mobo_form_factor_support?.includes(build.motherboard.form_factor)) {
        remarks.mobo_form_factor_support = { score: 'bad', text: `Obudowa nie wspiera formatu płyty głównej (${build.motherboard.form_factor}).` };
    }

    // Case GPU Length vs GPU
    if (build.gpu && chassis.max_gpu_length_mm < build.gpu.length_mm) {
        remarks.max_gpu_length_mm = { score: 'bad', text: `Obudowa jest za mała dla wybranej karty graficznej (max ${chassis.max_gpu_length_mm}mm).` };
    }

    // Case PSU Form Factor vs PSU
    if (build.psu && !chassis.psu_form_factor_support?.includes(build.psu.form_factor)) {
        remarks.psu_form_factor_support = { score: 'bad', text: `Obudowa nie wspiera formatu zasilacza (${build.psu.form_factor}).` };
    }

    return remarks;
};


export const generateRemarksForComponent = (component, componentType, currentBuild) => {
  if (!component) return {};

  switch (componentType) {
    case 'cpu':
      return generateCpuRemarks(component, currentBuild);
    case 'ram':
      return generateRamRemarks(component, currentBuild);
    case 'gpu':
      return generateGpuRemarks(component, currentBuild);
    case 'mobo':
      return generateMotherboardRemarks(component, currentBuild);
    case 'psu':
      return generatePsuRemarks(component, currentBuild);
    case 'mem':
      return generateMemRemarks(component, currentBuild);
    case 'chassis':
      return generateChassisRemarks(component, currentBuild);
    default:
      return {};
  }
};
