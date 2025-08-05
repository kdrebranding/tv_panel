import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
          <h1>🛢️ TV Panel SQL</h1>
          <p>System zarządzania klientami IPTV z SQL</p>
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
    { key: 'clients', label: '👥 Klienci', icon: '👥' },
    { key: 'add-client', label: '➕ Dodaj Klienta', icon: '➕' },
    { key: 'panels', label: '📺 Panele', icon: '📺' },
    { key: 'apps', label: '📱 Aplikacje', icon: '📱' },
    { key: 'smart-tv-activations', label: '📺 Aktywacja Smart TV', icon: '📺' },
    { key: 'contact-types', label: '📞 Kontakty', icon: '📞' },
    { key: 'payment-methods', label: '💳 Płatności', icon: '💳' },
    { key: 'pricing-config', label: '💰 Cennik', icon: '💰' },
    { key: 'questions', label: '❓ FAQ', icon: '❓' },
    { key: 'smart-tv-apps', label: '📺 Smart TV Apps', icon: '📺' },
    { key: 'android-apps', label: '🤖 Android Apps', icon: '🤖' },
    { key: 'telegram-bot', label: '🤖 Bot Telegram', icon: '🤖' },
    { key: 'settings', label: '⚙️ Ustawienia', icon: '⚙️' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('tv_panel_token');
    setAuth(false);
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>📊 TV Panel SQL</h2>
        <span className="version">v3.0 SQL Edition</span>
      </div>
      
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.key}
            onClick={() => setActiveView(item.key)}
            className={`nav-item ${activeView === item.key ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>
      
      <div className="sidebar-footer">
        <button onClick={handleLogout} className="logout-btn">
          🚪 Odloguj
        </button>
      </div>
    </div>
  );
};

// Dashboard Component with real data
const Dashboard = ({ setActiveView }) => {
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  const generatePassword = async () => {
    try {
      const token = localStorage.getItem('tv_panel_token');
      const response = await axios.post(`${API}/generate-password`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const password = response.data.password;
      navigator.clipboard.writeText(password);
      alert(`🔐 Wygenerowane hasło: ${password}\n\n✅ Hasło zostało skopiowane do schowka!`);
    } catch (error) {
      console.error('Error generating password:', error);
      alert('❌ Błąd podczas generowania hasła');
    }
  };

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('tv_panel_token');
        const response = await axios.get(`${API}/dashboard/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
      setLoading(false);
    };

    fetchStats();
  }, []);

  if (loading) return <div className="loading">Ładowanie panelu głównego...</div>;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>📊 Panel Główny SQL</h1>
        <div className="dashboard-controls">
          <button className="btn-refresh" onClick={() => window.location.reload()}>
            🔄 Odśwież
          </button>
        </div>
      </div>
      
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

      <div className="quick-actions">
        <h2>🚀 Zarządzanie danymi SQL</h2>
        <div className="action-buttons">
          <button className="btn-action" onClick={() => window.open(`${API}/export-csv/clients`, '_blank')}>
            📊 Eksport CSV Klientów
          </button>
          <button className="btn-action" onClick={() => window.open(`${API}/export-csv/panels`, '_blank')}>
            📺 Eksport Paneli
          </button>
          <button className="btn-action" onClick={() => setActiveView('settings')}>
            ⚙️ Ustawienia systemu
          </button>
          <button className="btn-action" onClick={generatePassword}>🔐 Generator haseł</button>
        </div>
      </div>

      <div className="json-data-overview">
        <h2>📋 Zarządzanie sekcjami</h2>
        <div className="data-grid">
          <div className="data-card clickable" onClick={() => setActiveView('payment-methods')}>
            <h3>💳 Metody płatności</h3>
            <p>Zarządzaj dostępnymi opcjami płatności</p>
          </div>
          <div className="data-card clickable" onClick={() => setActiveView('pricing-config')}>
            <h3>💰 Konfiguracja cennika</h3>
            <p>Ustawiaj ceny i pakiety subskrypcji</p>
          </div>
          <div className="data-card clickable" onClick={() => setActiveView('questions')}>
            <h3>❓ Pytania FAQ</h3>
            <p>Zarządzaj często zadawanymi pytaniami</p>
          </div>
          <div className="data-card clickable" onClick={() => setActiveView('smart-tv-apps')}>
            <h3>📺 Aplikacje Smart TV</h3>
            <p>Konfiguruj aplikacje dla Smart TV</p>
          </div>
          <div className="data-card clickable" onClick={() => setActiveView('telegram-bot')}>
            <h3>🤖 Bot Telegram</h3>
            <p>Zarządzaj botem i powiadomieniami</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Telegram Bot Component with real data
const TelegramBot = () => {
  const [botStats, setBotStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchBotStats = async () => {
      try {
        const token = localStorage.getItem('tv_panel_token');
        const response = await axios.get(`${API}/bot/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setBotStats(response.data);
      } catch (error) {
        console.error('Error fetching bot stats:', error);
        setError('Błąd pobierania danych bota');
      }
      setLoading(false);
    };

    fetchBotStats();
  }, []);

  if (loading) return <div className="loading">Ładowanie danych bota...</div>;
  if (error) return <div className="error">❌ {error}</div>;

  const botStatus = botStats.bot_configured && botStats.bot_active;
  const maskedToken = botStats.telegram_token_present ? 
    '7749306488:AAGYYY••••••••••••••••••••••••••••' : 'Nie skonfigurowany';

  return (
    <div className="telegram-bot">
      <div className="bot-header">
        <h1>🤖 Bot Telegram</h1>
        <div className={`status-indicator ${botStatus ? 'connected' : 'disconnected'}`}>
          <span>{botStatus ? '🟢' : '🔴'}</span>
          <span>{botStatus ? 'Aktywny' : 'Nieaktywny'}</span>
        </div>
      </div>
      
      <div className="bot-config">
        <div className="config-section">
          <h3>📋 Konfiguracja</h3>
          <div className="config-grid">
            <div className="config-item">
              <label>🔑 Token bota:</label>
              <input type="text" value={maskedToken} disabled className="bot-token" />
            </div>
            <div className="config-item">
              <label>👤 Admin ID:</label>
              <input type="text" value={botStats.admin_id || 'Nie skonfigurowany'} disabled />
            </div>
            <div className="config-item">
              <label>📱 WhatsApp Admin:</label>
              <input type="text" value={botStats.whatsapp_admin || 'Nie skonfigurowany'} disabled />
            </div>
            <div className="config-item">
              <label>⏰ Godzina przypomnień:</label>
              <input type="text" value="20:00" disabled />
            </div>
          </div>
        </div>
        
        <div className="config-section">
          <h3>🎯 Funkcje bota</h3>
          <div className="bot-features">
            <div className="feature-item">
              <span className="feature-icon">📤</span>
              <div className="feature-content">
                <h4>Powiadomienia o licencjach</h4>
                <p>Powiadomienia dla {botStats.expiring_clients || 0} wygasających licencji</p>
              </div>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🔐</span>
              <div className="feature-content">
                <h4>Autoryzacja klientów</h4>
                <p>{botStats.clients_with_telegram || 0} klientów z Telegram ID</p>
              </div>
            </div>
            <div className="feature-item">
              <span className="feature-icon">💰</span>
              <div className="feature-content">
                <h4>Zarządzanie płatnościami</h4>
                <p>Integracja z systemem płatności</p>
              </div>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📱</span>
              <div className="feature-content">
                <h4>Aplikacje i aktywacja</h4>
                <p>Zarządzanie aplikacjami Android i Smart TV</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="config-section">
          <h3>📊 Status systemu</h3>
          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">Status bota:</span>
              <span className={`status-value ${botStatus ? 'connected' : ''}`}>
                {botStatus ? '🟢 Aktywny' : '🔴 Nieaktywny'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Ostatnia aktywność:</span>
              <span className="status-value">Dziś o {botStats.last_activity || '--:--'}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Klienci w bazie:</span>
              <span className="status-value">{botStats.total_clients || 0}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Powiadomienia dzisiaj:</span>
              <span className="status-value">{botStats.notifications_today || 0}</span>
            </div>
          </div>
        </div>
        
        <div className="bot-actions">
          <button className="btn-primary" onClick={() => {
            const status = botStatus ? 'Aktywny' : 'Nieaktywny';
            const token = botStats.telegram_token_present ? 'Skonfigurowany' : 'Brak';
            const clients = botStats.total_clients || 0;
            alert(`🤖 Status bota: ${status}\n\nToken: ${token}\nAdmin ID: ${botStats.admin_id || 'Brak'}\nKlienci w bazie: ${clients}\nKlienci z Telegram: ${botStats.clients_with_telegram || 0}`);
          }}>
            📊 Sprawdź status
          </button>
          <button className="btn-secondary" onClick={() => {
            const logs = `📝 Rzeczywiste dane z bazy SQL:\n\n• Klienci ogółem: ${botStats.total_clients || 0}\n• Klienci z Telegram ID: ${botStats.clients_with_telegram || 0}\n• Dodano dzisiaj: ${botStats.clients_added_today || 0}\n• Wygasają wkrótce: ${botStats.expiring_clients || 0}\n• Token bota: ${botStats.telegram_token_present ? 'Skonfigurowany' : 'Brak'}\n• Admin ID: ${botStats.admin_id || 'Brak'}`;
            alert(logs);
          }}>
            📋 Zobacz dane
          </button>
          <button className="btn-secondary" onClick={() => alert('🔄 Funkcja restartu będzie dostępna w przyszłej wersji.')}>
            🔄 Restart bota
          </button>
        </div>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/*" element={<MainApp />} />
      </Routes>
    </Router>
  );
}

// Main App Component (temporary simplified version for testing)
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
        return <Dashboard setActiveView={setActiveView} />;
      
      case 'telegram-bot':
        return <TelegramBot />;
      
      default:
        return <div className="loading">Sekcja w budowie...</div>;
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