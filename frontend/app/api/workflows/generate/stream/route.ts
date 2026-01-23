import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081';

// POST /api/workflows/generate/stream - Stream workflow generation
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

        // Forward the request to the backend streaming endpoint
        const backendResponse = await fetch(`${API_URL}/workflows/generate/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ problem_statement }),
        });

        if (!backendResponse.ok) {
            const error = await backendResponse.json().catch(() => ({ detail: 'Failed to generate workflow' }));
            return NextResponse.json(
                { error: error.detail || 'Failed to generate workflow' },
                { status: backendResponse.status }
            );
        }

        // Stream the response back to the client
        const stream = backendResponse.body;

        if (!stream) {
            return NextResponse.json(
                { error: 'No response stream from backend' },
                { status: 500 }
            );
        }

        // Return streaming response with SSE headers
        return new NextResponse(stream, {
            headers: {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
            },
        });

    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || 'Failed to generate workflow stream' },
            { status: 500 }
        );
    }
}
