'use client';

import { LoaderState } from './types';
import { ProgressStep, ProgressConnector } from './Primitives';

interface ProgressTimelineProps {
    state: LoaderState;
}

export function ProgressTimeline({ state }: ProgressTimelineProps) {
    return (
        <div className="flex items-center justify-center mb-10 overflow-x-auto">
            <div className="flex items-center space-x-2 min-w-max px-4">
                <ProgressStep
                    stepNumber={1}
                    label="Policy Retrieval"
                    isActive={state.stage === 'policy_retrieval'}
                    isComplete={state.agent1Status === 'complete'}
                    activeColor="cyan"
                />

                <ProgressConnector
                    isComplete={state.agent1Status === 'complete'}
                    fromColor="cyan"
                    toColor="blue"
                />

                <ProgressStep
                    stepNumber={2}
                    label="Activity Selection"
                    isActive={state.stage === 'activity_selection'}
                    isComplete={state.agent2Status === 'complete'}
                    activeColor="blue"
                />

                <ProgressConnector
                    isComplete={state.agent2Status === 'complete'}
                    fromColor="blue"
                    toColor="purple"
                />

                <ProgressStep
                    stepNumber={3}
                    label="Workflow Planning"
                    isActive={state.stage === 'workflow_generation'}
                    isComplete={state.agent3Status === 'complete'}
                    activeColor="purple"
                />

                <ProgressConnector
                    isComplete={state.agent3Status === 'complete'}
                    fromColor="purple"
                    toColor="green"
                />

                <ProgressStep
                    stepNumber={4}
                    label="Plan Validation"
                    isActive={state.stage === 'plan_validation'}
                    isComplete={state.agent4Status === 'complete'}
                    activeColor="green"
                />

                <ProgressConnector
                    isComplete={state.agent4Status === 'complete'}
                    fromColor="green"
                    toColor="emerald"
                />

                <ProgressStep
                    stepNumber="✓"
                    label=""
                    isActive={state.stage === 'complete'}
                    isComplete={false}
                    activeColor="emerald"
                />
            </div>
        </div>
    );
}
