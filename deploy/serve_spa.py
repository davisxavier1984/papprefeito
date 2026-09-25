#!/usr/bin/env python3
"""Servidor estático com fallback SPA para o build de produção do frontend.

Serve os arquivos de --directory. Rotas que não correspondem a um arquivo real
caem em index.html, para o react-router resolver no cliente. Assets ausentes
continuam retornando 404, em vez de devolver o HTML disfarçado de JS.
"""
from __future__ import annotations

import argparse
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class SPARequestHandler(SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler com fallback para index.html."""

    def send_head(self):
        # translate_path já descarta query string e normaliza ".." fora da raiz.
        alvo = self.translate_path(self.path)
        eh_asset = self.path.startswith("/assets/")
        if not eh_asset and not os.path.exists(alvo):
            self.path = "/index.html"
        return super().send_head()

    def end_headers(self):
        # O index.html referencia bundles com hash no nome; ele próprio não pode
        # ser cacheado, senão um deploy novo não chega no navegador.
        if self.path in ("/", "/index.html"):
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5173)
    parser.add_argument("--directory", required=True)
    args = parser.parse_args()

    if not os.path.isfile(os.path.join(args.directory, "index.html")):
        raise SystemExit(f"index.html não encontrado em {args.directory} — rode o build antes.")

    handler = partial(SPARequestHandler, directory=args.directory)
    with ThreadingHTTPServer((args.bind, args.port), handler) as httpd:
        print(f"Servindo {args.directory} em http://{args.bind}:{args.port}", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
