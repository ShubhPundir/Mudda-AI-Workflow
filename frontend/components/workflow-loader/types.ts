// Types for WorkflowGenerationLoader
export interface Component {
    id: string;
    name: string;
    description: string;
}

export type AgentStatus = 'idle' | 'active' | 'complete';

export type LoaderStage = 'component_selection' | 'workflow_generation' | 'complete' | 'error';

export interface LoaderState {
    agent1Status: AgentStatus;
    agent2Status: AgentStatus;
    selectedComponents: Component[];
    currentMessage: string;
    stage: LoaderStage;
}

export interface AgentConfig {
    id: number;
    name: string;
    role: string;
    icon: string;
    activeColor: string;
    activeMessage: string;
    completeMessage: string | ((state: LoaderState) => string);
    idleMessage: string;
}

export const AGENTS: AgentConfig[] = [
    {
        id: 1,
        name: 'Agent 1',
        role: 'Component Selector',
        icon: '🤖',
        activeColor: 'blue',
        activeMessage: 'Analyzing problem statement and selecting relevant components...',
        completeMessage: (state) => `Selected ${state.selectedComponents.length} components`,
        idleMessage: 'Waiting to start...',
    },
    {
        id: 2,
        name: 'Agent 2',
        role: 'Plan Maker',
        icon: '🧠',
        activeColor: 'purple',
        activeMessage: 'Creating workflow plan with selected components...',
        completeMessage: 'Workflow plan created successfully',
        idleMessage: 'Waiting for component selection...',
    },
];
