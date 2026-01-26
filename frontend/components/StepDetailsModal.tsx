"use client";

import React from 'react';
import Modal from './Modal';

interface StepDetailsModalProps {
    isOpen: boolean;
    onClose: () => void;
    step: any; // We can type this properly if we have the schema shared, but 'any' is fine for now given the context
}

export default function StepDetailsModal({
    isOpen,
    onClose,
    step,
}: StepDetailsModalProps) {
    if (!step) return null;

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title={`Step Details: ${step.step_id}`}
            size="lg"
        >
            <div className="space-y-6">
                <div>
                    <h4 className="text-sm font-medium text-gray-500 mb-1">Description</h4>
                    <p className="text-gray-900">{step.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
                    <div>
                        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Component ID</span>
                        <p className="text-sm text-gray-900 font-medium mt-1 bg-gray-50 p-2 rounded border border-gray-200 inline-block">
                            {step.component_id}
                        </p>
                    </div>
                    <div>
                        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Requires Approval</span>
                        <div className="mt-1">
                            {step.requires_approval ? (
                                <span className="inline-flex px-3 py-1 text-xs font-semibold rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                                    Yes
                                </span>
                            ) : (
                                <span className="text-sm text-gray-600">No</span>
                            )}
                        </div>
                    </div>
                </div>

                {step.inputs && Object.keys(step.inputs).length > 0 && (
                    <div className="pt-4 border-t border-gray-100">
                        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 block">Inputs</span>
                        <pre className="mt-2 text-xs bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto font-mono">
                            {JSON.stringify(step.inputs, null, 2)}
                        </pre>
                    </div>
                )}

                {step.outputs && step.outputs.length > 0 && (
                    <div className="pt-4 border-t border-gray-100">
                        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 block">Outputs</span>
                        <div className="mt-2 flex flex-wrap gap-2">
                            {step.outputs.map((output: string, idx: number) => (
                                <span
                                    key={idx}
                                    className="inline-flex px-3 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 border border-blue-200 shadow-sm"
                                >
                                    {output}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {step.next && step.next.length > 0 && (
                    <div className="pt-4 border-t border-gray-100">
                        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 block">Next Steps</span>
                        <div className="flex flex-wrap gap-2">
                            {step.next.map((next: string, idx: number) => (
                                <span
                                    key={idx}
                                    className="inline-flex px-3 py-1 text-xs font-medium rounded bg-indigo-50 text-indigo-700 border border-indigo-100"
                                >
                                    → {next}
                                </span>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </Modal>
    );
}
