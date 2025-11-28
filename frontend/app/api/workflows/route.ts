import { NextRequest, NextResponse } from 'next/server';
import { workflowApi } from '@/lib/api';

// GET /api/workflows - List all workflows
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const skip = parseInt(searchParams.get('skip') || '0');
    const limit = parseInt(searchParams.get('limit') || '100');

    const workflows = await workflowApi.getAll(skip, limit);
    return NextResponse.json(workflows);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to fetch workflows' },
      { status: 500 }
    );
  }
}

// POST /api/workflows - Generate a new workflow
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { problem_statement } = body;

    if (!problem_statement) {
      return NextResponse.json(
        { error: 'problem_statement is required' },
        { status: 400 }
      );
    }

    const workflow = await workflowApi.generate({ problem_statement });
    return NextResponse.json(workflow);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to generate workflow' },
      { status: 500 }
    );
  }
}

