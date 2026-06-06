# Frontend Staging Browser Smoke Report

## Layer

TRAINER-PLATFORM-MVP-007B-FIX-FRONTEND-STAGING-API-BUILD-CONTRACT

## Date

2026-06-06

## Environment

| Service | URL |
|---------|-----|
| Frontend | https://frontend-staging-4146.up.railway.app |
| Backend | https://backend-staging-0487.up.railway.app |

## Test Results

### 1. Registration Flow

| Check | Result |
|-------|--------|
| Registration page loads | ✅ |
| Form fills (name, email, password, confirm) | ✅ |
| POST to external backend (not localhost) | ✅ |
| Target URL | `https://backend-staging-0487.up.railway.app/api/v1/auth/register` |
| HTTP status | 201 |
| CORS preflight | ✅ OPTIONS 200 |
| Redirect after success | ✅ Redirected to /domains |

### 2. Login Flow

| Check | Result |
|-------|--------|
| Login page loads | ✅ |
| Logout works | ✅ |
| Form fills (email, password) | ✅ |
| POST to external backend (not localhost) | ✅ |
| Target URL | `https://backend-staging-0487.up.railway.app/api/v1/auth/login` |
| HTTP status | 200 |
| CORS preflight | ✅ OPTIONS 200 |
| User profile loaded | ✅ GET /api/v1/me → 200 |
| Redirect after login | ✅ Redirected to /domains |

### 3. Domain Catalog

| Check | Result |
|-------|--------|
| Domains page loads | ✅ |
| Domain data from external backend | ✅ `GET /api/v1/domains` → 200 |
| Domain visible | ✅ "IT" domain displayed |

### 4. Trainer Page

| Check | Result |
|-------|--------|
| Trainer page loads | ✅ |
| Trainer data from external backend | ✅ `GET /api/v1/trainers/qa-engineer-interview-trainer` → 200 |
| Trainer name visible | ✅ "QA Engineer Interview Trainer" |
| Enroll button visible | ✅ "Записаться на курс" |

### 5. Network Request Security

| Check | Result |
|-------|--------|
| Requests to localhost:8000 | ✅ None observed |
| Requests to localhost | ✅ None observed |
| Requests to 127.0.0.1 | ✅ None observed |
| All API calls to external backend | ✅ Confirmed |

## Verdict

**ALL CHECKS PASSED** — Browser flow is fully operational over the external
backend URL. No localhost references in any request.
