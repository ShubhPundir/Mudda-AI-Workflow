import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// GET /api/components/[id] - Get a specific component
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const response = await apiClient.get(`/components/${params.id}`);
    return NextResponse.json(response.data);
  } catch (error: any) {
    if (error.response?.status === 404) {
      return NextResponse.json(
        { error: 'Component not found' },
        { status: 404 }
      );
    }
    return NextResponse.json(
      { error: error.response?.data?.detail || error.message || 'Failed to fetch component' },
      { status: error.response?.status || 500 }
    );
  }
}

