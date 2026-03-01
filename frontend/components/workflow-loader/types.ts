// Types for WorkflowGenerationLoader
export interface Component {
    id: string;
    name: string;
    description: string;
}

export interface Policy {
    heading: string;
    author: string;
    similarity_score: number;
}

export type AgentStatus = 'idle' | 'active' | 'complete';

export type LoaderStage = 'policy_retrieval' | 'activity_selection' | 'workflow_generation' | 'plan_validation' | 'complete' | 'error';

export interface LoaderState {
    agent1Status: AgentStatus; // Policy Retrieval
    agent2Status: AgentStatus; // Activity Selector
    agent3Status: AgentStatus; // Plan Maker
    agent4Status: AgentStatus; // Plan Validator
    retrievedPolicies: Policy[];
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
        role: 'Policy Retrieval',
        icon: '📚',
        activeColor: 'cyan',
        activeMessage: 'Retrieving relevant policies from knowledge base...',
        completeMessage: (state) => `Retrieved ${state.retrievedPolicies.length} relevant policies`,
        idleMessage: 'Waiting to start...',
    },
    {
        id: 2,
        name: 'Agent 2',
        role: 'Activity Selector',
        icon: '🤖',
        activeColor: 'blue',
        activeMessage: 'Analyzing problem and selecting activities based on policies...',
        completeMessage: (state) => `Selected ${state.selectedComponents.length} activities`,
        idleMessage: 'Waiting for policy retrieval...',
    },
    {
        id: 3,
        name: 'Agent 3',
        role: 'Plan Maker',
        icon: '🧠',
        activeColor: 'purple',
        activeMessage: 'Creating workflow plan with policy compliance...',
        completeMessage: 'Workflow plan created successfully',
        idleMessage: 'Waiting for activity selection...',
    },
    {
        id: 4,
        name: 'Agent 4',
        role: 'Plan Validator',
        icon: '✅',
        activeColor: 'green',
        activeMessage: 'Validating workflow plan for correctness...',
        completeMessage: 'Workflow validated successfully',
        idleMessage: 'Waiting for plan creation...',
    },
];
