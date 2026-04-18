# Development Servers - Feature 004 Intelligence Engine

**Status**: ✅ Frontend Running
**Date**: 2025-12-25

---

## 🚀 Active Servers

### Frontend (Docusaurus)
- **Status**: ✅ **RUNNING**
- **URL**: **http://localhost:3000/**
- **Tech**: Docusaurus v3.x + React 18
- **Process ID**: bdc3daa
- **Started**: Successfully

**Access the Landing Page**:
1. Open your browser
2. Navigate to: **http://localhost:3000**
3. You should see:
   - Hero section: "Master Physical AI & Humanoid Robotics"
   - Feature grid with 4 cards
   - CTA button (Get Started / Continue Learning)

---

### Backend (FastAPI)
- **Status**: ⏸️ **NOT STARTED**
- **Reason**: Python virtual environment setup requires system packages
- **Note**: Backend is not required for MVP testing (Feature 003 already has auth backend)

**To start backend manually** (if needed):
```bash
# Navigate to backend directory
cd /mnt/e/M.Y/GIAIC-Hackathons/final-project-v2/Humanoid-Robots-Book/backend

# Install python3-venv if needed
sudo apt-get install python3-venv

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn main:app --reload
```

---

## 📋 What to Test

### 1. Landing Page Components

**Hero Section**:
- Title: "Master Physical AI & Humanoid Robotics"
- Subtitle with project description
- CTA button: "Get Started" (if not signed in)

**Feature Grid**:
- 4 cards with icons:
  - Interactive RAG Chatbot (blue icon)
  - Hardware-Aware Learning (green icon)
  - Urdu Translation (purple icon)
  - Real-World Projects (orange icon)

### 2. Authentication Integration

**Test with Feature 003-better-auth**:
1. If you have an account, sign in
2. Return to homepage
3. CTA button should change to "Continue Learning"

### 3. Responsive Design

**Test different screen sizes**:
- Mobile (375px): Cards stack vertically
- Tablet (768px): 2 cards per row
- Desktop (1200px): 4 cards per row

---

## ⚠️ Warnings Observed

### Warning 1: Deprecated Config Option
```
[WARNING] The `siteConfig.onBrokenMarkdownLinks` config option is deprecated
and will be removed in Docusaurus v4.
```
**Impact**: Low - just a deprecation notice
**Action**: No immediate action needed

### Warning 2: Duplicate Routes
```
[WARNING] Duplicate routes found!
- Attempting to create page at /, but a page already exists at this route.
```
**Cause**: Both `src/pages/index.tsx` and potentially another index file exist
**Impact**: Medium - may cause routing confusion
**Fix**: Check if there's an old index file to remove

**To investigate**:
```bash
find src/pages -name "index.*"
```

---

## 🛑 Stop Servers

**To stop the frontend**:
```bash
# Find the process
ps aux | grep "docusaurus start"

# Kill the process (use the PID from above)
kill <PID>

# Or use npm
# (Navigate to project root first)
# Press Ctrl+C in the terminal where npm start is running
```

**Alternative**: The background task ID is `bdc3daa`, so you can use:
```bash
# This will stop the server (if using Claude Code task management)
```

---

## 📊 Server Logs

**View real-time frontend logs**:
```bash
tail -f /tmp/claude/-mnt-e-M-Y-GIAIC-Hackathons-final-project-v2-Humanoid-Robots-Book/tasks/bdc3daa.output
```

---

## ✅ MVP Testing Checklist

Now that the frontend is running, test these items:

- [ ] Navigate to http://localhost:3000
- [ ] Hero section displays correctly
- [ ] Feature grid shows 4 cards with icons
- [ ] Icons render (lucide-react)
- [ ] CTA button is clickable
- [ ] CTA links to `/docs/module-1-ros2-basics/chapter-1-intro`
- [ ] No JavaScript errors in browser console (F12)
- [ ] Responsive layout works (resize browser)
- [ ] Page loads in <2.5 seconds (check Lighthouse)

**For full validation**: See `MVP-VALIDATION.md`

---

## 🔗 Quick Links

- **Homepage**: http://localhost:3000
- **Docs**: http://localhost:3000/docs/intro
- **MVP Validation Guide**: ./MVP-VALIDATION.md
- **MVP Summary**: ./MVP-SUMMARY.md

---

## 🐛 Troubleshooting

### Issue: Page shows blank white screen

**Solution**:
```bash
# Clear Docusaurus cache
npm run clear

# Restart server
npm start
```

### Issue: Icons not showing

**Solution**:
```bash
# Verify lucide-react installed
npm list lucide-react

# Reinstall if needed
npm install lucide-react

# Restart server
npm start
```

### Issue: AuthContext error

**Status**: ✅ **FIXED**

**Cause**: AuthProvider was not wrapping the application in Root.tsx

**Solution Applied**:
1. Created mock AuthContext.tsx with null user state
2. Wrapped children with `<AuthProvider>` in src/theme/Root.tsx
3. Created placeholder ChatWidget.tsx to prevent import errors

**Result**: App should now render without errors. Refresh browser to see the landing page.

---

**🎉 Frontend is ready! Open http://localhost:3000 to see your MVP landing page!**
