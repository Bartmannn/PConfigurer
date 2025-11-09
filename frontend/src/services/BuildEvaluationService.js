// --- Profile: Gaming ---
const gamingRules = [
  // Gateway Rule: Checks for a capable GPU, which is essential for gaming.
  (build) => {
    const gpuScore = build.gpu?.graphics_chip?.tier_score;
    if (build.gpu && gpuScore > 3) {
        return { score: 15, feedback: 'Posiadasz dedykowaną kartę graficzną odpowiednią do gier.' };
    }
    if (build.gpu && gpuScore <= 3) {
        return { score: -20, feedback: `Twoja karta graficzna (Tier ${gpuScore}) jest zbyt słaba do komfortowej gry w nowe tytuły.` };
    }
    if (!build.gpu && build.cpu?.integrated_gpu) {
        return { score: -100, feedback: 'Zintegrowany układ graficzny nie nadaje się do nowoczesnych gier.' };
    }
    if (!build.gpu && !build.cpu?.integrated_gpu) {
        return { score: -200, feedback: 'Brak jakiejkolwiek karty graficznej. Zestaw nie jest gotowy do gier.' };
    }
    return { score: 0, feedback: '' };
  },
  // Rule: RAM Capacity
  (build) => {
    if (!build.ram) return { score: 0, feedback: '' };
    const ramCapacity = build.ram.total_capacity || 0;
    if (ramCapacity >= 32) return { score: 10, feedback: '32GB RAM to doskonały wybór dla najbardziej wymagających gier i multitaskingu.' };
    if (ramCapacity >= 16) return { score: 8, feedback: '16GB RAM to obecnie standard dla płynnej rozgrywki.' };
    return { score: -5, feedback: 'Poniżej 16GB RAM może powodować problemy z wydajnością w nowszych tytułach.' };
  },
  // Rule: CPU Cores - Note: This is a simplified check. The main logic is in the tier_score.
  (build) => {
    if (!build.cpu) return { score: 0, feedback: '' };
    const coreCount = build.cpu.p_cores || 0;
    if (coreCount >= 8) return { score: 10, feedback: 'Procesor z 8 lub więcej rdzeniami P-Core to świetny wybór na przyszłość.' };
    if (coreCount >= 6) return { score: 7, feedback: '6 rdzeni P-Core to solidna podstawa do gier.' };
    return { score: -5, feedback: 'Mniej niż 6 rdzeni P-Core może ograniczać wydajność w grach procesorowych.' };
  },
  // Rule: CPU-GPU Synergy (Bottleneck)
  (build) => {
    const cpuScore = build.cpu?.tier_score;
    const gpuScore = build.gpu?.graphics_chip?.tier_score;

    // A score of 0 is a valid, low-end score, so we check for undefined.
    if (cpuScore === undefined || gpuScore === undefined) {
      return { score: 0, feedback: "" }; // Cannot evaluate
    }

    const tierDifference = Math.abs(cpuScore - gpuScore);
    const THRESHOLD = 2; // Allow a difference of up to 2 tier points.

    if (tierDifference > THRESHOLD) {
      if (cpuScore > gpuScore) {
        return {
          score: 2, // This is a typical gaming setup, not a penalty.
          feedback:
            `Procesor (Tier ${cpuScore}) ma zapas mocy w stosunku do karty graficznej (Tier ${gpuScore}). W grach to GPU będzie w pełni wykorzystywane.`,
        };
      } else {
        return {
          score: -8,
          feedback:
            `Karta graficzna (Tier ${gpuScore}) jest znacznie wydajniejsza niż procesor (Tier ${cpuScore}). W grach procesor może stanowić 'wąskie gardło', ograniczając potencjał GPU.`,
        };
      }
    }

    return {
      score: 5,
      feedback:
        `Procesor (Tier ${cpuScore}) i karta graficzna (Tier ${gpuScore}) są dobrze zbalansowane pod względem wydajności.`,
    };
  },
  // Rule: Storage Type
  (build) => {
    if (!build.storage) return { score: 0, feedback: '' };
    if (build.storage.type === 'NVMe') return { score: 5, feedback: 'Dysk NVMe zapewnia najszybsze czasy ładowania gier.' };
    if (build.storage.type === 'SATA') return { score: 2, feedback: 'Dysk SSD (SATA) to solidna podstawa, ale dyski NVMe są znacznie szybsze.' };
    return { score: 0, feedback: '' };
  },
  // Rule: Storage Capacity
  (build) => {
    if (!build.storage) return { score: 0, feedback: '' };
    const capacity = build.storage.capacity_gb || 0;
    if (capacity >= 2000) return { score: 5, feedback: '2TB lub więcej to komfortowa przestrzeń na dużą bibliotekę gier.' };
    if (capacity >= 1000) return { score: 3, feedback: '1TB to dobry punkt startowy na system i kilka ulubionych gier.' };
    return { score: 0, feedback: '' };
  },
];

// --- Profile: Office Work ---
const officeRules = [
  // Rule: Checks for any form of graphics output.
  (build) => {
    if (build.gpu || build.cpu?.integrated_gpu) return { score: 10, feedback: 'Zintegrowana lub dedykowana karta graficzna w zupełności wystarczy do pracy biurowej.' };
    return { score: -15, feedback: 'Brak jakiejkolwiek karty graficznej uniemożliwi wyświetlanie obrazu.' };
  },
  // Rule: Bonus for using only integrated GPU, which is cost-effective for office work.
  (build) => {
    if (build.cpu?.integrated_gpu && !build.gpu) {
        return { score: 5, feedback: 'Zintegrowany układ graficzny jest idealnym i oszczędnym rozwiązaniem do pracy biurowej.' };
    }
    return { score: 0, feedback: '' };
  },
  // Rule: RAM Capacity
  (build) => {
    if (!build.ram) return { score: 0, feedback: '' };
    const ramCapacity = build.ram.total_capacity || 0;
    if (ramCapacity >= 16) return { score: 8, feedback: '16GB RAM lub więcej zapewni komfortową pracę z wieloma aplikacjami jednocześnie.' };
    if (ramCapacity >= 8) return { score: 5, feedback: '8GB RAM to dobre minimum do płynnej pracy biurowej.' };
    return { score: -5, feedback: 'Poniżej 8GB RAM praca z wieloma kartami w przeglądarce może być utrudniona.' };
  },
  // Rule: Storage Type
  (build) => {
    if (build.storage?.type === 'NVMe' || build.storage?.type === 'SATA') return { score: 10, feedback: 'Dysk SSD znacząco przyspieszy uruchamianie systemu i aplikacji.' };
    return { score: 0, feedback: 'Rozważ dodanie dysku SSD dla znacznej poprawy komfortu pracy.' };
  },
];


const PROFILES = [
  {
    id: 'gaming',
    name: 'Gaming',
    description: 'Zestaw przeznaczony do uruchamiania gier komputerowych.',
    rules: gamingRules,
  },
  {
    id: 'office',
    name: 'Praca Biurowa',
    description: 'Zestaw do codziennych zadań, pracy z dokumentami i przeglądania internetu.',
    rules: officeRules,
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
      if (result && result.score !== 0 && result.feedback) {
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
