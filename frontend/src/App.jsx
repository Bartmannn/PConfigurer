import ConfiguratorLayout from "./vertical-components/ConfiguratorLayout";

function App() {
  return (
    <div 
      style={{ 
        background: "#1e1e1e", 
        color: "white", 
        height: "100vh", 
        overflow: "hidden" // 🔒 blokada scrolla
      }}
    >
      <ConfiguratorLayout />
    </div>
  );
}

export default App;
