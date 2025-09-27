import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  try {
    // Get the authorization header
    const authHeader = req.headers.get('authorization')
    if (!authHeader) {
      return NextResponse.json({ error: 'Authorization required' }, { status: 401 })
    }

    // Parse request body
    const body = await req.json()

    // Construct Supabase edge function URL
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const edgeFunctionUrl = `${supabaseUrl}/functions/v1/spawn-project`

    console.log('🌐 Proxying to Supabase edge function:', edgeFunctionUrl)

    // Forward request to Supabase edge function
    const response = await fetch(edgeFunctionUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
        'apikey': process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      },
      body: JSON.stringify(body)
    })

    const result = await response.json()

    // Return the response from the edge function
    return NextResponse.json(result, { status: response.status })

  } catch (error) {
    console.error('API route error:', error)
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}