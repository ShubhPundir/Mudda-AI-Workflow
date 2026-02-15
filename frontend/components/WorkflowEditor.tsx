"use client";

import React, { useState, useCallback, useEffect, useRef } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    addEdge,
    MarkerType,
    Node,
    Edge,
    Connection,
    BackgroundVariant,
    Position,
    ReactFlowInstance,
    Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import { Save, RefreshCw, Search, X, ChevronRight, ChevronLeft, Trash2, Box, AlertTriangle, GitBranch, Puzzle } from 'lucide-react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import StepDetailsModal from './StepDetailsModal';
import { Workflow, WorkflowStep, Component } from '@/lib/type';

const nodeWidth = 250;
const nodeHeight = 150;

// Auto-layout using dagre
const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'LR') => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));

    dagreGraph.setGraph({ rankdir: direction });

    nodes.forEach((node) => {
        dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });

    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    nodes.forEach((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        node.targetPosition = direction === 'LR' ? Position.Left : Position.Top;
        node.sourcePosition = direction === 'LR' ? Position.Right : Position.Bottom;

        node.position = {
            x: nodeWithPosition.x - nodeWidth / 2,
            y: nodeWithPosition.y - nodeHeight / 2,
        };

        return node;
    });

    return { nodes, edges };
};

interface WorkflowEditorProps {
    workflowId: string;
}

const WorkflowEditor = ({ workflowId }: WorkflowEditorProps) => {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [workflow, setWorkflow] = useState<Workflow | null>(null);
    const [components, setComponents] = useState<Component[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [isLibOpen, setIsLibOpen] = useState(true);
    const [selectedStep, setSelectedStep] = useState<WorkflowStep | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [validationError, setValidationError] = useState<string | null>(null);
    const reactFlowWrapper = useRef<HTMLDivElement>(null);
    const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
    const router = useRouter();

    // Context Menu State
    const [menu, setMenu] = useState<{ id: string; top: number; left: number } | null>(null);
    const [connectingSource, setConnectingSource] = useState<string | null>(null);

    const fetchWorkflow = useCallback(async () => {
        try {
            const response = await axios.get(`http://localhost:8081/workflows/${workflowId}`);
            const wf = response.data;
            setWorkflow(wf);

            const initialNodes = wf.workflow_plan.steps.map((step: WorkflowStep) => ({
                id: step.step_id,
                type: 'default',
                data: {
                    label: (
                        <div className="p-3 border rounded-xl bg-white shadow-sm min-w-[200px] border-blue-100 hover:border-blue-400 transition-colors">
                            <div className="flex items-center justify-between border-b border-gray-100 pb-2 mb-2">
                                <div className="font-bold text-blue-700 truncate max-w-[140px]" title={step.step_id}>{step.step_id}</div>
                                <Box className="w-4 h-4 text-blue-500" />
                            </div>
                            <div className="text-[10px] text-gray-500 mb-2 line-clamp-2 leading-tight h-6">{step.description}</div>
                            <div className="text-[9px] bg-blue-50 text-blue-600 p-1.5 rounded-lg font-mono truncate border border-blue-100/50" title={step.component_id}>
                                ID: {step.component_id.split('-')[0]}...
                            </div>
                        </div>
                    )
                },
                position: { x: 0, y: 0 },
            }));

            const initialEdges: Edge[] = [];
            wf.workflow_plan.steps.forEach((step: WorkflowStep) => {
                if (step.next && step.next.length > 0) {
                    step.next.forEach((nextId: string) => {
                        initialEdges.push({
                            id: `e-${step.step_id}-${nextId}`,
                            source: step.step_id,
                            target: nextId,
                            animated: true,
                            markerEnd: {
                                type: MarkerType.ArrowClosed,
                                color: '#3b82f6',
                            },
                            style: { stroke: '#3b82f6', strokeWidth: 2 },
                        });
                    });
                }
            });

            const layouted = getLayoutedElements(initialNodes, initialEdges);
            setNodes(layouted.nodes);
            setEdges(layouted.edges);
        } catch (error) {
            console.error("Failed to fetch workflow", error);
        }
    }, [workflowId, setNodes, setEdges]);

    const fetchComponents = useCallback(async () => {
        try {
            const response = await axios.get('http://localhost:8081/components');
            setComponents(response.data);
        } catch (error) {
            console.error("Failed to fetch components", error);
        }
    }, []);

    useEffect(() => {
        const init = async () => {
            setLoading(true);
            await Promise.all([fetchWorkflow(), fetchComponents()]);
            setLoading(false);
        };
        if (workflowId) init();
    }, [workflowId, fetchWorkflow, fetchComponents]);

    // DAG Validation
    const validateDAG = useCallback((currentNodes: Node[], currentEdges: Edge[]) => {
        const adj = new Map<string, string[]>();
        currentNodes.forEach(node => adj.set(node.id, []));
        currentEdges.forEach(edge => adj.get(edge.source)?.push(edge.target));

        const visited = new Set<string>();
        const recStack = new Set<string>();

        const hasCycle = (u: string): boolean => {
            visited.add(u);
            recStack.add(u);
            for (const v of (adj.get(u) || [])) {
                if (!visited.has(v)) {
                    if (hasCycle(v)) return true;
                } else if (recStack.has(v)) {
                    return true;
                }
            }
            recStack.delete(u);
            return false;
        };

        for (const node of currentNodes) {
            if (!visited.has(node.id)) {
                if (hasCycle(node.id)) {
                    return "Cycle detected! Workflows must be directed acyclic graphs (DAGs).";
                }
            }
        }

        const connectedNodes = new Set<string>();
        currentEdges.forEach(edge => {
            connectedNodes.add(edge.source);
            connectedNodes.add(edge.target);
        });

        if (currentNodes.length > 1 && Array.from(currentNodes).some(n => !connectedNodes.has(n.id))) {
            return "Isolated nodes detected! All steps must be connected to the workflow.";
        }

        return null;
    }, []);

    useEffect(() => {
        const error = validateDAG(nodes, edges);
        setValidationError(error);
    }, [nodes, edges, validateDAG]);

    const onConnect = useCallback(
        (params: Connection) => {
            setEdges((eds) => addEdge({
                ...params,
                animated: true,
                markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' },
                style: { stroke: '#3b82f6', strokeWidth: 2 }
            }, eds));
        },
        [setEdges]
    );

    const onDragStart = (event: React.DragEvent, component: Component) => {
        event.dataTransfer.setData('application/reactflow', JSON.stringify(component));
        event.dataTransfer.effectAllowed = 'move';
    };

    const onDragOver = useCallback((event: React.DragEvent) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    const onDrop = useCallback(
        (event: React.DragEvent) => {
            event.preventDefault();

            if (!reactFlowWrapper.current || !reactFlowInstance) return;

            const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
            const rawData = event.dataTransfer.getData('application/reactflow');
            if (!rawData) return;

            const componentData = JSON.parse(rawData) as Component;

            const position = reactFlowInstance.project({
                x: event.clientX - reactFlowBounds.left,
                y: event.clientY - reactFlowBounds.top,
            });

            const step_id = `${componentData.name.toLowerCase().replace(/\s+/g, '_')}_${Date.now().toString().slice(-4)}`;

            const newNode: Node = {
                id: step_id,
                type: 'default',
                position,
                data: {
                    label: (
                        <div className="p-3 border rounded-xl bg-white shadow-sm min-w-[200px] border-blue-100 hover:border-blue-400 transition-colors">
                            <div className="flex items-center justify-between border-b border-gray-100 pb-2 mb-2">
                                <div className="font-bold text-blue-700 truncate max-w-[140px]" title={step_id}>{step_id}</div>
                                <Box className="w-4 h-4 text-blue-500" />
                            </div>
                            <div className="text-[10px] text-gray-500 mb-2 line-clamp-2 leading-tight h-6">{componentData.description}</div>
                            <div className="text-[9px] bg-blue-50 text-blue-600 p-1.5 rounded-lg font-mono truncate border border-blue-100/50" title={componentData.id}>
                                ID: {componentData.id.split('-')[0]}...
                            </div>
                        </div>
                    ),
                    originalComponent: componentData
                },
            };

            setNodes((nds) => nds.concat(newNode));

            setWorkflow(prev => {
                if (!prev) return null;
                const newStep: WorkflowStep = {
                    step_id,
                    component_id: componentData.id,
                    description: componentData.description || '',
                    inputs: { path_params: {}, query_params: {}, request_body: {} },
                    outputs: [],
                    next: []
                };
                return {
                    ...prev,
                    workflow_plan: {
                        ...prev.workflow_plan,
                        steps: [...prev.workflow_plan.steps, newStep]
                    }
                };
            });
        },
        [reactFlowInstance, setNodes]
    );

    const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
        // Handle "Connecting Mode"
        if (connectingSource) {
            if (connectingSource !== node.id) {
                const params: Connection = {
                    source: connectingSource,
                    target: node.id,
                    sourceHandle: null,
                    targetHandle: null
                };
                onConnect(params);
            }
            setConnectingSource(null);
            return;
        }

        if (workflow && workflow.workflow_plan && workflow.workflow_plan.steps) {
            const step = workflow.workflow_plan.steps.find((s) => s.step_id === node.id);
            if (step) {
                setSelectedStep(step);
                setIsModalOpen(true);
            }
        }
    }, [workflow, connectingSource, onConnect]);

    // Right Click Handlers
    const onNodeContextMenu = useCallback(
        (event: React.MouseEvent, node: Node) => {
            event.preventDefault();
            if (!reactFlowWrapper.current) return;
            const pane = reactFlowWrapper.current.getBoundingClientRect();
            setMenu({
                id: node.id,
                top: event.clientY - pane.top,
                left: event.clientX - pane.left,
            });
        },
        [setMenu]
    );

    const onPaneClick = useCallback(() => {
        setMenu(null);
        setConnectingSource(null);
    }, []);

    const deleteNode = useCallback((id: string) => {
        setNodes((nds) => nds.filter((node) => node.id !== id));
        setEdges((eds) => eds.filter((edge) => edge.source !== id && edge.target !== id));
        setMenu(null);
    }, [setNodes, setEdges]);

    const handleSave = async () => {
        if (validationError) {
            alert(`Cannot save: ${validationError}`);
            return;
        }

        setSaving(true);
        try {
            if (!workflow || !workflow.workflow_plan) return;

            const updatedSteps = nodes.map(node => {
                const existingStep = workflow.workflow_plan.steps.find(s => s.step_id === node.id);
                const nextSteps = edges
                    .filter(edge => edge.source === node.id)
                    .map(edge => edge.target);

                if (existingStep) {
                    return { ...existingStep, next: nextSteps };
                } else {
                    return {
                        step_id: node.id,
                        component_id: node.data.originalComponent?.id || '',
                        description: node.data.originalComponent?.description || '',
                        inputs: { path_params: {}, query_params: {}, request_body: {} },
                        outputs: [],
                        next: nextSteps
                    };
                }
            });

            const updatedPlan = {
                ...workflow.workflow_plan,
                steps: updatedSteps
            };

            await axios.put(`http://localhost:8081/workflows/${workflowId}`, updatedPlan);
            alert('Workflow saved successfully!');
        } catch (error) {
            console.error("Failed to save workflow", error);
            alert('Failed to save workflow');
        } finally {
            setSaving(false);
        }
    };

    const filteredComponents = components.filter(c =>
        c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.category?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    if (loading) {
        return (
            <div className="h-[80vh] w-full flex items-center justify-center bg-gray-50/50 rounded-2xl border border-dashed border-blue-200">
                <div className="flex flex-col items-center space-y-4">
                    <RefreshCw className="w-10 h-10 text-blue-500 animate-spin" />
                    <p className="text-blue-600 font-medium animate-pulse">Loading workflow engine...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="h-[85vh] w-full border border-blue-100 rounded-3xl bg-white flex flex-col shadow-2xl overflow-hidden">
            {/* Header */}
            <div className="px-8 py-5 border-b border-blue-50 bg-gradient-to-r from-white to-blue-50/30 flex justify-between items-center shrink-0">
                <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-blue-500 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-blue-200">
                        <GitBranch size={24} />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-gray-800 tracking-tight">{workflow?.workflow_plan?.workflow_name || 'Workflow Editor'}</h2>
                        <p className="text-sm text-gray-500 font-medium">{workflow?.workflow_plan?.description}</p>
                    </div>
                </div>

                <div className="flex items-center space-x-3">
                    {connectingSource && (
                        <div className="flex items-center space-x-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-xl border border-blue-100 animate-bounce text-xs font-bold">
                            <Box size={14} />
                            <span>Select target node to connect to...</span>
                        </div>
                    )}
                    {validationError && (
                        <div className="flex items-center space-x-2 px-4 py-2 bg-red-50 text-red-600 rounded-xl border border-red-100 animate-pulse text-xs font-bold">
                            <AlertTriangle size={14} />
                            <span>{validationError}</span>
                        </div>
                    )}
                    <button
                        onClick={fetchWorkflow}
                        className="flex items-center gap-2 px-4 py-2.5 text-sm font-bold text-gray-600 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-all active:scale-95 shadow-sm"
                    >
                        <RefreshCw size={16} /> Reset
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={saving || !!validationError}
                        className="flex items-center gap-2 px-6 py-2.5 text-sm font-bold text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl hover:shadow-lg hover:shadow-blue-200 transition-all active:scale-95 disabled:opacity-30 disabled:pointer-events-none"
                    >
                        <Save size={16} /> {saving ? 'Saving...' : 'Save Workflow'}
                    </button>
                </div>
            </div>

            {/* Main Section */}
            <div className="flex-1 flex overflow-hidden">
                <div className="flex-1 relative bg-gray-50/50" ref={reactFlowWrapper}>
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onConnect={onConnect}
                        onNodeClick={onNodeClick}
                        onInit={setReactFlowInstance}
                        onDrop={onDrop}
                        onDragOver={onDragOver}
                        onNodeContextMenu={onNodeContextMenu}
                        onPaneClick={onPaneClick}
                        fitView
                        className="validation-check"
                        deleteKeyCode={["Backspace", "Delete"]}
                    >
                        <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="#cbd5e1" />
                        <Controls className="bg-white border-blue-50 shadow-lg rounded-xl overflow-hidden" />
                        <MiniMap
                            className="bg-white border-blue-50 shadow-xl rounded-2xl overflow-hidden"
                            nodeColor="#eff6ff"
                            maskColor="rgba(241, 245, 249, 0.7)"
                        />
                        <Panel position="top-left" className="bg-white/80 backdrop-blur-md p-2 rounded-xl border border-blue-100 shadow-sm text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                            Editor Canvas
                        </Panel>

                        {/* Context Menu Overlay */}
                        {menu && (
                            <div
                                style={{ top: menu.top, left: menu.left }}
                                className="absolute z-50 bg-white border border-blue-100 shadow-2xl rounded-2xl py-2 min-w-[180px] backdrop-blur-sm shadow-blue-500/10"
                            >
                                <button
                                    onClick={() => {
                                        const step = workflow?.workflow_plan?.steps.find(s => s.step_id === menu.id);
                                        if (step) {
                                            setSelectedStep(step);
                                            setIsModalOpen(true);
                                        }
                                        setMenu(null);
                                    }}
                                    className="w-full flex items-center space-x-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
                                >
                                    <Box size={16} />
                                    <span className="font-semibold">Info</span>
                                </button>
                                <button
                                    onClick={() => {
                                        setConnectingSource(menu.id);
                                        setMenu(null);
                                    }}
                                    className="w-full flex items-center space-x-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
                                >
                                    <GitBranch size={16} />
                                    <span className="font-semibold">Extend Arrow</span>
                                </button>
                                <div className="my-1 border-t border-gray-100" />
                                <button
                                    onClick={() => deleteNode(menu.id)}
                                    className="w-full flex items-center space-x-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                                >
                                    <Trash2 size={16} />
                                    <span className="font-semibold">Delete</span>
                                </button>
                            </div>
                        )}
                    </ReactFlow>
                </div>

                {/* Component Library Sidebar */}
                <div className={`border-l border-blue-50 bg-white transition-all duration-500 ease-in-out flex flex-col shadow-[-10px_0_30px_rgba(0,0,0,0.02)] ${isLibOpen ? 'w-80' : 'w-0'}`}>
                    <div className="w-80 h-full flex flex-col shrink-0">
                        <div className="p-6 border-b border-blue-50 flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                                <Puzzle className="w-5 h-5 text-blue-500" />
                                <h3 className="font-bold text-gray-800">Components</h3>
                            </div>
                            <button onClick={() => setIsLibOpen(false)} className="p-2 hover:bg-red-50 hover:text-red-500 rounded-lg transition-colors group">
                                <X size={18} className="group-active:scale-90" />
                            </button>
                        </div>

                        <div className="p-4 border-b border-blue-50 bg-blue-50/30">
                            <div className="relative group">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-blue-500 transition-colors" size={16} />
                                <input
                                    type="text"
                                    placeholder="Search API components..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2.5 text-sm bg-white border border-blue-100 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none"
                                />
                            </div>
                        </div>

                        <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                            {filteredComponents.length > 0 ? (
                                filteredComponents.map((comp) => (
                                    <div
                                        key={comp.id}
                                        draggable
                                        onDragStart={(e) => onDragStart(e, comp)}
                                        className="p-4 border border-blue-50 rounded-2xl bg-white hover:border-blue-300 hover:shadow-xl hover:shadow-blue-500/5 transition-all cursor-move group relative active:scale-[0.98]"
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-[10px] font-black text-blue-500 uppercase tracking-tighter bg-blue-50 px-2 py-0.5 rounded-md">
                                                {comp.type}
                                            </span>
                                            <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                                                <div className="w-4 h-4 bg-blue-100 rounded-full flex items-center justify-center">
                                                    <ChevronLeft size={10} className="text-blue-600" />
                                                </div>
                                            </div>
                                        </div>
                                        <h4 className="font-bold text-sm text-gray-800 group-hover:text-blue-600 transition-colors mb-1 truncate">{comp.name}</h4>
                                        <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed h-8">{comp.description}</p>
                                    </div>
                                ))
                            ) : (
                                <div className="h-full flex flex-col items-center justify-center text-center p-8">
                                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                                        <Search size={24} className="text-gray-300" />
                                    </div>
                                    <p className="text-sm font-bold text-gray-500">No components found</p>
                                    <p className="text-xs text-gray-400">Try a different search term</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {!isLibOpen && (
                    <button
                        onClick={() => setIsLibOpen(true)}
                        className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-24 bg-white border border-blue-100 shadow-2xl rounded-2xl flex flex-col items-center justify-center text-blue-500 hover:bg-blue-50 transition-all hover:w-12 z-10 group"
                    >
                        <ChevronLeft size={18} className="mb-2 transition-transform group-hover:-translate-x-1" />
                        <span className="[writing-mode:vertical-lr] font-black text-[10px] uppercase tracking-[0.2em]">Components</span>
                    </button>
                )}
            </div>

            <StepDetailsModal
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false);
                    setSelectedStep(null);
                }}
                step={selectedStep}
            />
        </div>
    );
};

export default WorkflowEditor;
