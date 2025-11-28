import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// GET /api/components - List all components
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const activeOnly = searchParams.get('active_only') !== 'false';

    const response = await apiClient.get('/components', {
      params: { active_only: activeOnly },
    });
    return NextResponse.json(response.data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data?.detail || error.message || 'Failed to fetch components' },
      { status: error.response?.status || 500 }
    );
  }
}

// POST /api/components - Create a new component
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await apiClient.post('/components', body);
    return NextResponse.json(response.data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data?.detail || error.message || 'Failed to create component' },
      { status: error.response?.status || 500 }
    );
  }
}

