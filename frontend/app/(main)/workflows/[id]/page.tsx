"use client";

import { useParams } from 'next/navigation';
import WorkflowEditor from '@/components/WorkflowEditor';

export default function WorkflowDetailsPage() {
    const params = useParams();
    const id = params.id as string;

    return (
        <div className="h-full flex flex-col">
            <div className="flex-1 p-4">
                <WorkflowEditor workflowId={id} />
            </div>
        </div>
    );
}
