from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class ReviewHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if not self.path.startswith("/reviews/"):
            self.send_error(404)
            return

        try:
            product_id = int(self.path.split("/")[-1])
        except ValueError:
            self.send_error(404)
            return

        score = 3.5 + (product_id % 15) / 10
        review_count = 10 + (product_id * 7)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Product Review</title>
</head>
<body>
    <div class="review">
        <span class="average-score">{score:.1f}</span>
        <span class="review-count">{review_count}</span>
    </div>
</body>
</html>
"""

        content = html.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        return


def start_review_server(host="127.0.0.1", port=8765):
    """Start the simulated review website."""
    server = ThreadingHTTPServer((host, port), ReviewHandler)
    server.serve_forever()


if __name__ == "__main__":
    start_review_server()
