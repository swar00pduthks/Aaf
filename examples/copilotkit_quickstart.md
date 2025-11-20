# CopilotKit Integration Quickstart

## ✅ AAF now includes a working CopilotKit endpoint!

The `/api/copilotkit` endpoint is **already running** in your AAF FastAPI server.

---

## 🚀 How to Use It

### Option 1: Test with cURL

```bash
# Send a message to the CopilotKit endpoint
curl -X POST http://localhost:5000/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all users"}'

# Response: Server-Sent Events (SSE) stream
data: {"type": "message", "role": "assistant", "content": "Processing: Show me all users"}

data: {"type": "state_patch", "op": "merge", "path": "/progress", "value": {"current_node": "parse_intent", "percentage": 33}}

data: {"type": "message", "role": "assistant", "content": "```sql\nSELECT * FROM users\n```"}

data: {"type": "done"}
```

---

### Option 2: Integrate with React App

**Step 1: Install CopilotKit**

```bash
npm install @copilotkit/react-core @copilotkit/react-ui
```

**Step 2: Wrap Your App**

```tsx
// App.tsx
import { CopilotKit } from '@copilotkit/react-core';
import { CopilotSidebar } from '@copilotkit/react-ui';
import '@copilotkit/react-ui/styles.css';

function App() {
  return (
    <CopilotKit 
      runtimeUrl="http://localhost:5000/api/copilotkit"
      agent="aaf_agent"
    >
      <YourApp />
      <CopilotSidebar 
        defaultOpen={true}
        labels={{
          title: "AAF Assistant",
          initial: "Ask me anything about your data!"
        }}
      />
    </CopilotKit>
  );
}
```

**Step 3: Run Your App**

```bash
npm run dev
```

You'll see a beautiful chat sidebar powered by AAF! 🎉

---

### Option 3: Use Different UI Components

**Chat Popup (Floating Widget)**

```tsx
import { CopilotPopup } from '@copilotkit/react-ui';

<CopilotKit runtimeUrl="http://localhost:5000/api/copilotkit">
  <YourApp />
  <CopilotPopup 
    labels={{
      title: "Need Help?",
      initial: "Hi! I'm your AAF assistant."
    }}
  />
</CopilotKit>
```

**Full Chat Interface**

```tsx
import { CopilotChat } from '@copilotkit/react-ui';

<CopilotKit runtimeUrl="http://localhost:5000/api/copilotkit">
  <div style={{ display: 'flex', height: '100vh' }}>
    <YourApp />
    <CopilotChat 
      labels={{
        title: "AAF Chat",
        initial: "How can I help you today?"
      }}
    />
  </div>
</CopilotKit>
```

---

## 🎨 Customize the Theme

AAF supports multiple themes. Update your React component:

```tsx
<CopilotKit 
  runtimeUrl="http://localhost:5000/api/copilotkit"
  agent="aaf_agent"
>
  <style>{`
    /* Use AAF Dark Theme */
    .copilot-sidebar {
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    .copilot-message {
      color: #e0e0e0;
    }
  `}</style>
  
  <CopilotSidebar defaultOpen={true} />
</CopilotKit>
```

Or use AAF's theme CSS:

```bash
# Get theme CSS from AAF
curl http://localhost:5000/api/themes/dark > dark-theme.css
```

---

## 📋 What Works Out of the Box

✅ **Chat Workflow** - Routes to SQL, MCP tools, or autonomous agents  
✅ **Server-Sent Events** - Real-time streaming responses  
✅ **AG-UI Protocol** - Compatible with CopilotKit components  
✅ **Progress Tracking** - Shows which nodes are executing  
✅ **Error Handling** - Graceful error messages  
✅ **CORS Enabled** - Works with React dev servers  

---

## 🔧 Advanced: Custom Agent

To use a different AAF workflow with CopilotKit, modify `api.py`:

```python
from my_workflows import my_custom_workflow

@app.post("/api/copilotkit")
async def copilotkit_endpoint(request: CopilotKitRequest):
    adapter = AAFAGUIAdapter(
        workflow=my_custom_workflow,  # ← Change this
        agent_name="my_agent"
    )
    
    async def event_stream():
        async for event in adapter.stream_events(request.message):
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

---

## 🎯 Example: E-commerce Assistant

```tsx
// React component
import { CopilotKit, useCopilotAction } from '@copilotkit/react-core';
import { CopilotSidebar } from '@copilotkit/react-ui';

function EcommerceApp() {
  const [cart, setCart] = useState([]);
  
  // Allow AAF to add items to cart
  useCopilotAction({
    name: "addToCart",
    description: "Add a product to the shopping cart",
    parameters: [
      { name: "productId", type: "string", description: "Product ID" },
      { name: "quantity", type: "number", description: "Quantity" }
    ],
    handler: async ({ productId, quantity }) => {
      setCart(prev => [...prev, { productId, quantity }]);
      return { success: true };
    }
  });
  
  return (
    <CopilotKit runtimeUrl="http://localhost:5000/api/copilotkit">
      <div className="app">
        <h1>My Store</h1>
        <ProductList />
        <Cart items={cart} />
      </div>
      
      <CopilotSidebar 
        labels={{
          title: "Shopping Assistant",
          initial: "Hi! I can help you find products and manage your cart."
        }}
      />
    </CopilotKit>
  );
}
```

**User:** "Add 2 blue t-shirts to my cart"  
**AAF:** Analyzes intent → Searches products → Calls `addToCart` action → Confirms

---

## 📚 API Reference

### Endpoint

```
POST /api/copilotkit
```

### Request Body

```json
{
  "message": "User's message",
  "threadId": "optional-thread-id",
  "agentName": "aaf_agent"
}
```

### Response

Server-Sent Events stream with AG-UI protocol messages:

```json
data: {"type": "message", "role": "assistant", "content": "..."}
data: {"type": "state_patch", "op": "merge", "path": "/progress", "value": {...}}
data: {"type": "done"}
```

---

## 🎉 Summary

**Before:** Adapter existed, but no endpoint = doesn't work  
**Now:** `/api/copilotkit` endpoint is **live and working**!

Just point CopilotKit to `http://localhost:5000/api/copilotkit` and you're done! 🚀

---

## 🔗 Resources

- [CopilotKit Docs](https://docs.copilotkit.ai/)
- [AAF Documentation](../replit.md)
- [Chat Workflow Example](./chat_client_workflow.py)
- [Theme Customization](./theme_customization_demo.py)
