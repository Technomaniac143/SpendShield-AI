import React, { useState, useCallback } from 'react';
import { 
  ReactFlow, 
  MiniMap, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState,
  Panel
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { graphData } from '../mocks/graph';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { RiskScore } from '../components/common/RiskScore';
import { Search, Filter, Maximize, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function ProcurementGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState(graphData.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(graphData.edges);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const navigate = useNavigate();

  const onNodeClick = useCallback((event: React.MouseEvent, node: any) => {
    setSelectedNode(node);
  }, []);

  const closePanel = () => setSelectedNode(null);

  const handleInvestigate = () => {
    if (selectedNode) {
      if (selectedNode.type === 'supplier') {
        navigate(`/suppliers/${selectedNode.id}`);
      } else if (selectedNode.type === 'invoice' || selectedNode.type === 'po') {
        navigate(`/transactions/${selectedNode.id}`);
      } else {
        navigate(`/investigations/new?target=${selectedNode.id}`);
      }
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-6 pb-0 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Procurement Intelligence Graph</h1>
          <p className="mt-1 text-sm text-slate-500">Explore entity relationships, shared risks, and hidden dependencies.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search nodes..." 
              className="pl-9 pr-4 py-2 border border-slate-300 rounded-md text-sm focus:ring-info focus:border-info w-64"
            />
          </div>
          <Button variant="outline" icon={Filter}>Filter</Button>
        </div>
      </div>

      <div className="flex-1 p-6 relative">
        <div className="h-full w-full bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden flex relative">
          
          <div className="flex-1 h-full">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              fitView
              attributionPosition="bottom-right"
            >
              <Background color="#cbd5e1" gap={16} />
              <Controls />
              <MiniMap 
                nodeStrokeColor={(n) => {
                  if (n.data?.risk > 80) return '#ef4444';
                  if (n.data?.risk > 50) return '#f59e0b';
                  return '#10b981';
                }}
                nodeColor={(n) => {
                  return '#fff';
                }}
              />
              <Panel position="top-left" className="bg-white/90 p-2 rounded shadow-sm border border-slate-200 backdrop-blur text-xs text-slate-600">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1"><div className="w-3 h-3 bg-white border-2 border-risk rounded-full"></div> Critical Risk</div>
                  <div className="flex items-center gap-1"><div className="w-3 h-3 bg-white border-2 border-warning rounded-full"></div> Warning</div>
                  <div className="flex items-center gap-1"><div className="w-3 h-3 bg-white border-2 border-safe rounded-full"></div> Safe</div>
                </div>
              </Panel>
            </ReactFlow>
          </div>

          {/* Side Panel for Selected Node */}
          {selectedNode && (
            <div className="absolute right-0 top-0 bottom-0 w-80 bg-white border-l border-slate-200 shadow-xl z-10 flex flex-col transform transition-transform">
              <div className="p-4 border-b border-slate-200 flex justify-between items-start">
                <div>
                  <div className="text-xs font-semibold text-info uppercase tracking-wider mb-1">{selectedNode.data.type}</div>
                  <h3 className="text-lg font-bold text-slate-900">{selectedNode.data.label}</h3>
                  <p className="text-xs text-slate-500 mt-0.5">ID: {selectedNode.id}</p>
                </div>
                <button onClick={closePanel} className="text-slate-400 hover:text-slate-600">
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="p-4 flex-1 overflow-y-auto space-y-6">
                <div>
                  <p className="text-sm font-medium text-slate-500 mb-2">Entity Risk Score</p>
                  <RiskScore score={selectedNode.data.risk} size="lg" />
                </div>
                
                {selectedNode.data.risk > 80 && (
                  <div className="bg-risk-light text-risk-dark p-3 rounded-md text-sm border border-risk/20">
                    <span className="font-bold flex items-center gap-1"><AlertCircle className="h-4 w-4" /> Relationship Risk Signal</span>
                    <p className="mt-1 opacity-90">This entity shares high-risk signals with connected nodes. Manual investigation recommended.</p>
                  </div>
                )}
                
                <div className="pt-4 border-t border-slate-100">
                  <h4 className="text-sm font-semibold text-slate-900 mb-3">Connected Entities</h4>
                  <ul className="space-y-2 text-sm">
                    {edges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id).map(edge => {
                      const isSource = edge.source === selectedNode.id;
                      const connectedNodeId = isSource ? edge.target : edge.source;
                      const connectedNode = nodes.find(n => n.id === connectedNodeId);
                      
                      return (
                        <li key={edge.id} className="flex items-center justify-between p-2 bg-slate-50 rounded">
                          <span className="truncate pr-2">{connectedNode?.data.label}</span>
                          <span className="text-xs font-medium px-1.5 py-0.5 bg-slate-200 text-slate-700 rounded whitespace-nowrap">
                            {edge.type}
                          </span>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              </div>
              
              <div className="p-4 border-t border-slate-200 bg-slate-50">
                <Button className="w-full" onClick={handleInvestigate}>Investigate Entity</Button>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

function AlertCircle(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" x2="12" y1="8" y2="12" />
      <line x1="12" x2="12.01" y1="16" y2="16" />
    </svg>
  )
}
