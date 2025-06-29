import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Proxy the request to the backend
    const backendResponse = await fetch(
      `${process.env.BACKEND_URL || 'http://localhost:8000'}/api/v1/users`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      }
    );

    const data = await backendResponse.json();

    return NextResponse.json(data, { status: backendResponse.status });
  } catch (error) {
    console.error('API proxy error:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const pathSegments = url.pathname.split('/');
    const userId = pathSegments[pathSegments.length - 1];

    // Proxy the request to the backend
    const backendResponse = await fetch(
      `${
        process.env.BACKEND_URL || 'http://localhost:8000'
      }/api/v1/users/${userId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    const data = await backendResponse.json();

    return NextResponse.json(data, { status: backendResponse.status });
  } catch (error) {
    console.error('API proxy error:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
