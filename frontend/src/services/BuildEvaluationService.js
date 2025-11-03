// --- Profile: Gaming ---
const gamingRules = [
  // Rule: GPU Power
  (build) => {
    if (!build.gpu) return { score: 0, feedback: 'Brak karty graficznej.' };
    if (build.gpu.tdp >= 200) return { score: 15, feedback: 'Bardzo wydajna karta graficzna, idealna do gier w wysokiej rozdzielczości.' };
    if (build.gpu.tdp >= 120) return { score: 10, feedback: 'Dobra karta graficzna, zapewni płynną rozgrywkę w większości gier.' };
    return { score: -10, feedback: 'Karta graficzna może być niewystarczająca do nowoczesnych gier.' };
  },
  // Rule: RAM Capacity
  (build) => {
    const ramCapacity = build.ram?.total_capacity || 0;
    if (ramCapacity >= 32) return { score: 10, feedback: '32GB RAM to doskonały wybór dla najbardziej wymagających gier i multitaskingu.' };
    if (ramCapacity >= 16) return { score: 8, feedback: '16GB RAM to obecnie standard dla płynnej rozgrywki.' };
    return { score: -5, feedback: 'Poniżej 16GB RAM może powodować problemy z wydajnością w nowszych tytułach.' };
  },
  // Rule: CPU Cores
  (build) => {
    if (!build.cpu) return { score: 0, feedback: 'Brak procesora.' };
    if (build.cpu.cores >= 8) return { score: 10, feedback: 'Procesor z 8 lub więcej rdzeniami to świetny wybór na przyszłość.' };
    if (build.cpu.cores >= 6) return { score: 7, feedback: '6 rdzeni to solidna podstawa do gier.' };
    return { score: -5, feedback: 'Mniej niż 6 rdzeni może ograniczać wydajność w grach procesorowych.' };
  },
];

// --- Profile: Office Work ---
const officeRules = [
  // Rule: Integrated GPU or any GPU
  (build) => {
    if (build.gpu || build.cpu?.integrated_gpu) return { score: 10, feedback: 'Zintegrowana lub dedykowana karta graficzna w zupełności wystarczy do pracy biurowej.' };
    return { score: -15, feedback: 'Brak jakiejkolwiek karty graficznej uniemożliwi wyświetlanie obrazu.' };
  },
  // Rule: RAM Capacity
  (build) => {
    const ramCapacity = build.ram?.total_capacity || 0;
    if (ramCapacity >= 16) return { score: 8, feedback: '16GB RAM zapewni komfortową pracę z wieloma aplikacjami jednocześnie.' };
    if (ramCapacity >= 8) return { score: 5, feedback: '8GB RAM to dobre minimum do płynnej pracy biurowej.' };
    return { score: -5, feedback: 'Poniżej 8GB RAM praca z wieloma kartami w przeglądarce może być utrudniona.' };
  },
  // Rule: Storage Type
  (build) => {
    if (build.storage?.some(s => s.type === 'SSD')) return { score: 10, feedback: 'Dysk SSD znacząco przyspieszy uruchamianie systemu i aplikacji.' };
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
  if (!build || !build.cpu) {
    return [];
  }

  const evaluations = PROFILES.map(profile => {
    let totalScore = 0;
    const feedback = [];

    profile.rules.forEach(rule => {
      const result = rule(build);
      totalScore += result.score;
      if (result.score !== 0) {
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
