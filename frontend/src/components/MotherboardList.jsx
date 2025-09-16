import { useEffect, useState } from "react";

function MotherboardList() {
    const [mobos, setMobos] = useState([]);

    useEffect(() => {
        fetch("http://localhost:8000/api/motherboards/")
            .then((res) => res.json())
            .then((data) => setMobos(data));
    }, []);

    return (
        <div>
            <h2>Available Motherboards</h2>
            <ul>
                {mobos.map((mobo) => (
                    <li key={mobo.id}>
                        {mobo.name}
                    </li>
                ))}
            </ul>
        </div>
    );

}

export default MotherboardList;
