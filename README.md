# MobilePay

A mobile-money wallet app for Cameroon (MTN & Orange), with pay-ins (collections)
and pay-outs (disbursements) routed through **PawaPay**.

```
MobilePay/
├── Backend/    Flask + PostgreSQL API (JWT auth, wallet, transactions, PawaPay)
└── Frontend/   Expo / React Native app (expo-router)
```

## How the two connect

The frontend talks to the backend over HTTP at `EXPO_PUBLIC_API_URL`, which must
point at the Flask server and **end with `/api`** (all blueprints are mounted
under `/api`). Auth is a JWT bearer token returned by `/api/auth/login` and sent
on every request via the `Authorization` header.

Payments are routed through PawaPay:

| App action            | Endpoint                  | PawaPay op   | Effect          |
|-----------------------|---------------------------|--------------|-----------------|
| **Top up** (Wallet)   | `POST /api/pawapay/collect`  | collection   | credits wallet  |
| **Withdraw** (Wallet) | `POST /api/pawapay/disburse` | disbursement | debits wallet   |
| **Send money**        | `POST /api/transfer`         | internal P2P | wallet → wallet |

In local dev the payment calls use `polling: true`, so the backend polls PawaPay
for the final status and returns it in one request (webhooks aren't reachable on
localhost). PawaPay is configured for **sandbox** in `Backend/.env`.

---

## Running the backend

Requires Python 3.11+ and a running PostgreSQL with a `mobilepay` database
(credentials in `Backend/.env`).

```bash
cd Backend
venv/Scripts/python.exe -m pip install -r requirements.txt   # first time
venv/Scripts/python.exe -m flask db upgrade                  # apply migrations
venv/Scripts/python.exe app.py                               # serves http://127.0.0.1:5000
```

To reach the backend from a **real phone**, bind to all interfaces:

```bash
venv/Scripts/python.exe -m flask --app app run --host=0.0.0.0 --port=5000
```

## Running the frontend

Requires Node 18+.

```bash
cd Frontend
npm install            # first time — needs a stable connection to the npm registry
npm run web            # browser  → http://localhost:8081
# or: npm start        # then press i (iOS sim) / scan QR with Expo Go
```

> If `npm install` fails with `ECONNRESET`/`network aborted`, it's a registry
> connectivity hiccup, not a project problem — re-run it (npm resumes from cache).
> A clean install must finish before `npm run web` / `npm start` will work.

### Pointing the app at the backend

Edit `Frontend/.env`:

- **Browser / iOS simulator:** `EXPO_PUBLIC_API_URL=http://localhost:5000/api`
- **Real phone (Expo Go):** use this computer's LAN IP, e.g.
  `EXPO_PUBLIC_API_URL=http://192.168.1.42:5000/api`
  (find it with `ipconfig`; phone and PC must share the same Wi-Fi, and the
  backend must run with `--host=0.0.0.0`).

After changing `.env`, restart Expo with `npm run start:clear`.

CORS is open for `/api/*` in dev (see `Backend/app.py`); restrict
`CORS_ORIGINS` in `.env` for production.

## Quick smoke test

1. Start backend, then frontend.
2. Register an account, then log in.
3. On **Wallet**, tap **Top up**, enter an MTN/Orange number + amount → wallet is
   credited once the sandbox collection completes.
4. Tap **Withdraw** to pay out from the wallet balance.
