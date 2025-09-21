import React, { useState } from "react";
import ForceGraph2D from "react-force-graph-2d";


const GraphView = () => {
    const [selectedNode, setSelectedNode] = useState(null);

    const data = {
        nodes: [
            { id: "CPU", label: "CPU", fx: 100, fy: -100 },
            { id: "MOBO", label: "Płyta główna", fx: 0, fy: 0 },
            { id: "RAM", label: "RAM", fx: 100, fy: 100 },
        ],
        links: [
            { source: "CPU", target: "MOBO", color: "gray" },
            { source: "RAM", target: "MOBO", color: "gray" },
            { source: "RAM", target: "CPU", color: "gray" },
        ],
    };

    return (
        <div style={{ display: "flex", height: "100vh" }}>
            {/* panel boczny */}
            <div 
                style={{
                    width: "250px",
                    background: "#242424",
                    borderRight: "1px solid #ccc",
                    padding: "10px"
                }}
            >
                <h3>Panel boczny</h3>
                {selectedNode ? (
                    <p>Wybrano: {selectedNode.label}</p>
                ): (
                    <p>Kliknij węzeł, aby zobaczyć szczegóły</p>
                )}
            </div>

            {/* graf */}
            <div style={{ flexGrow: 1 }}>
                <ForceGraph2D
                    graphData={data}
                    linkWidth={10}
                    nodeRelSize={40}
                    nodeCanvasObject={(node, ctx) => {
                        // okrąg
                        ctx.fillStyle = "lightblue";
                        ctx.beginPath();
                        ctx.arc(node.x, node.y, 40, 0, 2 * Math.PI, false);
                        ctx.fill();
                        ctx.stroke();

                        // nazwa
                        ctx.fillStyle = "black";
                        ctx.font = "12px Sans-Serif";
                        ctx.textAlign = "center";
                        ctx.fillText(node.label, node.x, node.y-4);

                        // +
                        ctx.fillStyle = "darkgreen";
                        ctx.font = "18px Sans-Serif";
                        ctx.fillText("+", node.x, node.y + 16);
                    }}
                    linkColor={(link) => link.color}
                    onNodeClick={(node) => setSelectedNode(node)}
                />
            </div>
        </div>
    );
};

export default GraphView;
