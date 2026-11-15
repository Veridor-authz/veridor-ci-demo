"""Invoice API: a small stand-in service for the CI demo."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Bearer token -> tenant. CI provides the tokens as secrets.
TENANTS = {os.environ["ACME_TOKEN"]: "acme", os.environ["GLOBEX_TOKEN"]: "globex"}

INVOICES = {
    "inv-100": {"tenant": "acme", "customer": "vdr-Xk7Qm2Ls9Rt4Vb8Nc3Zp6Wf1", "total": 1200},
    "inv-200": {"tenant": "globex", "customer": "vdr-Bq3Wm8Ke5Tz1Yx7Rn2Hd4Vs6", "total": 90},
}


def can_read(tenant, invoice):
    # A shared invoice is readable by any signed-in tenant.
    return invoice["tenant"] == tenant or invoice.get("shared", False)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        token = self.headers.get("Authorization", "").removeprefix("Bearer ")
        tenant = TENANTS.get(token)
        if tenant is None:
            return self.reply(401, {"error": "sign in"})
        invoice = INVOICES.get(self.path.removeprefix("/api/invoices/"))
        if invoice is None or not can_read(tenant, invoice):
            return self.reply(404, {"error": "not found"})
        return self.reply(200, invoice)

    def reply(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
