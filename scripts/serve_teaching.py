import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class CleanTeachingServer(ThreadingHTTPServer):
    allow_reuse_address = False


ROOT_DIR = str(Path(__file__).resolve().parents[1])
handler = functools.partial(SimpleHTTPRequestHandler, directory=ROOT_DIR)
server = CleanTeachingServer(("127.0.0.1", 4322), handler)
print(f"Serving {ROOT_DIR} on http://127.0.0.1:4322/ (threaded, exclusive bind)", flush=True)
server.serve_forever()
