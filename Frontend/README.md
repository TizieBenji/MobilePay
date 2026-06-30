# MobilePay FrontEnd — Expo React Native

MobilePay FrontEnd is a clean, integration-ready mobile application for a Cameroon mobile money interoperability project. The app is designed for the backend described in the project specification: user registration, login, KYC upload, wallet display, money transfer, transaction history, profile management, and logout.

## 1. What this frontend contains

- Expo React Native mobile app
- Expo Router file-based navigation
- TypeScript structure
- Authentication context
- AsyncStorage token/session persistence
- Axios API client with JWT bearer token injection
- Reusable UI components
- Registration, login, forgot password screens
- KYC upload screen for ID front, ID back, selfie, national ID, and address
- Dashboard with wallet summary and recent transactions
- Transfer workflow compatible with the Flask backend payload
- Wallet screen
- Transaction history screen
- Profile screen with logout
- Mock fallback data while backend endpoints are not ready

## 2. Recommended project position

Place this folder like this:

```text
MobilePay/
├── Backend/
└── FrontEnd/
```

This archive already represents the `FrontEnd` folder.

## 3. Install and run

```bash
cd FrontEnd
npm install
npx expo start
```

Open the app using Expo Go on Android/iOS or an emulator.

## 4. Environment configuration

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Then set your Flask API URL:

```env
EXPO_PUBLIC_API_URL=http://127.0.0.1:5000/api
```

For Android emulator, you may need:

```env
EXPO_PUBLIC_API_URL=http://10.0.2.2:5000/api
```

For a real phone, use your computer LAN IP, for example:

```env
EXPO_PUBLIC_API_URL=http://192.168.1.20:5000/api
```

## 5. Backend endpoint mapping

The frontend expects these backend routes:

| Screen / action | Method | Endpoint |
|---|---:|---|
| Register | POST | `/register` |
| Login | POST | `/login` |
| Logout | POST | `/logout` |
| Forgot password | POST | `/forgot-password` |
| Get profile | GET | `/profile` |
| Update profile | PUT | `/profile` |
| Upload KYC | POST | `/kyc/upload` |
| Get KYC status | GET | `/kyc/status` |
| Get wallet | GET | `/wallet` |
| Get wallet balance | GET | `/wallet/balance` |
| Transfer money | POST | `/transfer` |
| Transfer status | GET | `/transfer/status/:id` |
| Transaction history | GET | `/transactions` |

## 6. Transfer payload

The transfer screen sends this payload:

```json
{
  "sender": "670123456",
  "receiver": "690123456",
  "amount": 5000
}
```

The UI also detects Orange or MTN from the phone number prefix before sending.

## 7. KYC payload

The KYC screen uses `multipart/form-data` with:

- `national_id`
- `residential_address`
- `id_front`
- `id_back`
- `selfie`

The image files are selected using Expo Image Picker.

## 8. Frontend architecture

```text
FrontEnd/
├── app/
│   ├── _layout.tsx
│   ├── index.tsx
│   ├── (auth)/
│   │   ├── _layout.tsx
│   │   ├── welcome.tsx
│   │   ├── login.tsx
│   │   ├── register.tsx
│   │   └── forgot-password.tsx
│   ├── (onboarding)/
│   │   └── kyc.tsx
│   └── (tabs)/
│       ├── _layout.tsx
│       ├── dashboard.tsx
│       ├── wallet.tsx
│       ├── transfer.tsx
│       ├── transactions.tsx
│       └── profile.tsx
├── src/
│   ├── components/
│   ├── constants/
│   ├── context/
│   ├── hooks/
│   ├── services/
│   ├── storage/
│   ├── types/
│   └── utils/
```

## 9. Integration strategy

The backend integration is centralized in `src/services/api/`. When your Flask backend is ready, you only need to adjust endpoint names or response shapes in these service files rather than editing every screen.

The authentication token is saved in `src/storage/tokenStorage.ts` and injected into every protected request in `src/services/api/client.ts`.

## 10. Suggested next steps

1. Start your Flask backend.
2. Confirm `POST /register` returns a user and/or token.
3. Confirm `POST /login` returns an access token.
4. Update `normalizeAuthResponse()` in `src/services/api/auth.ts` if your backend returns a slightly different JSON shape.
5. Test dashboard after implementing `/profile`, `/wallet`, and `/transactions`.
6. Test KYC after implementing file upload handling in Flask.
7. Test transfer after implementing the interoperability engine.
