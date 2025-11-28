import { NextRequest, NextResponse } from 'next/server';
import { componentApi } from '@/lib/api';

// GET /api/components/[id] - Get a specific component
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const component = await componentApi.getById(params.id);
    
    if (!component) {
      return NextResponse.json(
        { error: 'Component not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(component);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to fetch component' },
      { status: 500 }
    );
  }
}

