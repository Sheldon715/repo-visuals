# Pulsecheck

A tiny CLI that checks health endpoints and prints a clean status summary.

## Install

```bash
npm install -g pulsecheck-cli
```

## Use

```bash
pulsecheck https://api.example.com/health https://status.example.com/ping
```

Pulsecheck exits with a non-zero status when an endpoint is unavailable, so it can be used in local scripts and CI jobs.
