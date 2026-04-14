from http.server import BaseHTTPRequestHandler
import requests
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # This handles browser visits and prevents the 501 error
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Simple HTML landing page for the API link
        html = """
        <html>
            <body style="font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #f8fafc;">
                <div style="text-align: center; padding: 40px; background: white; border-radius: 20px; shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
                    <h1 style="color: #4f46e5;">CUET Proxy API Active</h1>
                    <p style="color: #64748b;">Please use the frontend at <a href="https://zodax.gamer.gd/answer_checker/nu.html" style="color: #4f46e5; text-decoration: none; font-weight: bold;">zodax.gamer.gd</a> to calculate your scores.</p>
                </div>
            </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            url = data.get('url')
            
            if not url:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'No URL provided'}).encode())
                return

            # Enhanced headers to mimic a real desktop browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Use a session to handle potential cookies/redirects from NTA
            session = requests.Session()
            res = session.get(url, headers=headers, timeout=20)
            res.raise_for_status()
            
            # Ensure we detect the correct encoding (NTA pages often use utf-8 or windows-1252)
            if res.encoding is None:
                res.encoding = 'utf-8'

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(json.dumps({
                'html': res.text,
                'status': 'success',
                'length': len(res.text)
            }).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': str(e),
                'details': 'Failed to fetch the NTA page. Check if the link is still valid.'
            }).encode('utf-8'))

    def do_OPTIONS(self):
        # Mandatory for Cross-Origin requests from InfinityFree
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
