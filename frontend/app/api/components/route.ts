import { NextRequest, NextResponse } from 'next/server';
import { componentApi } from '@/lib/api';

// GET /api/components - List all components
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const activeOnly = searchParams.get('active_only') !== 'false';

    const components = await componentApi.getAll(activeOnly);
    return NextResponse.json(components);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to fetch components' },
      { status: 500 }
    );
  }
}

// POST /api/components - Create a new component
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const component = await componentApi.create(body);
    return NextResponse.json(component);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Failed to create component' },
      { status: 500 }
    );
  }
}

