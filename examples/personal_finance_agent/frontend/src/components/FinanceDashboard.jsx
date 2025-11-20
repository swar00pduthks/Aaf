import { useState, useEffect } from 'react';
import { DollarSign, TrendingUp, PiggyBank, CreditCard, Sparkles } from 'lucide-react';

function FinanceDashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch financial summary from API
    fetch('/api/finance/summary')
      .then(res => res.json())
      .then(data => {
        setSummary(data.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load summary:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="dashboard loading">
        <div className="spinner"></div>
        <p>Loading your financial data...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>
            <Sparkles className="icon" />
            Personal Finance Assistant
          </h1>
          <p className="subtitle">Powered by AAF Framework</p>
        </div>
      </header>

      <div className="stats-grid">
        {/* Income Card */}
        <div className="stat-card income">
          <div className="stat-header">
            <TrendingUp className="stat-icon" />
            <span className="stat-label">Total Income</span>
          </div>
          <div className="stat-value">
            ${summary?.total_income?.toLocaleString() || '0.00'}
          </div>
          <div className="stat-footer">This month</div>
        </div>

        {/* Expenses Card */}
        <div className="stat-card expenses">
          <div className="stat-header">
            <CreditCard className="stat-icon" />
            <span className="stat-label">Total Expenses</span>
          </div>
          <div className="stat-value">
            ${summary?.total_expenses?.toLocaleString() || '0.00'}
          </div>
          <div className="stat-footer">This month</div>
        </div>

        {/* Savings Card */}
        <div className="stat-card savings">
          <div className="stat-header">
            <PiggyBank className="stat-icon" />
            <span className="stat-label">Savings</span>
          </div>
          <div className="stat-value">
            ${summary?.savings?.toLocaleString() || '0.00'}
          </div>
          <div className="stat-footer">
            {summary?.savings_rate?.toFixed(1)}% savings rate
          </div>
        </div>

        {/* Net Worth Card */}
        <div className="stat-card net-worth">
          <div className="stat-header">
            <DollarSign className="stat-icon" />
            <span className="stat-label">Available</span>
          </div>
          <div className="stat-value">
            ${summary?.savings?.toLocaleString() || '0.00'}
          </div>
          <div className="stat-footer">After expenses</div>
        </div>
      </div>

      {/* Spending Categories */}
      {summary?.top_categories && (
        <div className="spending-section">
          <h2>Top Spending Categories</h2>
          <div className="categories-grid">
            {summary.top_categories.map((cat, index) => (
              <div key={index} className="category-card">
                <div className="category-header">
                  <span className="category-name">{cat.category}</span>
                  <span className="category-amount">${cat.amount.toLocaleString()}</span>
                </div>
                <div className="category-bar">
                  <div 
                    className="category-fill"
                    style={{ width: `${cat.percentage}%` }}
                  ></div>
                </div>
                <div className="category-footer">
                  {cat.percentage.toFixed(1)}% of total spending
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="actions-grid">
          <button className="action-btn track-expense">
            <CreditCard />
            <span>Track Expense</span>
          </button>
          <button className="action-btn track-income">
            <TrendingUp />
            <span>Log Income</span>
          </button>
          <button className="action-btn get-advice">
            <PiggyBank />
            <span>Budget Tips</span>
          </button>
          <button className="action-btn invest">
            <DollarSign />
            <span>Invest</span>
          </button>
        </div>
        <p className="helper-text">
          💡 Or ask the AI assistant anything in the sidebar →
        </p>
      </div>
    </div>
  );
}

export default FinanceDashboard;
