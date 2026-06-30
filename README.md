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

---

## Testing

The integration was exercised against the **live backend + PawaPay sandbox**,
hitting the exact endpoints/payloads the app's screens send. The wallet ledger
rule held throughout: **balance only moves on `COMPLETED`** — never on `FAILED`
or while still pending.

### Happy path
`register → login → collect (wallet credited) → disburse (wallet debited) → history`
— verified, with balances and transaction history updating correctly.

### Input validation (all rejected, HTTP 400)
| Case | Result |
|------|--------|
| Amount below min (50) | `Minimum amount is 100 XAF` |
| Amount above coarse max (2,000,000) | `Maximum amount is 1,000,000 XAF` |
| Decimal amount (100.5) | `XAF does not support decimal amounts` |
| Invalid / non-mobile phone | `Invalid phone number` |
| Missing amount / phone / empty body | field-specific error |
| **Orange 600k** (over the 500k Orange cap) | `exceeds the maximum … for ORANGE_CMR (500,000 XAF)` |
| Disburse over balance | `Insufficient available balance …` |
| Status with malformed UUID / unknown UUID | 400 / 404 |

### Auth & authorization
Login issues a short-lived **access token (1 h)** plus a long-lived **refresh
token (30 d)**. When the access token expires, the frontend transparently calls
`POST /api/auth/refresh` (refresh token as the Bearer credential) and retries the
original request; only when the refresh token is also expired is the user signed
out. TTLs are configurable via `JWT_ACCESS_TOKEN_EXPIRES_HOURS` /
`JWT_REFRESH_TOKEN_EXPIRES_DAYS`.

| Case | Result |
|------|--------|
| Request with no token | 401 |
| Login wrong password | 401 |
| Login success | returns `token` + `refresh_token` |
| Expired access token + valid refresh token | `/auth/refresh` mints a new access token, request retried |
| `/auth/refresh` with access token (not refresh) | 422 (wrong token type) |
| `/auth/refresh` with expired/invalid refresh token | 401 → client clears session |
| User B reads User A's transaction | 404 (masks existence) |

### Failure paths (PawaPay sandbox test MSISDNs)
Driven through `collect`/`disburse` with `polling: true`; each returned
`pawa_status: FAILED` with the right `failure_code`, and the **wallet was not
moved**:

| MSISDN | Operation | failureCode |
|--------|-----------|-------------|
| 653456789 | deposit | *(COMPLETED — wallet credited)* |
| 653456019 | deposit | PAYER_LIMIT_REACHED |
| 653456029 | deposit | PAYER_NOT_FOUND |
| 693456049 | deposit (Orange) | INSUFFICIENT_BALANCE |
| 653456129 | deposit | NO_CALLBACK → returns "still processing" (202) |
| 653456089 | payout | RECIPIENT_NOT_FOUND |
| 693456099 | payout (Orange) | RECIPIENT_NOT_ALLOWED_TO_RECEIVE |

### Sandbox test numbers (reference)
PawaPay routes the outcome by MSISDN. `…789` always **COMPLETES**; the others
fail with the listed code. `…129` never calls back (stuck `SUBMITTED`) — locally
the polling path times out and the deposit stays pending.

**MTN (`MTN_MOMO_CMR`, `2376534560xx`)**
- Deposit: `…19` PAYER_LIMIT_REACHED · `…29` PAYER_NOT_FOUND · `…39` PAYMENT_NOT_APPROVED · `…69` OTHER_ERROR · `…129` NO_CALLBACK · `…789` COMPLETED
- Payout: `…89` RECIPIENT_NOT_FOUND · `…119` OTHER_ERROR · `…129` NO_CALLBACK · `…789` COMPLETED

**Orange (`ORANGE_CMR`, `2376934560xx`)**
- Deposit: `…19` PAYER_LIMIT_REACHED · `…29` PAYER_NOT_FOUND · `…39` PAYMENT_NOT_APPROVED · `…49` INSUFFICIENT_BALANCE · `…69` OTHER_ERROR · `…129` NO_CALLBACK · `…789` COMPLETED
- Payout: `…99` RECIPIENT_NOT_ALLOWED_TO_RECEIVE · `…119` OTHER_ERROR · `…129` NO_CALLBACK · `…789` COMPLETED

### Not covered
- The rendered React Native UI itself (clicking through screens) — the web build
  bundles cleanly and the API layer is fully proven, but UI interaction wasn't
  automated.
- The production **webhook** flow (HMAC-verified async callbacks); local testing
  used the polling path instead.
