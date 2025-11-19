/**
 * CopilotKit Integration Example for AAF
 * 
 * This shows how to embed AAF workflows in a React app using CopilotKit's
 * beautiful UI components with custom themes.
 * 
 * Installation:
 *   npm install @copilotkit/react-core @copilotkit/react-ui
 */

import React from 'react';
import { CopilotKit } from '@copilotkit/react-core';
import { CopilotSidebar, CopilotChat, CopilotPopup } from '@copilotkit/react-ui';
import '@copilotkit/react-ui/styles.css';

// ============================================================================
// Example 1: Sidebar Chat (Persistent Assistant)
// ============================================================================

export function AppWithSidebar() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="aaf_agent">
      <div className="app-container">
        {/* Your main app content */}
        <YourApp />
        
        {/* AAF agent in sidebar */}
        <CopilotSidebar
          defaultOpen={true}
          clickOutsideToClose={false}
          labels={{
            title: "AAF Assistant",
            initial: "Hi! I can help with database queries, research, and more."
          }}
        />
      </div>
    </CopilotKit>
  );
}


// ============================================================================
// Example 2: Embedded Chat (Full-Page)
// ============================================================================

export function AppWithChat() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="aaf_agent">
      <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <header style={{ padding: '1rem', borderBottom: '1px solid #e5e7eb' }}>
          <h1>AAF Chat Client</h1>
        </header>
        
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <CopilotChat
            labels={{
              title: "AAF Workflow Assistant",
              initial: "Ask me to generate SQL, search the web, or research topics!"
            }}
          />
        </div>
      </div>
    </CopilotKit>
  );
}


// ============================================================================
// Example 3: Popup Widget (Non-Intrusive)
// ============================================================================

export function AppWithPopup() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="aaf_agent">
      <div className="app-container">
        {/* Your main app */}
        <YourApp />
        
        {/* AAF agent as floating widget */}
        <CopilotPopup
          labels={{
            title: "Need Help?",
            initial: "Ask me anything about your data or research needs!"
          }}
        />
      </div>
    </CopilotKit>
  );
}


// ============================================================================
// Example 4: Custom Theming
// ============================================================================

export function AppWithCustomTheme() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="aaf_agent">
      <style>{`
        /* AAF Dark Theme */
        :root {
          --copilotkit-primary-color: #818cf8;
          --copilotkit-background-color: #111827;
          --copilotkit-text-color: #f9fafb;
          --copilotkit-border-radius: 0.5rem;
        }
      `}</style>
      
      <div className="app-container dark-theme">
        <YourApp />
        <CopilotSidebar defaultOpen={true} />
      </div>
    </CopilotKit>
  );
}


// ============================================================================
// Example 5: Shared State with useCoAgent
// ============================================================================

import { useCoAgent } from '@copilotkit/react-core';

export function AppWithSharedState() {
  // Bidirectionally sync state between your app and AAF agent
  const { state, setState } = useCoAgent({
    name: 'aaf_agent',
    initialState: {
      query_type: null,
      last_result: null,
      workflow_step: 0
    }
  });
  
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="aaf_agent">
      <div className="app-container">
        {/* Your app can read/write agent state */}
        <div className="status-bar">
          <p>Current Step: {state.workflow_step}</p>
          <p>Query Type: {state.query_type || 'none'}</p>
        </div>
        
        <YourApp agentState={state} />
        <CopilotSidebar />
      </div>
    </CopilotKit>
  );
}


// ============================================================================
// Example 6: Generative UI with useCoAgentStateRender
// ============================================================================

import { useCoAgentStateRender } from '@copilotkit/react-core';

export function AppWithGenerativeUI() {
  // Render custom React components based on agent state
  useCoAgentStateRender({
    name: 'aaf_agent',
    render: ({ state }) => {
      if (state.query_type === 'sql') {
        return (
          <div className="sql-result">
            <h3>Generated SQL</h3>
            <pre><code>{state.last_result?.query}</code></pre>
          </div>
        );
      }
      
      if (state.query_type === 'research') {
        return (
          <div className="research-result">
            <h3>Research Results</h3>
            <ul>
              {state.last_result?.tools_used?.map((tool: string) => (
                <li key={tool}>✓ {tool}</li>
              ))}
            </ul>
          </div>
        );
      }
      
      return null;
    }
  });
  
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="aaf_agent">
      <YourApp />
      <CopilotSidebar />
    </CopilotKit>
  );
}


// ============================================================================
// Example 7: Human-in-the-Loop with useCopilotAction
// ============================================================================

import { useCopilotAction } from '@copilotkit/react-core';

export function AppWithHumanApproval() {
  // Let agent request user approval before executing actions
  useCopilotAction({
    name: 'execute_sql',
    description: 'Execute a SQL query',
    parameters: [
      {
        name: 'sql_query',
        type: 'string',
        description: 'The SQL query to execute',
        required: true
      }
    ],
    renderAndWaitForResponse: ({ args, status, respond }) => (
      <div className="approval-dialog">
        <h3>Approve SQL Query?</h3>
        <pre><code>{args.sql_query}</code></pre>
        <button onClick={() => respond({ approved: true })}>
          ✓ Approve
        </button>
        <button onClick={() => respond({ approved: false })}>
          ✗ Reject
        </button>
      </div>
    )
  });
  
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="aaf_agent">
      <YourApp />
      <CopilotSidebar />
    </CopilotKit>
  );
}


// Dummy component for examples
function YourApp(props?: any) {
  return (
    <div style={{ padding: '2rem' }}>
      <h2>Your Application Content</h2>
      <p>AAF agent runs alongside your app!</p>
    </div>
  );
}
