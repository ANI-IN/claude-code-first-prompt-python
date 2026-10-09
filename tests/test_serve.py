"""The local dev server serves the project files with caching disabled."""

import threading
import urllib.request

import pytest

from serve import make_server


@pytest.fixture
def base_url():
    server = make_server(port=0, quiet=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}/"
    server.shutdown()
    server.server_close()


@pytest.mark.parametrize("path, content_type, marker", [
    ("", "text/html", b"FlowState"),
    ("styles.css", "text/css", b":root"),
    ("main.py", "text/x-python", b"def main():"),
])
def test_serves_page_files_without_caching(base_url, path, content_type, marker):
    with urllib.request.urlopen(base_url + path) as response:
        assert response.status == 200
        assert response.headers["Content-Type"].startswith(content_type)
        assert response.headers["Cache-Control"] == "no-store"
        assert marker in response.read()
