# Pin — TLS (https)

**Status (decided 2026-10-25, owner):** Pin does not do TLS, neither in its server nor in its HTTP client.
Encryption and certificates belong to a proxy next to the program, the way load balancers already handle
them.

Decision rule: memory safety > speed > clarity > looking like PHP.

## Why

- **Incoming (server):** in production, TLS is already done by a load balancer or a reverse proxy (Caddy,
  nginx, a cloud load balancer). It also renews certificates, speaks HTTP/2 and HTTP/3, and is maintained by
  people whose only job is that. Building TLS into Pin would duplicate that work.
- **Outgoing (client):** a program that calls https APIs talks to a local *egress proxy* over plain
  http on 127.0.0.1, and the proxy opens the https connection. This is what service meshes and many
  company networks already do.
- **Safety:** TLS libraries are large C code bases with a steady stream of security fixes. Linking one would
  make every Pin binary depend on keeping it current, and verifying certificates correctly is easy to get
  wrong. A proxy that is built for this does it better.
- **Speed and size:** binaries stay small and have no extra dependency (SQLite is the only optional one).

## What Pin does instead

- `serve()` speaks HTTP/1.1. Put it behind a reverse proxy for anything public.
- `http_get` / `http_post` / `http_stream` accept `http://` only. An `https://` URL fails with error 400, and
  the message points to the egress proxy.
- The docs show a working Caddy setup for both directions (language guide, Learn chapters 8 and 14, AI
  guide).

## Rules for the proxy setup

- The egress proxy listens on **127.0.0.1 only**. On any other address it is an open proxy that anyone can use
  with your credentials.
- Request headers (for example `Authorization`) pass through the proxy unchanged; the proxy adds TLS only.
- Streams (Server-Sent Events) need the proxy to forward bytes at once (Caddy: `flush_interval -1`).

## Not ruled out

If a real need appears that a proxy cannot meet (for example a single binary that must call https with
nothing else installed), revisit with that case in hand. The choice would then be between linking the
system's TLS library and embedding a small one, and certificate verification must be on by default.
