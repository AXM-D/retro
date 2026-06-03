# Retro

Active defense platform. Detects attackers, investigates them with OSINT, blocks them — all locally, no cloud, no subscriptions.

Built on [TaQ Engine](https://github.com/AXM-D).

## How it works

1. A sensor catches something — SSH login attempt, HTTP scan, port probe, or a log line you feed it.
2. Retro looks up the attacker using public sources: DNS, WHOIS, geolocation, IP reputation, breach data.
3. A profile is built. Repeat attackers are tracked, scored, and remembered.
4. You block, report, or export. Or let Retro do it automatically.

All data stays on your machine. SQLite. No servers.

## Quick start

```bash
cd retro
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn retro.api.server:app --host 127.0.0.1 --port 8500
```

Open http://127.0.0.1:8500

### Dashboard

```bash
cd ui
npm install
npm run dev
```

Open http://localhost:5173

## What's included

- **Sensors** — SSH honeypot, HTTP honeypot, port scan detector, log importer
- **OSINT** — IP/email/domain/hash/username/phone enrichment via public sources
- **Protection** — Auto-block via iptables/nftables, geo blocking, DNS sinkhole, rate limiting
- **Countermeasures** — Firewall rules, abuse reporting, threat feed export (JSON/STIX), takedown assistance
- **Reporting** — HTML reports, incident timeline
- **Dashboard** — Real-time web UI with event feed, attacker profiles, sensor controls

## Requirements

- Python 3.12+
- Node.js 18+ (for the dashboard)
- Linux recommended (for firewall features)

## License

MIT
