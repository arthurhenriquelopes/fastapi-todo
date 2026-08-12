import React, { useState, useCallback, useMemo } from 'react';
import { ReactFlow, addEdge, Background, Controls, applyNodeChanges, applyEdgeChanges } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { PromptNode } from './nodes/PromptNode';

const nodeTypes = {
  promptNode: PromptNode,
};

const initialNodes = [
  {
    id: '1',
    type: 'promptNode',
    position: { x: 250, y: 100 },
    data: { id: '1', prompt: 'Is this a support request?' },
  },
];

export default function App() {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState([]);

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({ ...params, type: 'smoothstep', animated: true }, eds)),
    []
  );

  const handlePromptChange = (id, newPrompt) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === id) {
          node.data = { ...node.data, prompt: newPrompt };
        }
        return node;
      })
    );
  };

  const nodesWithHandler = useMemo(() => {
    return nodes.map((n) => ({
      ...n,
      data: { ...n.data, onChange: handlePromptChange },
    }));
  }, [nodes]);

  const addNode = () => {
    const newNode = {
      id: (nodes.length + 1).toString(),
      type: 'promptNode',
      position: { x: 250 + Math.random() * 100, y: 250 + Math.random() * 100 },
      data: { id: (nodes.length + 1).toString(), prompt: 'New decision?' },
    };
    setNodes((nds) => nds.concat(newNode));
  };

  const runFlow = async () => {
    const graphDict = {};
    nodes.forEach(n => {
      const yesEdge = edges.find(e => e.source === n.id && e.sourceHandle === 'yes');
      const noEdge = edges.find(e => e.source === n.id && e.sourceHandle === 'no');
      
      graphDict[n.id] = {
        prompt: n.data.prompt,
        yes_path: yesEdge ? yesEdge.target : null,
        no_path: noEdge ? noEdge.target : null,
      };
    });

    const startNodeId = '1';

    console.log({ nodes: graphDict, start_node_id: startNodeId });
    
    try {
      await fetch('http://localhost:8000/api/flow/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nodes: graphDict, start_node_id: startNodeId })
      });
      alert('Flow triggered successfully! Check backend terminal for Inngest step logs.');
    } catch (err) {
      alert('Failed to trigger flow. Make sure backend is running and CORS is allowed.');
    }
  };

  return (
    <div className="w-screen h-screen flex flex-col">
      <header className="bg-slate-900 text-white p-4 flex justify-between items-center shadow-md">
        <h1 className="text-xl font-bold">AI Decision Flow</h1>
        <div className="space-x-2">
          <button onClick={addNode} className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded">
            + Add Node
          </button>
          <button onClick={runFlow} className="bg-green-600 hover:bg-green-500 px-4 py-2 rounded font-bold">
            ▶ Run Flow
          </button>
        </div>
      </header>
      <div className="flex-grow bg-slate-50 relative">
        <ReactFlow
          nodes={nodesWithHandler}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}
