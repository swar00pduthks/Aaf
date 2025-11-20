import { CopilotKit } from '@copilotkit/react-core';
import { CopilotSidebar } from '@copilotkit/react-ui';
import '@copilotkit/react-ui/styles.css';
import FinanceDashboard from './components/FinanceDashboard';

function App() {
  return (
    <CopilotKit 
      runtimeUrl="/api/copilotkit"
      agent="finance_assistant"
    >
      <div className="app-container">
        <FinanceDashboard />
        
        <CopilotSidebar
          defaultOpen={true}
          labels={{
            title: "💰 Finance Assistant",
            initial: "Hi! I'm your personal finance assistant. I can help you:\n\n• Track expenses and income\n• Analyze spending patterns\n• Get budget recommendations\n• Receive investment advice\n\nTry asking: 'Show me my spending summary' or 'How can I save money?'"
          }}
          className="finance-copilot"
        />
      </div>
    </CopilotKit>
  );
}

export default App;
