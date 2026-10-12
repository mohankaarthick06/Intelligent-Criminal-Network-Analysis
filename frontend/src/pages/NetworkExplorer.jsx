import React, { useState, useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import { api } from '../api/client';
import { 
  Network, Filter, ZoomIn, ZoomOut, RefreshCw, 
  MapPin, Phone, Users, Share2, Layers, Search
} from 'lucide-react';

const COMMUNITY_COLORS = [
  '#38bdf8', '#818cf8', '#34d399', '#f472b6', '#fbbf24', 
  '#a78bfa', '#2dd4bf', '#fb7185', '#60a5fa', '#4ade80'
];

export default function NetworkExplorer() {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  const [loading, setLoading] = useState(false);
  const [graphSummary, setGraphSummary] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [allNodesList, setAllNodesList] = useState([]);

  // Filters
  const [minInteractions, setMinInteractions] = useState(1);
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedCallType, setSelectedCallType] = useState('');
  const [maxNodesLimit, setMaxNodesLimit] = useState(150);

  // Link Analysis Tool state
  const [linkSource, setLinkSource] = useState('');
  const [linkTarget, setLinkTarget] = useState('');
  const [linkResult, setLinkResult] = useState(null);
  const [linkLoading, setLinkLoading] = useState(false);

  const fetchAndRenderGraph = async () => {
    setLoading(true);
    try {
      const data = await api.buildGraph({
        min_interactions: minInteractions,
        city: selectedCity || null,
        call_type: selectedCallType || null,
        max_nodes: maxNodesLimit
      });

      setGraphSummary(data.summary);
      setAllNodesList(data.nodes);

      if (data.nodes.length >= 2 && !linkSource && !linkTarget) {
        setLinkSource(data.nodes[0].id);
        setLinkTarget(data.nodes[1].id);
      }

      // Prepare elements for Cytoscape
      const elements = [];
      data.nodes.forEach(n => {
        const color = COMMUNITY_COLORS[n.community % COMMUNITY_COLORS.length];
        elements.push({
          data: {
            id: n.id,
            label: n.id,
            community: n.community,
            color: color,
            city: n.city,
            degree: n.degree,
            degree_centrality: n.degree_centrality,
            betweenness_centrality: n.betweenness_centrality,
            phone: n.phone_number
          }
        });
      });

      data.edges.forEach(e => {
        elements.push({
          data: {
            id: e.id,
            source: e.source,
            target: e.target,
            weight: e.weight,
            duration: e.total_duration_sec,
            call_types: e.call_types.join(', ')
          }
        });
      });

      if (cyRef.current) {
        cyRef.current.destroy();
      }

      if (containerRef.current) {
        const cy = cytoscape({
          container: containerRef.current,
          elements: elements,
          style: [
            {
              selector: 'node',
              style: {
                'background-color': 'data(color)',
                'label': 'data(label)',
                'color': '#cbd5e1',
                'font-size': '10px',
                'font-family': 'Inter, sans-serif',
                'text-valign': 'bottom',
                'text-margin-y': 4,
                'width': 'mapData(degree, 1, 30, 16, 42)',
                'height': 'mapData(degree, 1, 30, 16, 42)',
                'border-width': 2,
                'border-color': '#0f172a'
              }
            },
            {
              selector: 'node:selected',
              style: {
                'border-color': '#ffffff',
                'border-width': 4,
                'shadow-blur': 12,
                'shadow-color': '#38bdf8',
                'shadow-opacity': 0.8
              }
            },
            {
              selector: 'edge',
              style: {
                'width': 'mapData(weight, 1, 10, 1.2, 5)',
                'line-color': '#334155',
                'opacity': 0.65,
                'curve-style': 'bezier'
              }
            },
            {
              selector: 'edge:selected',
              style: {
                'line-color': '#38bdf8',
                'opacity': 1.0,
                'width': 3
              }
            }
          ],
          layout: {
            name: 'cose',
            animate: false,
            nodeOverlap: 20,
            idealEdgeLength: 50,
            nodeRepulsion: 400000
          }
        });

        cy.on('tap', 'node', evt => {
          setSelectedNode(evt.target.data());
          setSelectedEdge(null);
        });

        cy.on('tap', 'edge', evt => {
          setSelectedEdge(evt.target.data());
          setSelectedNode(null);
        });

        cy.on('tap', evt => {
          if (evt.target === cy) {
            setSelectedNode(null);
            setSelectedEdge(null);
          }
        });

        cyRef.current = cy;
      }
    } catch (err) {
      console.error('Error constructing graph:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAndRenderGraph();
    return () => {
      if (cyRef.current) cyRef.current.destroy();
    };
  }, [minInteractions, selectedCity, selectedCallType, maxNodesLimit]);

  const handleZoom = (factor) => {
    if (cyRef.current) {
      const zoom = cyRef.current.zoom();
      cyRef.current.zoom(zoom * factor);
    }
  };

  const handleFit = () => {
    if (cyRef.current) cyRef.current.fit();
  };

  const handleRunLinkAnalysis = async () => {
    if (!linkSource || !linkTarget) return;
    setLinkLoading(true);
    try {
      const res = await api.analyzeLink(linkSource, linkTarget);
      setLinkResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLinkLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Network className="w-6 h-6 text-emerald-400" />
            Communication Graph Network Explorer
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Constructed from CDR call events. Explores Louvain communities, degree centrality, and topology.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchAndRenderGraph}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-dark-800 hover:bg-dark-700 border border-slate-700 text-xs font-medium text-slate-200"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh Layout
          </button>
          <button
            onClick={() => handleZoom(1.2)}
            className="p-1.5 rounded-lg bg-dark-800 hover:bg-dark-700 border border-slate-700 text-slate-300"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleZoom(0.8)}
            className="p-1.5 rounded-lg bg-dark-800 hover:bg-dark-700 border border-slate-700 text-slate-300"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={handleFit}
            className="px-2.5 py-1.5 rounded-lg bg-dark-800 hover:bg-dark-700 border border-slate-700 text-xs font-medium text-slate-300"
          >
            Fit View
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="glass-panel p-4 rounded-xl flex flex-wrap items-center gap-4 text-xs">
        <div className="flex items-center gap-2 text-slate-300">
          <Filter className="w-4 h-4 text-cyan-400" />
          <span className="font-medium">Filters:</span>
        </div>

        {/* Min Interactions */}
        <div className="flex items-center gap-2">
          <span className="text-slate-400">Min Calls:</span>
          <select
            value={minInteractions}
            onChange={e => setMinInteractions(Number(e.target.value))}
            className="bg-dark-900 border border-slate-700 rounded px-2.5 py-1 text-slate-200"
          >
            <option value="1">≥ 1 Call</option>
            <option value="2">≥ 2 Calls</option>
            <option value="3">≥ 3 Calls</option>
            <option value="5">≥ 5 Calls</option>
          </select>
        </div>

        {/* City Filter */}
        <div className="flex items-center gap-2">
          <span className="text-slate-400">City:</span>
          <select
            value={selectedCity}
            onChange={e => setSelectedCity(e.target.value)}
            className="bg-dark-900 border border-slate-700 rounded px-2.5 py-1 text-slate-200"
          >
            <option value="">All Cities</option>
            <option value="Coimbatore">Coimbatore</option>
            <option value="Chennai">Chennai</option>
            <option value="Madurai">Madurai</option>
            <option value="Kochi">Kochi</option>
            <option value="Bengaluru">Bengaluru</option>
            <option value="Hyderabad">Hyderabad</option>
            <option value="Mumbai">Mumbai</option>
          </select>
        </div>

        {/* Call Type */}
        <div className="flex items-center gap-2">
          <span className="text-slate-400">Type:</span>
          <select
            value={selectedCallType}
            onChange={e => setSelectedCallType(e.target.value)}
            className="bg-dark-900 border border-slate-700 rounded px-2.5 py-1 text-slate-200"
          >
            <option value="">All (Voice & SMS)</option>
            <option value="voice">Voice Only</option>
            <option value="sms">SMS Only</option>
          </select>
        </div>

        {/* Max Nodes Limit */}
        <div className="flex items-center gap-2">
          <span className="text-slate-400">Max Render Nodes:</span>
          <select
            value={maxNodesLimit}
            onChange={e => setMaxNodesLimit(Number(e.target.value))}
            className="bg-dark-900 border border-slate-700 rounded px-2.5 py-1 text-slate-200"
          >
            <option value="50">Top 50 Nodes</option>
            <option value="100">Top 100 Nodes</option>
            <option value="150">Top 150 Nodes</option>
            <option value="300">Top 300 Nodes</option>
          </select>
        </div>

        {/* Summary pill */}
        {graphSummary && (
          <div className="ml-auto flex items-center gap-3 text-slate-400">
            <span>Nodes: <strong className="text-white">{graphSummary.node_count}</strong></span>
            <span>Edges: <strong className="text-white">{graphSummary.edge_count}</strong></span>
            <span>Louvain Communities: <strong className="text-cyan-400">{graphSummary.community_count}</strong></span>
          </div>
        )}
      </div>

      {/* Main Canvas & Details Panel Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Graph Canvas (8 cols) */}
        <div className="lg:col-span-8 glass-panel rounded-xl overflow-hidden relative h-[560px] border border-slate-800">
          <div ref={containerRef} className="w-full h-full bg-[#070b12]" />

          {loading && (
            <div className="absolute inset-0 bg-dark-950/70 backdrop-blur-sm flex items-center justify-center">
              <div className="flex items-center gap-2 text-cyan-400 text-sm">
                <RefreshCw className="w-5 h-5 animate-spin" />
                Constructing NetworkX Graph & Louvain Communities...
              </div>
            </div>
          )}

          {/* Canvas Floating Legend */}
          <div className="absolute bottom-3 left-3 bg-dark-900/90 border border-slate-800 p-2.5 rounded-lg text-[10px] text-slate-400 space-y-1">
            <span className="font-semibold text-slate-300 block mb-1">Graph Legend</span>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span> Node size = Degree centrality
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-400"></span> Colors = Louvain community cluster
            </div>
          </div>
        </div>

        {/* Right Inspector & Link Analysis (4 cols) */}
        <div className="lg:col-span-4 space-y-5">
          {/* Selected Item Inspector */}
          <div className="glass-panel p-5 rounded-xl space-y-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              Inspector Panel
            </h3>

            {selectedNode ? (
              <div className="space-y-3 text-xs">
                <div className="p-3 rounded-lg bg-dark-900/80 border border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Selected Individual</span>
                  <p className="text-base font-mono font-bold text-white mt-0.5">{selectedNode.id}</p>
                  <p className="text-slate-400 flex items-center gap-1 mt-1">
                    <Phone className="w-3 h-3 text-cyan-400" /> {selectedNode.phone}
                  </p>
                  <p className="text-slate-400 flex items-center gap-1 mt-1">
                    <MapPin className="w-3 h-3 text-cyan-400" /> {selectedNode.city}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="p-2.5 rounded-lg bg-dark-900/60 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Connections</span>
                    <span className="text-sm font-bold text-white font-mono">{selectedNode.degree}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-dark-900/60 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Community ID</span>
                    <span className="text-sm font-bold text-cyan-300 font-mono">Cluster {selectedNode.community}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-dark-900/60 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Degree Centrality</span>
                    <span className="text-sm font-bold text-indigo-300 font-mono">{selectedNode.degree_centrality}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-dark-900/60 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Betweenness</span>
                    <span className="text-sm font-bold text-emerald-300 font-mono">{selectedNode.betweenness_centrality}</span>
                  </div>
                </div>
              </div>
            ) : selectedEdge ? (
              <div className="space-y-3 text-xs">
                <div className="p-3 rounded-lg bg-dark-900/80 border border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Interaction Channel</span>
                  <p className="text-sm font-mono font-bold text-cyan-300 mt-1">
                    {selectedEdge.source} ↔ {selectedEdge.target}
                  </p>
                </div>
                <div className="space-y-1.5 text-slate-300">
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Total Call Events:</span>
                    <span className="font-mono font-bold text-white">{selectedEdge.weight}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Total Duration:</span>
                    <span className="font-mono text-white">{selectedEdge.duration}s</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-800">
                    <span className="text-slate-400">Mediums:</span>
                    <span className="font-mono text-white uppercase">{selectedEdge.call_types}</span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 py-6 text-center">
                Click on any node or edge in the graph to inspect structural metrics.
              </p>
            )}
          </div>

          {/* Link Prediction & Topological Proximity Tool */}
          <div className="glass-panel p-5 rounded-xl space-y-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Share2 className="w-4 h-4 text-indigo-400" />
              Pairwise Link Analysis
            </h3>
            <p className="text-xs text-slate-400">
              Calculate Common Neighbors, Jaccard similarity, and Adamic-Adar proximity between two entities.
            </p>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-400 block mb-1">Source Node</label>
                  <select
                    value={linkSource}
                    onChange={e => setLinkSource(e.target.value)}
                    className="w-full bg-dark-900 border border-slate-700 rounded px-2 py-1.5 text-white"
                  >
                    {allNodesList.map(n => <option key={n.id} value={n.id}>{n.id}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Target Node</label>
                  <select
                    value={linkTarget}
                    onChange={e => setLinkTarget(e.target.value)}
                    className="w-full bg-dark-900 border border-slate-700 rounded px-2 py-1.5 text-white"
                  >
                    {allNodesList.map(n => <option key={n.id} value={n.id}>{n.id}</option>)}
                  </select>
                </div>
              </div>

              <button
                onClick={handleRunLinkAnalysis}
                disabled={linkLoading || !linkSource || !linkTarget}
                className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition"
              >
                {linkLoading ? 'Computing Topology...' : 'Analyze Connection'}
              </button>

              {linkResult && (
                <div className="mt-3 p-3 rounded-lg bg-dark-900/80 border border-slate-800 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Direct Link:</span>
                    <span className={`font-semibold ${linkResult.direct_edge_exists ? 'text-emerald-400' : 'text-slate-400'}`}>
                      {linkResult.direct_edge_exists ? 'YES' : 'NO'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Common Neighbors:</span>
                    <span className="font-mono text-cyan-300 font-bold">{linkResult.common_neighbors_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Jaccard Coefficient:</span>
                    <span className="font-mono text-white">{linkResult.jaccard_coefficient}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Adamic-Adar Index:</span>
                    <span className="font-mono text-white">{linkResult.adamic_adar_index}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Shortest Path Distance:</span>
                    <span className="font-mono text-indigo-300">
                      {linkResult.shortest_path_distance !== null ? `${linkResult.shortest_path_distance} hops` : 'No path'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
