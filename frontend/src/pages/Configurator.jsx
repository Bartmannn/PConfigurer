import CPUList from "../components/CPUList";
import RAMList from "../components/RAMList";
import MotherboardList from "../components/MotherboardList";

function Configurator() {
    return (
        <div>
            <h1>Build Your PC</h1>
            <CPUList />
            <RAMList />
            <MotherboardList />
        </div>
    );
}

export default Configurator;
