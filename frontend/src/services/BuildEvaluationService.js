const officeRules = [
  (build) => { // biuro - GPU
    if (!build.gpu && build.cpu?.integrated_gpu) return { score: 10, feedback: '' };
    if (build.gpu && build.cpu?.integrated_gpu) return { score: -5, feedback: 'Nie potrzebujesz dedykowanej karty graficznej, masz ją zintegrowaną w procesorze.' };
    
    const gpu_tier_score = build.gpu?.graphics_chip.tier_score || 0;
    
    if (gpu_tier_score <= 1) return { score: 5, feedback: '' };
    if (gpu_tier_score < 4) return { score: -5, feedback: 'Przepłacasz na karcie grafiki.' };
    if (gpu_tier_score >= 4) return { score: -10, feedback: 'Ta grafika nie jest do biura!' };

    return { score: 0, feedback: 'Wybierz dedykowaną kartę grafiki lub procesor ze zinstegrowaną grafiką.' };
  },
  (build) => { // biuro - RAM
    if (!build.ram || build.ram?.length == 0) return { score: 0, feedback: 'Wybierz pamięć RAM.' };

    const ramCapacity = build.ram.total_capacity || 0;

    if (ramCapacity < 8) return { score: -10, feedback: 'Mniej niż 8GB RAM\'u nie ma sensu!' };
    if (ramCapacity == 8) return { score: -5, feedback: '8GB RAM to teraz za mało.' };
    if (ramCapacity < 16) return { score: 5, feedback: 'Niecałe 16GB RAM może okazać się niewystarczające.' };
    if (ramCapacity == 16) return { score: 10, feedback: '' };
    return { score: -5, feedback: 'Ponad 16GB RAM\'u jest niepotrzebnym wydatkiem!' };
  },
  (build) => { // biuro - CPU
    if (!build.cpu) return { score: 0, feedback: 'Wybierz procesor.' };
    
    const cpu_tier_score = build.cpu?.tier_score;

    if (cpu_tier_score <= 3 || cpu_tier_score == 7) return { score: 5, feedback: '' };
    if (cpu_tier_score == 4 || cpu_tier_score == 6) return { score: 10, feedback: '' };
    if (cpu_tier_score == 5) return { score: 15, feedback: '' };

    return { score: -5, feedback: 'Przepłacasz na procesorze.'};
  },
  (build) => { // biuro - Pamięć (typ)
    if (!build.mem) return { score: 0, feedback: 'Wybierz dysk.' };
    if (build.mem?.type === 'NVMe') return { score: 10, feedback: '' };
    if (build.mem?.type === 'SATA') return { score: 5, feedback: '' };
    return { score: -5, feedback: 'Dysk HDD jest zbyt powolny na dzisiejsze standardy.' };
  },
  (build) => { // biuro - Pamięć (pojemność)
    if (!build.mem) return { score: 0, feedback: 'Wybierz dysk.' };
    if (build.mem?.capacity_gb < 500) return { score: -5, feedback: 'Mniej niż 500GB na dysku może okazać się niewystarczające.' };
    if (build.mem?.capacity_gb <= 1000) return { score: 5, feedback: '' };
    return { score: -5, feedback: 'Ponad 1TB (1000GB) jest niepotrzebny.' };
  },
];

const gamingRules = [
  (build) => { // gry - GPU
    if (!build.gpu) return { score: 0, feedback: 'Wybierz kartę grafiki.' }

    const gpuScore = build.gpu?.graphics_chip?.tier_score;
    if (gpuScore <= 2) return { score: 0, feedback: 'Wybrana karta grafiki może okazać się za słaba.' }
    if (gpuScore == 3 || gpuScore >= 8) return { score: 5, feedback: '' }
    if (gpuScore <= 5 || gpuScore == 7) return { score: 10, feedback: '' }
    
    return { score: 15, feedback: '' }
  },
  (build) => { // gry - RAM
    if (!build.ram || build.ram?.length == 0) return { score: 0, feedback: 'Wybierz pamięć RAM.' };

    const ramCapacity = build.ram.total_capacity || 0;

    if (ramCapacity < 8) return { score: -10, feedback: 'Mniej niż 8GB RAM\'u nie nadaje się do gier!' };
    if (ramCapacity == 8) return { score: -5, feedback: '8GB RAM to teraz za mało.' };
    if (ramCapacity < 16) return { score: 0, feedback: 'Niecałe 16GB RAM może okazać się niewystarczające.' };
    if (ramCapacity == 16) return { score: 5, feedback: '' };
    if (ramCapacity > 16) return { score: 8, feedback: '' };
    if (ramCapacity == 32) return { score: 10, feedback: '' };

    return { score: -5, feedback: 'Ponad 32GB RAM\'u jest niepotrzebnym wydatkiem!' };
  },
  (build) => { // gry - CPU
    if (!build.cpu) return { score: 0, feedback: 'Wybierz procesor.' };

    const cpuTier = build.cpu?.tier_score;
    
    if (cpuTier <= 2) return { score: 0, feedback: 'Wybrany procesor może okazać się niewystarczający.' };
    if (cpuTier <= 4 || cpuTier == 8) return { score: 5, feedback: '' };
    if (cpuTier == 5 || cpuTier == 7) return { score: 10, feedback: ''};
    if (cpuTier == 6) return { score: 15, feedback: '' };
    
    return { score: -5, feedback: 'Nie potrzebujesz tak dobrego procesora.' };
  },
  (build) => { // gry - bottleneck
    if (!build.cpu || !build.gpu) return { score: 0, feedback: '' };

    const cpuTier = build.cpu?.tier_score;
    const gpuTier = build.gpu?.graphics_chip?.tier_score;
    const diff = Math.abs(cpuTier - gpuTier);

    if (diff >= 5 && cpuTier > gpuTier) return { score: -15, feedback: 'Wybrany procesor jest zbyt potężny dla tej karty grafiki!' };
    if (diff >= 5 && cpuTier < gpuTier) return { score: -15, feedback: 'Wybrana karta graficzna jest zbyt potężna dla tego procesora!' };
    if (diff == 4 && cpuTier > gpuTier) return { score: -5, feedback: 'Wybrany procesor jest za dobry dla tej grafiki.' };
    if (diff == 4 && cpuTier < gpuTier) return { score: -5, feedback: 'Wybrana grafika jest za dobra dla tego procesora. '};
    if (diff == 3 && cpuTier > gpuTier) return { score: 0, feedback: 'Grafika może spowalniać procesor.' };
    if (diff == 3 && cpuTier < gpuTier) return { score: 0, feedback: 'Procesor może spowalniać grafikę.' };
    if (diff == 2) return { score: 5, feedback: '' };
    if (diff == 1) return { score: 10, feedback: '' };

    return { score: 15, feedback: '' };
  },
  (build) => { // gry - Pamięć (typ)
    if (!build.mem) return { score: 0, feedback: 'Wybierz dysk.' };
    if (build.mem?.type === 'NVMe') return { score: 10, feedback: '' };
    if (build.mem?.type === 'SATA') return { score: 0, feedback: 'Dysk SSD może być niewystarczająco szybki do gier.' };
    return { score: -10, feedback: 'Dysk HDD jest zbyt powolny do gier.' };
  },
  (build) => { // gry - Pamięć (pojemność)
    if (!build.mem) return { score: 0, feedback: '' };

    if (build.mem?.capacity_gb < 1000) return { score: -5, feedback: 'Mniej niż 1000GB (1TB) na dysku to za mało.' };
    if (build.mem?.capacity_gb == 1000) return { score: 0, feedback: '1000GB (1TB) może nie wystarczyć.' };
    if (build.mem?.capacity_gb <= 2000) return { score: 10, feedback: '' };
    return { score: -5, feedback: 'Ponad 2TB (2000GB) jest niepotrzebne.' };
  },
];

const professionalRules = [
  (build) => { // profesjonalia - GPU
    if (!build.gpu) return { score: 0, feedback: 'Wybierz kartę graficzną.' };

    const gpuScore = build.gpu?.graphics_chip?.tier_score;
    if (gpuScore <= 2) return { score: -5, feedback: 'Wybrana karta grafiki jest za słaba.' }
    if (gpuScore <= 4) return { score: 0, feedback: 'Wybrana karta graficzna może okazać się zbyt słaba.' }
    if (gpuScore <= 6) return { score: 5, feedback: '' }
    if (gpuScore <= 8) return { score: 10, feedback: '' }
    
    return { score: 15, feedback: '' }
  },
  (build) => { // profesjonalia - RAM
    if (!build.ram || build.ram?.length == 0) return { score: 0, feedback: 'Wybierz pamięć RAM.' };

    const ramCapacity = build.ram.total_capacity || 0;

    if (ramCapacity < 16) return { score: -15, feedback: 'Niecałe 16GB RAM, to zdecydowanie za mało!' };
    if (ramCapacity < 32) return { score: -5, feedback: 'Niecałe 32GB RAM, może okazać się niewystarczające.' };
    if (ramCapacity == 32) return { score: 5, feedback: '' };
    if (ramCapacity <= 64) return { score: 10, feedback: '' };

    return { score: 15, feedback: '' };
  },
  (build) => { // profesjonalia - CPU
    if (!build.cpu) return { score: 0, feedback: 'Wybierz procesor.' };

    const cpuTier = build.cpu?.tier_score;
    
    if (cpuTier <= 4) return { score: 0, feedback: 'Wybrany procesor jest zbyt słaby!' };
    if (cpuTier <= 6) return { score: 5, feedback: '' };
    if (cpuTier <= 8) return { score: 10, feedback: ''};
    
    return { score: 15, feedback: '' };
  },
  (build) => { // profesjonalia - bottleneck
    if (!build.cpu || !build.gpu) return { score: 0, feedback: '' };

    const cpuTier = build.cpu?.tier_score;
    const gpuTier = build.gpu?.graphics_chip?.tier_score;
    const diff = Math.abs(cpuTier - gpuTier);

    if (diff >= 5 && cpuTier > gpuTier) return { score: -15, feedback: 'Wybrany procesor jest zbyt potężny dla tej karty grafiki!' };
    if (diff >= 5 && cpuTier < gpuTier) return { score: -15, feedback: 'Wybrana karta graficzna jest zbyt potężna dla tego procesora!' };
    if (diff == 4 && cpuTier > gpuTier) return { score: -5, feedback: 'Wybrany procesor jest za dobry dla tej grafiki.' };
    if (diff == 4 && cpuTier < gpuTier) return { score: -5, feedback: 'Wybrana grafika jest za dobra dla tego procesora. '};
    if (diff == 3 && cpuTier > gpuTier) return { score: 0, feedback: 'Grafika może spowalniać procesor.' };
    if (diff == 3 && cpuTier < gpuTier) return { score: 0, feedback: 'Procesor może spowalniać grafikę.' };
    if (diff == 2) return { score: 5, feedback: '' };
    if (diff == 1) return { score: 10, feedback: '' };

    return { score: 15, feedback: '' };
  },
  (build) => { // profesjonalia - Pamięć (typ)
    if (!build.mem) return { score: 0, feedback: 'Wybierz dysk.' };
    if (build.mem?.type === 'NVMe') return { score: 10, feedback: '' };
    if (build.mem?.type === 'SATA') return { score: -5, feedback: 'Dysk SSD się tutaj nie nadaje.' };
    return { score: -15, feedback: 'Dysk HDD się tutaj nie nadaje.' };
  },
  (build) => { // profesjonalia - Pamięć (pojemność)
    if (!build.mem) return { score: 0, feedback: 'Wybierz dysk.' };

    if (build.mem?.capacity_gb < 2000) return { score: -10, feedback: 'Mniej niż 2000GB (2TB) na dysku to zdecydowanie za mało.' };
    if (build.mem?.capacity_gb < 4000) return { score: 0, feedback: 'Mniej niż 4000GB (4TB) może nie wystarczyć.' };
    return { score: 10, feedback: '' };
  },
];

const PROFILES = [
  {
    id: 'gaming',
    name: 'Gry komputerowe',
    description: 'Zestaw przeznaczony do uruchamiania gier komputerowych.',
    rules: gamingRules,
  },
  {
    id: 'office',
    name: 'Praca Biurowa',
    description: 'Zestaw do codziennych zadań, pracy z dokumentami i przeglądania internetu.',
    rules: officeRules,
  },
  {
    id: 'professional',
    name: 'Zestaw profesjonalny',
    description: 'Zestaw przeznaczony dla pracy z grafiką komputerową i innych zadań specjalnych.',
    rules: professionalRules,
  },
];

export const evaluateBuild = (build) => {
  // Run evaluation if the build object exists and has at least one component selected.
  if (!build || Object.values(build).every(v => v === null || (Array.isArray(v) && v.length === 0))) {
    return [{
      id: 'no_build',
      name: 'Rozpocznij budowę',
      description: 'Wybierz komponenty, aby ocenić ich przeznaczenie.',
      feedback: ['Wybierz dowolny komponent, aby rozpocząć ocenę zestawu.'],
      totalScore: 0,
    }];
  }

  const evaluations = PROFILES.map(profile => {
    let totalScore = 0;
    const feedback = [];

    profile.rules.forEach(rule => {
      const result = rule(build);
      if (result && (result.score !== 0 || result.feedback)) {
        totalScore += result.score;
        feedback.push(result.feedback);
      }
    });

    return {
      ...profile,
      totalScore,
      feedback,
    };
  });

  return evaluations.sort((a, b) => b.totalScore - a.totalScore);
};
