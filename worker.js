export default {
  async fetch(request, env) {
    // Set CORS headers to allow your site
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*', // Replace with your actual domain in production
      'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    // Handle preflight OPTIONS request
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders })
    }
    
    // Get URL path to differentiate between increment and just getting the count
    const url = new URL(request.url)
    const path = url.pathname
    
    // Use KV binding to get/set counter
    let count = await env.VISITOR_COUNTER.get('visitors')
    if (count === null) {
      count = '42' // Start with base count
    }
    
    // Convert to number
    count = parseInt(count)
    
    // Only increment for specific endpoint
    if (path === '/increment') {
      // Increment and store the new count
      await env.VISITOR_COUNTER.put('visitors', (count + 1).toString())
      count += 1
    }
    
    // Return the count as JSON
    return new Response(JSON.stringify({ count: count }), {
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    })
  }
}