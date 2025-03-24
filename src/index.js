// Cloudflare Worker script for IP-based visitor counting
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
    
    try {
      // Get the visitor's IP address
      const clientIP = request.headers.get('CF-Connecting-IP') || 
                      request.headers.get('X-Forwarded-For') || 
                      'unknown-ip';
      
      // Get URL path to differentiate between actions
      const url = new URL(request.url);
      const path = url.pathname;
      
      // Get the current count
      let count = await env.VISITOR_COUNTER.get('total_visitors');
      if (count === null) {
        count = '42'; // Start with base count
      }
      count = parseInt(count);
      
      // Handle the increment request - only if this is a new IP
      if (path === '/increment') {
        // Check if this IP has been counted before
        const ipKey = `ip_${clientIP.replace(/\./g, '_')}`;
        const hasVisited = await env.VISITOR_COUNTER.get(ipKey);
        
        if (!hasVisited) {
          // This is a new IP, increment the counter
          count += 1;
          await env.VISITOR_COUNTER.put('total_visitors', count.toString());
          
          // Mark this IP as counted (with 30-day expiration)
          await env.VISITOR_COUNTER.put(ipKey, 'visited', {expirationTtl: 60 * 60 * 24 * 30});
        }
      }
      
      // Return the count as JSON
      return new Response(JSON.stringify({ 
        count: count,
        // For debugging, can be removed in production
        ip: clientIP.split('.').slice(0, 2).join('.') + '.x.x' // Only return partial IP for privacy
      }), {
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    } catch (error) {
      // Handle errors gracefully
      return new Response(JSON.stringify({ 
        error: 'Counter service unavailable', 
        count: 42 // Fallback count
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
  }
}