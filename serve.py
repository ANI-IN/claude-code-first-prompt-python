"""Serve the FlowState landing page locally.

Usage:
    python serve.py                 # http://localhost:8000
    python serve.py --port 9000     # pick another port
    python serve.py --open          # also open the page in your browser

The page loads main.py over HTTP, so it must be served rather than opened as a
file. Responses are sent with caching disabled, so a plain reload always picks
up your latest edits to index.html, styles.css, and main.py.
"""

import argparse
import functools
import http.server
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    """Static file handler that tells the browser never to cache responses."""

    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".py": "text/x-python; charset=utf-8",
    }

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, format, *args):
        if not getattr(self.server, "quiet", False):
            super().log_message(format, *args)


def make_server(port=8000, host="127.0.0.1", quiet=False):
    """Create (but do not start) a server for the project folder."""
    handler = functools.partial(NoCacheHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer((host, port), handler)
    server.quiet = quiet
    return server


def main():
    parser = argparse.ArgumentParser(description="Serve the FlowState landing page.")
    parser.add_argument("--port", type=int, default=8000, help="port to listen on (default: 8000)")
    parser.add_argument("--host", default="127.0.0.1", help="interface to bind (default: 127.0.0.1)")
    parser.add_argument("--open", action="store_true", help="open the page in your default browser")
    args = parser.parse_args()

    server = make_server(args.port, args.host)
    url = f"http://localhost:{server.server_address[1]}/"
    print(f"Serving FlowState at {url}  (press Ctrl+C to stop)")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
