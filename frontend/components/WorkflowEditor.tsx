"use client";

import React, { useState, useCallback, useEffect } from 'react';
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
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import { Save, RefreshCw } from 'lucide-react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import StepDetailsModal from './StepDetailsModal';
import { Workflow, WorkflowStep } from '@/lib/type';

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

        // We are shifting the dagre node position (anchor=center center) to the top left
        // so it matches the React Flow node anchor point (top left).
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
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [selectedStep, setSelectedStep] = useState<WorkflowStep | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const router = useRouter();

    const fetchWorkflow = useCallback(async () => {
        try {
            const response = await axios.get(`http://localhost:8081/workflows/${workflowId}`);
            const wf = response.data;
            setWorkflow(wf);

            // Transform Mudda workflow to ReactFlow
            const initialNodes = wf.workflow_plan.steps.map((step: WorkflowStep) => ({
                id: step.step_id,
                type: 'default',
                data: {
                    label: (
                        <div className="p-2 border rounded bg-white shadow-sm min-w-[200px]">
                            <div className="font-bold border-b pb-1 mb-1 truncate" title={step.step_id}>{step.step_id}</div>
                            <div className="text-xs text-gray-500 mb-1">{step.description}</div>
                            <div className="text-xs bg-gray-100 p-1 rounded font-mono truncate" title={step.component_id}>
                                📦 {step.component_id}
                            </div>
                        </div>
                    )
                },
                position: { x: 0, y: 0 }, // Will be set by dagre
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
                            },
                        });
                    });
                }
            });

            const layouted = getLayoutedElements(initialNodes, initialEdges);
            setNodes(layouted.nodes);
            setEdges(layouted.edges);
            setLoading(false);
        } catch (error) {
            console.error("Failed to fetch workflow", error);
            setLoading(false);
        }
    }, [workflowId, setNodes, setEdges]);

    useEffect(() => {
        if (workflowId) {
            fetchWorkflow();
        }
    }, [workflowId, fetchWorkflow]);

    const onConnect = useCallback(
        (params: Connection) => setEdges((eds) => addEdge({ ...params, animated: true, markerEnd: { type: MarkerType.ArrowClosed } }, eds)),
        [setEdges]
    );

    const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
        if (workflow && workflow.workflow_plan && workflow.workflow_plan.steps) {
            const step = workflow.workflow_plan.steps.find((s) => s.step_id === node.id);
            if (step) {
                setSelectedStep(step);
                setIsModalOpen(true);
            }
        }
    }, [workflow]);

    const handleSave = async () => {
        setSaving(true);
        try {
            // Reconstruct workflow plan from graph
            // We assume nodes aren't added/removed, just edges. 
            // If nodes are removed, we'd need to handle that.

            if (!workflow || !workflow.workflow_plan) return;

            const updatedSteps = workflow.workflow_plan.steps.map(step => {
                // Find outgoing edges from this node
                const nextSteps = edges
                    .filter(edge => edge.source === step.step_id)
                    .map(edge => edge.target);

                return {
                    ...step,
                    next: nextSteps
                };
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

    if (loading) return <div>Loading workflow...</div>;

    return (
        <div className="h-[80vh] w-full border rounded-lg bg-gray-50 flex flex-col">
            <div className="p-4 border-b bg-white flex justify-between items-center">
                <div>
                    <h2 className="text-xl font-bold">{workflow?.workflow_plan?.workflow_name || 'Workflow Editor'}</h2>
                    <p className="text-sm text-gray-500">{workflow?.workflow_plan?.description}</p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={fetchWorkflow}
                        className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 bg-gray-100 rounded hover:bg-gray-200"
                    >
                        <RefreshCw size={16} /> Reset
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                        <Save size={16} /> {saving ? 'Saving...' : 'Save Workflow'}
                    </button>
                </div>
            </div>
            <div className="flex-1">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    onNodeClick={onNodeClick}
                    fitView
                >
                    <Controls />
                    <MiniMap />
                    <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
                </ReactFlow>
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
