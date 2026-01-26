'use client';

import { LoaderState } from './types';
import { ProgressStep, ProgressConnector } from './Primitives';

interface ProgressTimelineProps {
    state: LoaderState;
}

export function ProgressTimeline({ state }: ProgressTimelineProps) {
    return (
        <div className="flex items-center justify-center mb-10 space-x-4">
            <ProgressStep
                stepNumber={1}
                label="Component Selection"
                isActive={state.stage === 'component_selection'}
                isComplete={state.agent1Status === 'complete'}
                activeColor="blue"
            />

            <ProgressConnector
                isComplete={state.agent1Status === 'complete'}
                fromColor="blue"
                toColor="purple"
            />

            <ProgressStep
                stepNumber={2}
                label="Workflow Planning"
                isActive={state.stage === 'workflow_generation'}
                isComplete={state.agent2Status === 'complete'}
                activeColor="purple"
            />

            <ProgressConnector
                isComplete={state.agent2Status === 'complete'}
                fromColor="purple"
                toColor="green"
            />

            <ProgressStep
                stepNumber="✓"
                label=""
                isActive={state.stage === 'complete'}
                isComplete={false}
                activeColor="green"
            />
        </div>
    );
}
