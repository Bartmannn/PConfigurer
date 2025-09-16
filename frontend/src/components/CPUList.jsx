import { useEffect, useState } from "react";

function CPUList() {
    const [cpus, setCpus] = useState([]);

    useEffect(() => {
        fetch("http://127.0.0.1:8000/api/cpus/")
            .then((res) => res.json())
            .then((data) => setCpus(data));
    }, []);

    return (
        <div>
            <h2>Available CPUs</h2>
            <ul>
                {cpus.map((cpu) => (
                    <li key={cpu.id}>
                        {cpu.name} - {cpu.cores} cores / {cpu.threads} threads
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default CPUList;
