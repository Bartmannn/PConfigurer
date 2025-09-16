import { useEffect, useState } from "react";

function RAMList() {
    const [rams, setRams] = useState([]);

    useEffect(() => {
        fetch("http://localhost:8000/api/rams/")
            .then((res) => res.json())
            .then((data) => setRams(data));
    }, []);

    return (
        <div>
            <h2>Available RAMs</h2>
            <ul>
                {rams.map((ram) => (
                    <li key={ram.id}>
                        {ram.name}
                    </li>
                ))}
            </ul>
        </div>
    );

}

export default RAMList;
