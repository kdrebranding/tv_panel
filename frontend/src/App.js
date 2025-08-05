import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============ CONTEXT ============
const AuthContext = React.createContext();

// ============ COMPONENTS ============

// Login Component
const Login = ({ setAuth }) => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [isRegistering, setIsRegistering] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isRegistering ? '/auth/register' : '/auth/login';
      const response = await axios.post(`${API}${endpoint}`, credentials);
      
      if (isRegistering) {
        setError('Administrator utworzony! Możesz się teraz zalogować.');
        setIsRegistering(false);
      } else {
        localStorage.setItem('tv_panel_token', response.data.access_token);
        setAuth(true);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Błąd logowania');
    }
    
    setLoading(false);
  };

  return (
    <div className="login-container">
      <div className="login-form">
        <div className="logo-section">
          <h1>📺 TV Panel</h1>
          <p>System zarządzania klientami IPTV</p>
        </div>
        
        <form onSubmit={handleSubmit}>
          <h2>{isRegistering ? 'Rejestracja' : 'Logowanie'}</h2>
          
          {error && (
            <div className={`alert ${error.includes('utworzony') ? 'alert-success' : 'alert-error'}`}>
              {error}
            </div>
          )}
          
          <div className="form-group">
            <input
              type="text"
              placeholder="Nazwa użytkownika"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              required
            />
          </div>
          
          <div className="form-group">
            <input
              type="password"
              placeholder="Hasło"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              required
            />
          </div>
          
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Ładowanie...' : (isRegistering ? 'Zarejestruj' : 'Zaloguj')}
          </button>
          
          <button 
            type="button" 
            onClick={() => setIsRegistering(!isRegistering)}
            className="btn-link"
          >
            {isRegistering ? 'Masz już konto? Zaloguj się' : 'Pierwszy raz? Zarejestruj się'}
          </button>
        </form>
      </div>
    </div>
  );
};

// Sidebar Component
const Sidebar = ({ activeView, setActiveView, setAuth }) => {
  const menuItems = [
    { key: 'dashboard', label: '📊 Panel główny', icon: '📊' },
    { key: 'clients', label: '👥 Lista Klientów', icon: '👥' },
    { key: 'add-client', label: '➕ Dodaj Klienta', icon: '➕' },
    { key: 'reports', label: '📈 Raporty', icon: '📈' },
    { key: 'telegram', label: '🤖 Bot Telegram', icon: '🤖' },
    { key: 'backup', label: '💾 Kopie Zapasowe', icon: '💾' },
    { key: 'panels', label: '📺 Panele', icon: '📺' },
    { key: 'apps', label: '📱 Aplikacje', icon: '📱' },
    { key: 'contact-types', label: '📞 Typy Kontaktów', icon: '📞' },
    { key: 'settings', label: '⚙️ Ustawienia', icon: '⚙️' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('tv_panel_token');
    setAuth(false);
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>📺 TV Panel Pro</h2>
        <div className="version">v2.0 Advanced</div>
      </div>
      
      <nav className="sidebar-nav">
        {menuItems.map(item => (
          <button
            key={item.key}
            className={`nav-item ${activeView === item.key ? 'active' : ''}`}
            onClick={() => setActiveView(item.key)}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>
      
      <div className="sidebar-footer">
        <div className="user-info">
          <span>👤 Administrator</span>
        </div>
        <button onClick={handleLogout} className="btn-logout">
          🚪 Wyloguj
        </button>
      </div>
    </div>
  );
};

// Enhanced Dashboard Component
const Dashboard = () => {
  const [stats, setStats] = useState({});
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [charts, setCharts] = useState({});

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('tv_panel_token');
        const headers = { Authorization: `Bearer ${token}` };
        
        // Fetch basic stats and advanced analytics
        const [statsRes, analyticsRes] = await Promise.all([
          axios.get(`${API}/dashboard/stats`, { headers }),
          axios.get(`${API}/reports/dashboard`, { headers })
        ]);
        
        setStats(statsRes.data);
        setAnalytics(analyticsRes.data);
        
        // Fetch charts
        const chartTypes = ['revenue_trend', 'client_growth', 'panel_distribution'];
        const chartsData = {};
        
        for (const chartType of chartTypes) {
          try {
            const chartRes = await axios.get(`${API}/reports/chart/${chartType}`, { headers });
            chartsData[chartType] = chartRes.data.chart;
          } catch (e) {
            console.warn(`Could not load chart: ${chartType}`);
          }
        }
        
        setCharts(chartsData);
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
      setLoading(false);
    };

    fetchDashboardData();
  }, []);

  if (loading) return <div className="loading">Ładowanie panelu głównego...</div>;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>📊 Panel Główny</h1>
        <div className="dashboard-controls">
          <button className="btn-refresh" onClick={() => window.location.reload()}>
            🔄 Odśwież
          </button>
        </div>
      </div>
      
      {/* Basic Stats */}
      <div className="stats-grid">
        <div className="stat-card total">
          <div className="stat-number">{stats.total_clients || 0}</div>
          <div className="stat-label">Wszyscy klienci</div>
          <div className="stat-trend">📈</div>
        </div>
        
        <div className="stat-card active">
          <div className="stat-number">{stats.active_clients || 0}</div>
          <div className="stat-label">Aktywni klienci</div>
          <div className="stat-trend">✅</div>
        </div>
        
        <div className="stat-card warning">
          <div className="stat-number">{stats.expiring_soon || 0}</div>
          <div className="stat-label">Wygasający wkrótce</div>
          <div className="stat-trend">⚠️</div>
        </div>
        
        <div className="stat-card danger">
          <div className="stat-number">{stats.expired_clients || 0}</div>
          <div className="stat-label">Wygasłe licencje</div>
          <div className="stat-trend">❌</div>
        </div>
      </div>

      {/* Advanced Analytics */}
      {analytics && (
        <div className="analytics-section">
          <div className="analytics-grid">
            <div className="analytics-card">
              <h3>📊 Wskaźniki Biznesowe</h3>
              <div className="metrics">
                <div className="metric">
                  <span className="metric-label">Retencja:</span>
                  <span className="metric-value">{analytics.retention_rate}%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Churn:</span>
                  <span className="metric-value">{analytics.churn_rate}%</span>
                </div>
              </div>
            </div>
            
            <div className="analytics-card">
              <h3>💰 Przychody (szacowane)</h3>
              <div className="revenue-info">
                {analytics.revenue_trend?.slice(-1)[0] && (
                  <>
                    <div className="revenue-amount">
                      {analytics.revenue_trend.slice(-1)[0].revenue} PLN
                    </div>
                    <div className="revenue-period">Miesięczne</div>
                  </>
                )}
              </div>
            </div>
          </div>
          
          {/* Charts Section */}
          <div className="charts-section">
            {charts.revenue_trend && (
              <div className="chart-container">
                <h3>📈 Trend Przychodów</h3>
                <img src={charts.revenue_trend} alt="Revenue Trend" className="chart-image" />
              </div>
            )}
            
            {charts.client_growth && (
              <div className="chart-container">
                <h3>👥 Wzrost Klientów</h3>
                <img src={charts.client_growth} alt="Client Growth" className="chart-image" />
              </div>
            )}
            
            {charts.panel_distribution && (
              <div className="chart-container">
                <h3>📺 Rozkład Paneli</h3>
                <img src={charts.panel_distribution} alt="Panel Distribution" className="chart-image" />
              </div>
            )}
          </div>
        </div>
      )}
      
      <div className="quick-actions">
        <h2>🚀 Szybkie Akcje</h2>
        <div className="action-buttons">
          <button className="btn-action" onClick={() => window.open(`${API}/reports/export?format=csv`, '_blank')}>
            📊 Eksport CSV
          </button>
          <button className="btn-action" onClick={() => alert('Funkcja w przygotowaniu')}>
            📧 Wyślij przypomnienia
          </button>
          <button className="btn-action" onClick={() => alert('Funkcja w przygotowaniu')}>
            📥 Import klientów
          </button>
          <button className="btn-action">🔐 Generator haseł</button>
        </div>
      </div>
    </div>
  );
};

// Reports Component
const Reports = () => {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState('dashboard');

  const generateReport = async (reportType, format = 'json') => {
    setLoading(true);
    try {
      const token = localStorage.getItem('tv_panel_token');
      
      if (format === 'csv' || format === 'pdf') {
        // For file downloads
        const response = await fetch(`${API}/reports/export`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            report_type: reportType,
            format: format
          })
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `tv_panel_report.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        // For JSON data
        const response = await axios.get(`${API}/reports/${reportType}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setReportData(response.data);
      }
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Błąd podczas generowania raportu');
    }
    setLoading(false);
  };

  return (
    <div className="reports-section">
      <div className="reports-header">
        <h1>📈 Zaawansowane Raporty</h1>
        <div className="report-controls">
          <select 
            value={selectedReport}
            onChange={(e) => setSelectedReport(e.target.value)}
            className="report-select"
          >
            <option value="dashboard">Panel główny</option>
            <option value="monthly">Raport miesięczny</option>
            <option value="analytics/retention">Analiza retencji</option>
            <option value="analytics/revenue">Analiza przychodów</option>
          </select>
          
          <button 
            onClick={() => generateReport(selectedReport)} 
            disabled={loading}
            className="btn-generate"
          >
            {loading ? 'Generowanie...' : '📊 Generuj raport'}
          </button>
        </div>
      </div>

      <div className="export-buttons">
        <button 
          onClick={() => generateReport(selectedReport, 'csv')} 
          className="btn-export"
          disabled={loading}
        >
          📄 Eksport CSV
        </button>
        <button 
          onClick={() => generateReport(selectedReport, 'pdf')} 
          className="btn-export"
          disabled={loading}
        >
          📑 Eksport PDF
        </button>
      </div>

      {reportData && (
        <div className="report-content">
          <div className="report-summary">
            <h3>📋 Podsumowanie raportu</h3>
            <pre>{JSON.stringify(reportData, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

// Telegram Bot Component
const TelegramBot = () => {
  const [botStatus, setBotStatus] = useState('disconnected');
  const [botToken, setBotToken] = useState('');
  const [adminIds, setAdminIds] = useState('');

  return (
    <div className="telegram-bot">
      <div className="bot-header">
        <h1>🤖 Bot Telegram</h1>
        <div className={`status-indicator ${botStatus}`}>
          <span className="status-dot"></span>
          {botStatus === 'connected' ? 'Połączony' : 'Rozłączony'}
        </div>
      </div>

      <div className="bot-config">
        <h2>⚙️ Konfiguracja Bota</h2>
        
        <div className="form-group">
          <label>Token Bota:</label>
          <input
            type="password"
            value={botToken}
            onChange={(e) => setBotToken(e.target.value)}
            placeholder="123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
          />
          <small>Uzyskaj token od @BotFather na Telegramie</small>
        </div>

        <div className="form-group">
          <label>ID Administratorów (rozdzielone przecinkami):</label>
          <input
            type="text"
            value={adminIds}
            onChange={(e) => setAdminIds(e.target.value)}
            placeholder="12345678,87654321"
          />
          <small>ID użytkowników, którzy mogą używać bota</small>
        </div>

        <button className="btn-primary">💾 Zapisz konfigurację</button>
      </div>

      <div className="bot-features">
        <h2>🔧 Funkcje Bota</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>🔔 Powiadomienia</h3>
            <p>Automatyczne powiadomienia o wygasających licencjach</p>
            <label className="switch">
              <input type="checkbox" />
              <span className="slider"></span>
            </label>
          </div>
          
          <div className="feature-card">
            <h3>📊 Statystyki</h3>
            <p>Codzienne raporty o stanie systemu</p>
            <label className="switch">
              <input type="checkbox" />
              <span className="slider"></span>
            </label>
          </div>
          
          <div className="feature-card">
            <h3>📧 Przypomnienia</h3>
            <p>Wysyłanie przypomnień do klientów</p>
            <label className="switch">
              <input type="checkbox" />
              <span className="slider"></span>
            </label>
          </div>
        </div>
      </div>

      <div className="bot-logs">
        <h2>📝 Logi Bota</h2>
        <div className="log-container">
          <div className="log-entry">
            <span className="timestamp">2025-03-19 10:30:15</span>
            <span className="message">Bot uruchomiony pomyślnie</span>
          </div>
          <div className="log-entry">
            <span className="timestamp">2025-03-19 10:35:22</span>
            <span className="message">Wysłano 3 powiadomienia o wygasających licencjach</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Backup & Restore Component
const BackupRestore = () => {
  const [backups, setBackups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  const fetchBackups = async () => {
    setLoading(true);
    try {
      // This would call a backup list API
      // For now, simulate backup data
      const mockBackups = [
        {
          filename: 'tv_panel_backup_20250319_120000.zip',
          created_at: '2025-03-19T12:00:00Z',
          total_documents: 156,
          size_mb: 2.3
        },
        {
          filename: 'tv_panel_backup_20250318_020000.zip',
          created_at: '2025-03-18T02:00:00Z',
          total_documents: 148,
          size_mb: 2.1
        }
      ];
      setBackups(mockBackups);
    } catch (error) {
      console.error('Error fetching backups:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchBackups();
  }, []);

  const createBackup = async () => {
    setCreating(true);
    try {
      // This would call backup creation API
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate
      alert('✅ Kopia zapasowa utworzona pomyślnie!');
      fetchBackups();
    } catch (error) {
      console.error('Error creating backup:', error);
      alert('❌ Błąd podczas tworzenia kopii zapasowej');
    }
    setCreating(false);
  };

  return (
    <div className="backup-restore">
      <div className="backup-header">
        <h1>💾 Kopie Zapasowe</h1>
        <button 
          onClick={createBackup} 
          disabled={creating}
          className="btn-primary"
        >
          {creating ? '⏳ Tworzenie...' : '📦 Utwórz kopię'}
        </button>
      </div>

      <div className="backup-settings">
        <h2>⚙️ Ustawienia automatyczne</h2>
        <div className="settings-grid">
          <div className="setting-item">
            <label>
              <input type="checkbox" defaultChecked />
              Codzienne kopie zapasowe (02:00)
            </label>
          </div>
          <div className="setting-item">
            <label>
              <input type="checkbox" defaultChecked />
              Zachowuj kopie przez 30 dni
            </label>
          </div>
          <div className="setting-item">
            <label>
              <input type="checkbox" />
              Powiadomienia email o kopiach
            </label>
          </div>
        </div>
      </div>

      <div className="backups-list">
        <h2>📋 Lista kopii zapasowych</h2>
        
        {loading ? (
          <div className="loading">Ładowanie kopii zapasowych...</div>
        ) : (
          <div className="backup-table">
            {backups.map((backup, index) => (
              <div key={index} className="backup-row">
                <div className="backup-info">
                  <div className="backup-name">📁 {backup.filename}</div>
                  <div className="backup-meta">
                    📅 {new Date(backup.created_at).toLocaleString('pl-PL')} | 
                    📊 {backup.total_documents} dokumentów | 
                    💾 {backup.size_mb} MB
                  </div>
                </div>
                <div className="backup-actions">
                  <button className="btn-download">⬇️ Pobierz</button>
                  <button className="btn-restore">🔄 Przywróć</button>
                  <button className="btn-delete">🗑️ Usuń</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Enhanced Clients List Component (same as before but with additional features)
const ClientsList = () => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [expiryFilter, setExpiryFilter] = useState('');
  const [selectedClients, setSelectedClients] = useState([]);

  const fetchClients = async () => {
    try {
      const token = localStorage.getItem('tv_panel_token');
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (expiryFilter) params.append('expiry_filter', expiryFilter);
      
      const response = await axios.get(`${API}/clients?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setClients(response.data);
    } catch (error) {
      console.error('Error fetching clients:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchClients();
  }, [search, expiryFilter]);

  const deleteClient = async (clientId) => {
    if (!window.confirm('Czy na pewno chcesz usunąć tego klienta?')) return;
    
    try {
      const token = localStorage.getItem('tv_panel_token');
      await axios.delete(`${API}/clients/${clientId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchClients();
    } catch (error) {
      console.error('Error deleting client:', error);
    }
  };

  const getStatusClass = (client) => {
    if (client.days_left < 0) return 'status-expired';
    if (client.days_left <= 7) return 'status-warning';
    return 'status-active';
  };

  const getStatusLabel = (client) => {
    if (client.days_left < 0) return '❌ Wygasło';
    if (client.days_left <= 7) return '⚠️ Wygasa wkrótce';
    return '✅ Aktywny';
  };

  if (loading) return <div className="loading">Ładowanie klientów...</div>;

  return (
    <div className="clients-list">
      <div className="page-header">
        <h1>👥 Lista Klientów</h1>
        
        <div className="filters">
          <input
            type="text"
            placeholder="🔍 Szukaj po nazwie, loginie, MAC..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          
          <select
            value={expiryFilter}
            onChange={(e) => setExpiryFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Wszystkie</option>
            <option value="active">Aktywne</option>
            <option value="expiring_soon">Wygasające wkrótce</option>
            <option value="expired">Wygasłe</option>
          </select>
          
          <button className="btn-primary">📥 Import CSV</button>
          <button className="btn-secondary" onClick={() => window.open(`${API}/reports/export?format=csv`, '_blank')}>
            📤 Eksport CSV
          </button>
        </div>
      </div>

      <div className="table-container">
        <table className="clients-table">
          <thead>
            <tr>
              <th>
                <input 
                  type="checkbox"
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedClients(clients.map(c => c.id));
                    } else {
                      setSelectedClients([]);
                    }
                  }}
                />
              </th>
              <th>ID</th>
              <th>Nazwa</th>
              <th>Status</th>
              <th>Dni pozostałe</th>
              <th>Panel</th>
              <th>Login</th>
              <th>Hasło</th>
              <th>Aplikacja</th>
              <th>MAC</th>
              <th>Klucz</th>
              <th>Kontakt</th>
              <th>Akcje</th>
            </tr>
          </thead>
          <tbody>
            {clients.map(client => (
              <tr key={client.id} className={getStatusClass(client)}>
                <td>
                  <input 
                    type="checkbox"
                    checked={selectedClients.includes(client.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedClients([...selectedClients, client.id]);
                      } else {
                        setSelectedClients(selectedClients.filter(id => id !== client.id));
                      }
                    }}
                  />
                </td>
                <td>{client.id.slice(-6)}</td>
                <td className="client-name">{client.name}</td>
                <td>
                  <span className={`status ${getStatusClass(client)}`}>
                    {getStatusLabel(client)}
                  </span>
                </td>
                <td>
                  <span className={client.days_left <= 7 ? 'days-warning' : ''}>
                    {client.days_left < 0 ? 'Wygasło' : `${client.days_left} dni`}
                  </span>
                </td>
                <td>{client.panel_name || '-'}</td>
                <td>{client.login || '-'}</td>
                <td className="password-field">{client.password || '-'}</td>
                <td>{client.app_name || '-'}</td>
                <td className="mac-field">{client.mac || '-'}</td>
                <td className="key-field">{client.key_value || '-'}</td>
                <td>{client.contact_value || '-'}</td>
                <td>
                  <div className="action-buttons">
                    <button className="btn-edit" title="Edytuj">✏️</button>
                    <button className="btn-message" title="Wyślij wiadomość">💬</button>
                    <button className="btn-extend" title="Przedłuż licencję">⏱️</button>
                    <button 
                      className="btn-delete" 
                      title="Usuń"
                      onClick={() => deleteClient(client.id)}
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedClients.length > 0 && (
        <div className="bulk-actions">
          <button className="btn-bulk-extend">
            ⏱️ Przedłuż licencje ({selectedClients.length})
          </button>
          <button className="btn-bulk-message">
            💬 Wyślij wiadomości ({selectedClients.length})
          </button>
          <button className="btn-bulk-delete">
            🗑️ Usuń zaznaczone ({selectedClients.length})
          </button>
        </div>
      )}
    </div>
  );
};

// Add Client Component (same as before)
const AddClient = () => {
  const [formData, setFormData] = useState({
    name: '',
    subscription_period: 30,
    panel_id: '',
    login: '',
    password: '',
    app_id: '',
    mac: '',
    key_value: '',
    contact_type_id: '',
    contact_value: '',
    telegram_id: '',
    notes: '',
    line_id: ''
  });
  
  const [panels, setPanels] = useState([]);
  const [apps, setApps] = useState([]);
  const [contactTypes, setContactTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('tv_panel_token');
        const headers = { Authorization: `Bearer ${token}` };
        
        const [panelsRes, appsRes, contactTypesRes] = await Promise.all([
          axios.get(`${API}/panels`, { headers }),
          axios.get(`${API}/apps`, { headers }),
          axios.get(`${API}/contact-types`, { headers })
        ]);
        
        setPanels(panelsRes.data);
        setApps(appsRes.data);
        setContactTypes(contactTypesRes.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  const generatePassword = async () => {
    try {
      const response = await axios.get(`${API}/generate-password?length=8`);
      setFormData({...formData, password: response.data.password});
    } catch (error) {
      console.error('Error generating password:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const token = localStorage.getItem('tv_panel_token');
      await axios.post(`${API}/clients`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setMessage('✅ Klient został dodany pomyślnie!');
      setFormData({
        name: '',
        subscription_period: 30,
        panel_id: '',
        login: '',
        password: '',
        app_id: '',
        mac: '',
        key_value: '',
        contact_type_id: '',
        contact_value: '',
        telegram_id: '',
        notes: '',
        line_id: ''
      });
    } catch (error) {
      setMessage('❌ Błąd podczas dodawania klienta: ' + (error.response?.data?.detail || 'Nieznany błąd'));
    }
    
    setLoading(false);
  };

  const handleInputChange = (field, value) => {
    setFormData({...formData, [field]: value});
  };

  return (
    <div className="add-client">
      <h1>➕ Dodaj Nowego Klienta</h1>
      
      {message && (
        <div className={`alert ${message.includes('✅') ? 'alert-success' : 'alert-error'}`}>
          {message}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="client-form">
        <div className="form-grid">
          {/* Basic Information */}
          <div className="form-section">
            <h3>📋 Podstawowe informacje</h3>
            
            <div className="form-group">
              <label>Nazwa klienta *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                required
              />
            </div>
            
            <div className="form-group">
              <label>ID linii</label>
              <input
                type="text"
                value={formData.line_id}
                onChange={(e) => handleInputChange('line_id', e.target.value)}
              />
            </div>
            
            <div className="form-group">
              <label>Okres ważności *</label>
              <select
                value={formData.subscription_period}
                onChange={(e) => handleInputChange('subscription_period', parseInt(e.target.value))}
                required
              >
                <option value={30}>1 miesiąc</option>
                <option value={90}>3 miesiące</option>
                <option value={180}>6 miesięcy</option>
                <option value={365}>12 miesięcy</option>
              </select>
            </div>
          </div>

          {/* Access Data */}
          <div className="form-section">
            <h3>🔐 Dane dostępowe</h3>
            
            <div className="form-group">
              <label>Panel</label>
              <select
                value={formData.panel_id}
                onChange={(e) => handleInputChange('panel_id', e.target.value)}
              >
                <option value="">Wybierz panel</option>
                {panels.map(panel => (
                  <option key={panel.id} value={panel.id}>
                    {panel.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label>Login</label>
              <input
                type="text"
                value={formData.login}
                onChange={(e) => handleInputChange('login', e.target.value)}
              />
            </div>
            
            <div className="form-group">
              <label>Hasło</label>
              <div className="password-input">
                <input
                  type="text"
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                />
                <button type="button" onClick={generatePassword} className="btn-generate">
                  🎲 Generuj
                </button>
              </div>
            </div>
          </div>

          {/* Technical Data */}
          <div className="form-section">
            <h3>📱 Dane techniczne</h3>
            
            <div className="form-group">
              <label>Aplikacja</label>
              <select
                value={formData.app_id}
                onChange={(e) => handleInputChange('app_id', e.target.value)}
              >
                <option value="">Wybierz aplikację</option>
                {apps.map(app => (
                  <option key={app.id} value={app.id}>
                    {app.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label>MAC</label>
              <input
                type="text"
                value={formData.mac}
                onChange={(e) => handleInputChange('mac', e.target.value)}
                placeholder="12:34:56:78:90:AB"
              />
            </div>
            
            <div className="form-group">
              <label>Klucz</label>
              <input
                type="text"
                value={formData.key_value}
                onChange={(e) => handleInputChange('key_value', e.target.value)}
              />
            </div>
          </div>

          {/* Contact Info */}
          <div className="form-section">
            <h3>📞 Kontakt i notatki</h3>
            
            <div className="form-group">
              <label>Typ kontaktu</label>
              <select
                value={formData.contact_type_id}
                onChange={(e) => handleInputChange('contact_type_id', e.target.value)}
              >
                <option value="">Wybierz typ kontaktu</option>
                {contactTypes.map(type => (
                  <option key={type.id} value={type.id}>
                    {type.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label>Kontakt</label>
              <input
                type="text"
                value={formData.contact_value}
                onChange={(e) => handleInputChange('contact_value', e.target.value)}
              />
            </div>
            
            <div className="form-group">
              <label>ID Telegrama</label>
              <input
                type="text"
                value={formData.telegram_id}
                onChange={(e) => handleInputChange('telegram_id', e.target.value)}
                placeholder="Numeryczne ID użytkownika"
              />
            </div>
            
            <div className="form-group">
              <label>Notatki</label>
              <textarea
                value={formData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                rows="3"
              />
            </div>
          </div>
        </div>
        
        <div className="form-actions">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Dodawanie...' : '➕ Dodaj klienta'}
          </button>
        </div>
      </form>
    </div>
  );
};

// Simple management components (same as before)
const SimpleManager = ({ title, endpoint, createEndpoint, fields, icon }) => {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState({});
  const [loading, setLoading] = useState(true);

  const fetchItems = async () => {
    try {
      const token = localStorage.getItem('tv_panel_token');
      const response = await axios.get(`${API}${endpoint}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setItems(response.data);
    } catch (error) {
      console.error(`Error fetching ${endpoint}:`, error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchItems();
  }, [endpoint]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('tv_panel_token');
      await axios.post(`${API}${createEndpoint || endpoint}`, newItem, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNewItem({});
      fetchItems();
    } catch (error) {
      console.error(`Error creating item:`, error);
    }
  };

  if (loading) return <div className="loading">Ładowanie...</div>;

  return (
    <div className="simple-manager">
      <h1>{icon} {title}</h1>
      
      <form onSubmit={handleCreate} className="add-form">
        <div className="form-row">
          {fields.map(field => (
            <input
              key={field.key}
              type={field.type || 'text'}
              placeholder={field.label}
              value={newItem[field.key] || ''}
              onChange={(e) => setNewItem({...newItem, [field.key]: e.target.value})}
              required={field.required}
            />
          ))}
          <button type="submit" className="btn-primary">Dodaj</button>
        </div>
      </form>
      
      <div className="items-list">
        {items.map(item => (
          <div key={item.id} className="item-card">
            <h3>{item.name}</h3>
            {item.description && <p>{item.description}</p>}
            {item.url && <p><strong>URL:</strong> {item.url}</p>}
            {item.url_pattern && <p><strong>Wzorzec:</strong> {item.url_pattern}</p>}
          </div>
        ))}
      </div>
    </div>
  );
};

// Main App Component
const MainApp = () => {
  const [activeView, setActiveView] = useState('dashboard');
  const [auth, setAuth] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('tv_panel_token');
    if (token) {
      setAuth(true);
    }
  }, []);

  if (!auth) {
    return <Login setAuth={setAuth} />;
  }

  const renderContent = () => {
    switch(activeView) {
      case 'dashboard':
        return <Dashboard />;
      case 'clients':
        return <ClientsList />;
      case 'add-client':
        return <AddClient />;
      case 'reports':
        return <Reports />;
      case 'telegram':
        return <TelegramBot />;
      case 'backup':
        return <BackupRestore />;
      case 'panels':
        return <SimpleManager 
          title="Panele IPTV" 
          endpoint="/panels" 
          icon="📺"
          fields={[
            {key: 'name', label: 'Nazwa panelu', required: true},
            {key: 'url', label: 'URL panelu'},
            {key: 'description', label: 'Opis'}
          ]}
        />;
      case 'apps':
        return <SimpleManager 
          title="Aplikacje IPTV" 
          endpoint="/apps" 
          icon="📱"
          fields={[
            {key: 'name', label: 'Nazwa aplikacji', required: true},
            {key: 'description', label: 'Opis'}
          ]}
        />;
      case 'contact-types':
        return <SimpleManager 
          title="Typy Kontaktów" 
          endpoint="/contact-types" 
          icon="📞"
          fields={[
            {key: 'name', label: 'Nazwa typu kontaktu', required: true},
            {key: 'url_pattern', label: 'Wzorzec URL (z {contact})', required: true},
            {key: 'icon', label: 'Ikona'}
          ]}
        />;
      case 'settings':
        return <div className="settings">
          <h1>⚙️ Ustawienia</h1>
          <div className="settings-grid">
            <div className="setting-section">
              <h3>🔧 Ustawienia systemowe</h3>
              <p>Konfiguracja podstawowych parametrów systemu</p>
            </div>
            <div className="setting-section">
              <h3>👤 Zarządzanie użytkownikami</h3>
              <p>Dodawanie i edycja administratorów</p>
            </div>
            <div className="setting-section">
              <h3>📧 Powiadomienia</h3>
              <p>Konfiguracja emaili i SMS</p>
            </div>
          </div>
        </div>;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Sidebar activeView={activeView} setActiveView={setActiveView} setAuth={setAuth} />
      <div className="main-content">
        {renderContent()}
      </div>
    </div>
  );
};

// Root App Component
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/*" element={<MainApp />} />
      </Routes>
    </Router>
  );
}

export default App;