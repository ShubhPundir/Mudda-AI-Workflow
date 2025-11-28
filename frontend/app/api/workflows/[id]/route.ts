import { NextRequest, NextResponse } from 'next/server';
import { workflowApi } from '@/lib/api';

// GET /api/workflows/[id] - Get a specific workflow
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const workflow = await workflowApi.getById(params.id);
    
    if (!workflow) {
      return NextResponse.json(
        { error: 'Workflow not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(workflow);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to fetch workflow' },
      { status: 500 }
    );
  }
}

