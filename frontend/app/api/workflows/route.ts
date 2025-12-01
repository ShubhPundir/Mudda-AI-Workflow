import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// GET /api/workflows - List all workflows
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const skip = parseInt(searchParams.get('skip') || '0');
    const limit = parseInt(searchParams.get('limit') || '100');

    const response = await apiClient.get('/workflows', {
      params: { skip, limit },
    });
    return NextResponse.json(response.data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data?.detail || error.message || 'Failed to fetch workflows' },
      { status: error.response?.status || 500 }
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

    const response = await apiClient.post('/workflows/generate', { problem_statement });
    return NextResponse.json(response.data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.response?.data?.detail || error.message || 'Failed to generate workflow' },
      { status: error.response?.status || 500 }
    );
  }
}

