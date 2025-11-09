import { useContext, useEffect, useState } from 'react';
import { ConfiguratorContext } from '../context/ConfiguratorContext';
import { evaluateBuild } from '../services/BuildEvaluationService';
import './BuildEvaluation.css';

function BuildEvaluation() {
  const { currentBuild } = useContext(ConfiguratorContext);
  const [evaluation, setEvaluation] = useState([]);

  useEffect(() => {
    const results = evaluateBuild(currentBuild);
    setEvaluation(results);
  }, [currentBuild]);
  
  if (!evaluation.length || !evaluation[0]) {
    return null; // Nie pokazuj nic, jeśli nie ma oceny
  }

  const topProfile = evaluation[0];

  return (
    <div className="build-evaluation-box">
      <h4>Sugerowane przeznaczenie</h4>
      <p className="top-profile-name">{topProfile.name}</p>
      <ul className="feedback-list">
        {topProfile.feedback.filter(fb => fb).map((fb, index) => (
          <li key={index}>{fb}</li>
        ))}
      </ul>
    </div>
  );
}

export default BuildEvaluation;
