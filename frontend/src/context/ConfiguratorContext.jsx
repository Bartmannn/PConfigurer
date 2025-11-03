import React, { createContext, useState } from 'react';

export const ConfiguratorContext = createContext();

export const ConfiguratorProvider = ({ children }) => {
  const [currentBuild, setCurrentBuild] = useState({
    cpu: null,
    motherboard: null,
    ram: [],
    gpu: null,
    psu: null,
    case: null,
    storage: [],
  });

  const updateBuild = (componentType, component) => {
    setCurrentBuild(prevBuild => ({
      ...prevBuild,
      [componentType]: component,
    }));
  };

  return (
    <ConfiguratorContext.Provider value={{ currentBuild, updateBuild }}>
      {children}
    </ConfiguratorContext.Provider>
  );
};
