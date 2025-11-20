# Personal Finance Assistant - React UI

Beautiful React frontend with CopilotKit integration for the AAF Personal Finance Agent.

## Features

✅ **Beautiful Dashboard** - Real-time financial overview  
✅ **CopilotKit Integration** - AI chat sidebar  
✅ **Responsive Design** - Works on all devices  
✅ **Real-time Data** - Fetches from AAF backend  
✅ **Interactive Stats** - Income, expenses, savings, categories  

## Quick Start

### 1. Install Dependencies

```bash
cd examples/personal_finance_agent/frontend
npm install
```

### 2. Start Backend (Terminal 1)

```bash
cd examples/personal_finance_agent
python finance_api.py
```

Backend runs on: `http://localhost:5001`

### 3. Start Frontend (Terminal 2)

```bash
cd examples/personal_finance_agent/frontend
npm run dev
```

Frontend runs on: `http://localhost:5000`

### 4. Open Browser

Navigate to: `http://localhost:5000`

You'll see:
- 📊 Financial dashboard with stats
- 💬 AI chat sidebar (CopilotKit)
- 📈 Spending categories
- 🎯 Quick action buttons

## What You Can Do

### Use the Dashboard
- View income, expenses, and savings
- See spending breakdown by category
- Check savings rate

### Chat with AI Assistant
Ask questions like:
- "I spent $50 on groceries"
- "Show me my spending summary"
- "How can I save more money?"
- "What should I invest in?"

The AI uses:
- **MCP tools** for expense tracking
- **Autonomous agents** for analysis
- **A2A delegation** for investment advice

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **CopilotKit** - AI chat interface
- **Lucide React** - Icons
- **AAF Backend** - AI agent framework

## Project Structure

```
frontend/
├── index.html                    # HTML entry point
├── package.json                  # Dependencies
├── vite.config.js                # Vite configuration
├── src/
│   ├── main.jsx                  # React entry point
│   ├── App.jsx                   # Main app with CopilotKit
│   ├── index.css                 # Global styles
│   └── components/
│       └── FinanceDashboard.jsx  # Dashboard component
```

## Configuration

### Backend Proxy

Vite proxies `/api` requests to the backend:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5001',
      changeOrigin: true
    }
  }
}
```

### CopilotKit Setup

```jsx
// App.jsx
<CopilotKit 
  runtimeUrl="/api/copilotkit"
  agent="finance_assistant"
>
  <FinanceDashboard />
  <CopilotSidebar defaultOpen={true} />
</CopilotKit>
```

## Customization

### Change Theme Colors

Edit `src/index.css`:

```css
/* Change gradient background */
body {
  background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
}

/* Change accent color */
.stat-card.income .stat-icon { color: #your-color; }
```

### Modify Dashboard Stats

Edit `src/components/FinanceDashboard.jsx`:

```jsx
// Add more stat cards
<div className="stat-card custom">
  <div className="stat-header">
    <YourIcon className="stat-icon" />
    <span className="stat-label">Your Metric</span>
  </div>
  <div className="stat-value">$1,234</div>
</div>
```

### Customize AI Assistant

Edit `src/App.jsx`:

```jsx
<CopilotSidebar
  labels={{
    title: "Your Custom Title",
    initial: "Your custom welcome message"
  }}
/>
```

## Build for Production

```bash
npm run build
```

Output in `dist/` directory.

Deploy to:
- Vercel
- Netlify
- Replit
- Any static host

## Troubleshooting

### Backend not connecting?

Make sure backend is running:
```bash
python finance_api.py
```

Check console for errors:
- Press F12 in browser
- Look at Network tab

### CopilotKit not working?

1. Check backend endpoint: `http://localhost:5001/api/copilotkit`
2. Verify proxy in `vite.config.js`
3. Check browser console for errors

### Styles not loading?

1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R)
3. Check `index.css` imports

## Next Steps

- [ ] Connect to real database
- [ ] Add authentication
- [ ] Create expense entry form
- [ ] Add charts and graphs
- [ ] Mobile app version

## Learn More

- [CopilotKit Docs](https://docs.copilotkit.ai/)
- [React Docs](https://react.dev/)
- [Vite Docs](https://vitejs.dev/)
- [AAF Framework](../../README.md)

---

**Built with AAF + CopilotKit** 🚀
