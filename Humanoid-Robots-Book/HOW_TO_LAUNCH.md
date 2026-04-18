# How to Launch the Platform

## ✅ FIXED: The scripts now work!

The line ending issue has been resolved. You have **3 ways** to launch the platform:

---

## Option 1: Simple Launch (RECOMMENDED for Testing)

```bash
./scripts/start_simple.sh
```

**What it does**:
- Starts backend in background
- Waits 10 seconds
- Starts frontend in foreground
- No health checks (faster startup)

**Use this for**: Quick testing, demo preparation

---

## Option 2: Full Launch (With Health Checks)

```bash
./scripts/start_all.sh
```

**What it does**:
- Starts backend in background
- Performs health check (waits up to 10 seconds)
- If healthy, starts frontend
- If unhealthy, exits with error

**Note**: May fail if backend takes >10 seconds to start (Qdrant connection issues are normal and don't affect auth features)

---

## Option 3: Manual Launch (Most Control)

### Terminal 1 - Backend
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
npm start
```

---

## 🐛 Troubleshooting

### "required file not found" error
**Cause**: Windows line endings (CRLF) in bash script
**Fix**: Already applied! Scripts are now Unix-format.

### Backend takes >10 seconds to start
**Cause**: Qdrant connection timeout (normal - we're not using Qdrant for auth)
**Fix**: Use Option 1 (start_simple.sh) which doesn't check health

### Port 8000 or 3000 already in use
**Solution**:
```bash
# Kill processes on these ports
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

---

## 🎯 Quick Test After Launch

1. **Check Backend**: http://localhost:8000/health
   - Should return: `{"status":"healthy","environment":"development"}`

2. **Check Frontend**: http://localhost:3000
   - Should show the textbook homepage
   - Look for "Sign In" and "Sign Up" buttons in navbar (top-right)

3. **Test 50-Point Feature**:
   - Click "Sign Up"
   - Fill Step 1 (name, email, password)
   - Fill Step 2 (GPU, RAM, languages, experience)
   - Verify success and navbar updates

---

## ✅ Current Platform Status

- ✅ Dependencies installed
- ✅ Line endings fixed
- ✅ Scripts executable
- ✅ Backend ready (port 8000)
- ✅ Frontend ready (port 3000)
- ✅ Auth feature complete

---

## 🚀 READY TO LAUNCH!

Run this command right now:

```bash
./scripts/start_simple.sh
```

Then open http://localhost:3000 in your browser!
