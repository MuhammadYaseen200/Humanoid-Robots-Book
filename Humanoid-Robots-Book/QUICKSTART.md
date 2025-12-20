# Physical AI Textbook Platform - Quick Start Guide

**Platform Status**: ✅ **READY TO LAUNCH**
**Last Updated**: 2025-12-19

---

## 🚀 One-Command Launch

```bash
./scripts/start_all.sh
```

This script will:
1. ✅ Start Backend (FastAPI on port 8000)
2. ✅ Verify backend health check
3. ✅ Start Frontend (Docusaurus on port 3000)
4. ✅ Open your browser to http://localhost:3000

**To Stop**: Press `Ctrl+C` (both servers will shut down gracefully)

---

## 📋 Prerequisites (Already Installed ✅)

### Frontend Dependencies
- ✅ Node.js >= 20.0
- ✅ npm packages (1,444 packages installed)
- ✅ Docusaurus v3.9.2
- ✅ React v18.2.0
- ✅ Tailwind CSS v3.3.0
- ✅ Playwright v1.57.0 (with Chromium browser)

### Backend Dependencies
- ✅ Python 3.12
- ✅ FastAPI
- ✅ Uvicorn
- ✅ AsyncPG (Postgres driver)
- ✅ Qdrant Client (Vector DB)
- ✅ Google Gemini API
- ✅ Python-JOSE (JWT)
- ✅ Passlib + Bcrypt (Password hashing)

---

## 🌐 Platform URLs

After running `./scripts/start_all.sh`:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Main textbook website |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | Backend health status |

---

## 🔧 Manual Launch (Alternative)

### Option 1: Launch Both Servers in Separate Terminals

**Terminal 1 - Backend**:
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
npm start
```

### Option 2: Background Backend, Foreground Frontend

```bash
# Start backend in background
cd backend && uvicorn src.main:app --reload --port 8000 &
cd ..

# Wait for backend to be ready
sleep 5

# Start frontend in foreground
npm start
```

---

## 🧪 Testing the 50-Point Feature

### Backend API Tests (Already Passed ✅)

```bash
cd backend
python tests/api/test_auth_api.py
```

**Expected Output**: ✅ ALL 6 TESTS PASSED
- Signup with hardware profiling
- Signin authentication
- Profile retrieval
- Profile update
- Password validation
- Duplicate email prevention

### Frontend Manual Testing

1. **Navigate to**: http://localhost:3000
2. **Click**: "Sign Up" button (top-right navbar)
3. **Step 1**: Fill basic credentials
   - Name: "Test Student"
   - Email: `test-${timestamp}@example.com`
   - Password: "StrongPass1!"
   - Confirm Password: "StrongPass1!"
   - Click "Next: Hardware Profile"

4. **Step 2**: Fill hardware profile (THE 50-POINT FEATURE)
   - GPU Type: "NVIDIA RTX 4090"
   - RAM Capacity: "More than 32GB"
   - Coding Languages: Click "Python" and "C++"
   - Robotics Experience: "Beginner (0-1 years)"
   - Click "Create Account"

5. **Verify**:
   - ✅ Success message displays
   - ✅ Modal closes after 2 seconds
   - ✅ Navbar shows your name: "Test Student"
   - ✅ Navbar shows GPU: "NVIDIA RTX 4090"
   - ✅ "Sign Up" button replaced with "Sign Out"

6. **Verify JWT Token**:
   - Open DevTools (F12) → Console
   - Run: `localStorage.getItem('auth_token')`
   - Copy token to https://jwt.io
   - Confirm payload contains:
     - `gpu_type`: "NVIDIA RTX 4090"
     - `ram_capacity`: "More than 32GB"
     - `coding_languages`: ["Python", "C++"]
     - `robotics_experience`: "Beginner (0-1 years)"

---

## 📁 Project Structure

```
Humanoid-Robots-Book/
├── scripts/
│   └── start_all.sh          ← Unified launch script
├── backend/
│   ├── src/
│   │   ├── main.py           ← FastAPI app entry point
│   │   ├── routers/
│   │   │   ├── auth.py       ← Authentication endpoints
│   │   │   └── profile.py    ← Profile endpoints
│   │   ├── models/
│   │   │   └── auth.py       ← Pydantic models
│   │   ├── utils/
│   │   │   ├── jwt.py        ← JWT utilities
│   │   │   └── password.py   ← Password hashing
│   │   └── dependencies/
│   │       └── auth.py       ← Auth middleware
│   ├── db/
│   │   └── migrations/
│   │       └── 003_user_profile_hardware.sql
│   ├── tests/
│   │   └── api/
│   │       └── test_auth_api.py
│   └── requirements.txt
├── src/
│   ├── theme/
│   │   ├── Root.tsx          ← AuthProvider wrapper
│   │   └── NavbarItem/
│   │       ├── index.tsx     ← Navbar wrapper
│   │       └── AuthButton.tsx ← Auth UI component
│   ├── components/
│   │   └── Auth/
│   │       ├── SignupModal.tsx ← 2-step signup wizard
│   │       └── SigninModal.tsx ← Signin form
│   └── context/
│       └── AuthContext.tsx   ← JWT state management
├── tests/
│   ├── e2e/
│   │   └── auth-flow.spec.ts ← Playwright E2E tests
│   ├── TESTING_GUIDE.md      ← Manual testing checklist
│   ├── TEST_RESULTS.md       ← Test execution results
│   └── E2E_TEST_REPORT.md    ← Comprehensive test report
├── package.json
├── docusaurus.config.js
└── QUICKSTART.md            ← This file
```

---

## 🔍 Troubleshooting

### Backend Won't Start

**Issue**: `uvicorn: command not found`
**Solution**:
```bash
cd backend
pip3 install --break-system-packages -r requirements.txt
```

**Issue**: Database connection error
**Solution**: Check `backend/.env` has correct `DATABASE_URL`

### Frontend Won't Start

**Issue**: `'docusaurus' is not recognized`
**Solution**:
```bash
npm install
```

**Issue**: Port 3000 already in use
**Solution**:
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm start -- --port 3001
```

### Both Servers Running But Can't Access

**Issue**: Firewall blocking ports
**Solution**: Allow ports 3000 and 8000 in firewall

**Issue**: WSL2 network issues
**Solution**:
```bash
# In Windows PowerShell (Admin)
netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=localhost
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=localhost
```

---

## 🎯 Hackathon Submission Checklist

### Feature Implementation
- [x] Base textbook (Docusaurus)
- [x] Better-Auth signup/signin (FastAPI + JWT)
- [x] **Hardware profiling** (GPU, RAM, languages, experience) ← **50 POINTS**
- [x] Profile storage in Neon Postgres
- [x] JWT with embedded hardware claims
- [x] 2-step signup wizard UI
- [x] Navbar integration (authenticated state)

### Testing
- [x] Backend API tests (6/6 passed)
- [x] Manual frontend testing guide created
- [x] E2E test spec written (Playwright)
- [x] Test results documented

### Documentation
- [x] QUICKSTART.md (this file)
- [x] SETUP_STATUS.md (environment status)
- [x] NAVBAR_INTEGRATION.md (integration guide)
- [x] tests/TESTING_GUIDE.md (manual testing)
- [x] tests/TEST_RESULTS.md (test results)
- [x] tests/E2E_TEST_REPORT.md (comprehensive report)

### Deployment
- [ ] Record demo video (<90 seconds)
- [ ] Show signup flow with hardware profiling
- [ ] Verify JWT token in DevTools
- [ ] Highlight 50-point feature

---

## 📊 Feature Scoring

| Feature | Points | Status |
|---------|--------|--------|
| Base Textbook + RAG | 100 | ✅ Implemented |
| Reusable Intelligence (Agents/Skills) | +50 | ✅ Implemented |
| **Better-Auth + Hardware Profiling** | **+50** | ✅ **COMPLETE** |
| Content Personalization | +50 | ⏳ Pending |
| Urdu Translation | +50 | ⏳ Pending |

**Current Total**: 200 points (Base + 2 bonus features)
**Potential Maximum**: 300 points

---

## 🏆 Success Criteria

✅ **All criteria met**:
- [x] Both servers start successfully
- [x] Backend health check passes
- [x] Frontend loads without errors
- [x] Signup flow works end-to-end
- [x] Hardware profiling data collected
- [x] JWT tokens contain profile claims
- [x] Navbar shows authenticated state
- [x] Sign out functionality works

---

## 🚀 Ready to Launch!

**Run this command to start the platform**:

```bash
./scripts/start_all.sh
```

Then navigate to **http://localhost:3000** and test the signup flow with hardware profiling!

---

**Platform Status**: ✅ **READY FOR HACKATHON SUBMISSION**
**Next Step**: Record demo video (<90 seconds) showing the 50-point feature in action!
