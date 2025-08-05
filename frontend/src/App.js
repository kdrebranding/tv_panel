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

// Enhanced Editable Table Component
const EditableTable = ({ title, endpoint, fields, icon, canAdd = true, canDelete = true }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingItem, setEditingItem] = useState(null);
  const [newItem, setNewItem] = useState({});
  const [showAddForm, setShowAddForm] = useState(false);
  const [message, setMessage] = useState('');

  const fetchItems = async () => {
    try {
      const token = localStorage.getItem('tv_panel_token');
      const response = await axios.get(`${API}${endpoint}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setItems(response.data);
    } catch (error) {
      console.error(`Error fetching ${endpoint}:`, error);
      setMessage(`❌ Błąd ładowania danych: ${error.message}`);
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
      await axios.post(`${API}${endpoint}`, newItem, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNewItem({});
      setShowAddForm(false);
      setMessage('✅ Dodano pomyślnie!');
      fetchItems();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage(`❌ Błąd dodawania: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleUpdate = async (id, updatedData) => {
    try {
      const token = localStorage.getItem('tv_panel_token');
      await axios.put(`${API}${endpoint}/${id}`, updatedData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEditingItem(null);
      setMessage('✅ Zaktualizowano pomyślnie!');
      fetchItems();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage(`❌ Błąd aktualizacji: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Czy na pewno chcesz usunąć ten element?')) return;
    
    try {
      const token = localStorage.getItem('tv_panel_token');
      await axios.delete(`${API}${endpoint}/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage('✅ Usunięto pomyślnie!');
      fetchItems();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage(`❌ Błąd usuwania: ${error.response?.data?.detail || error.message}`);
    }
  };

  const renderField = (field, value, onChange, isEditing = false) => {
    if (field.type === 'select') {
      return (
        <select value={value || ''} onChange={(e) => onChange(e.target.value)} disabled={!isEditing}>
          <option value="">Wybierz...</option>
          {field.options?.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      );
    }
    
    if (field.type === 'textarea') {
      return (
        <textarea 
          value={value || ''} 
          onChange={(e) => onChange(e.target.value)}
          disabled={!isEditing}
          rows="2"
        />
      );
    }
    
    if (field.type === 'checkbox') {
      return (
        <input 
          type="checkbox" 
          checked={value || false} 
          onChange={(e) => onChange(e.target.checked)}
          disabled={!isEditing}
        />
      );
    }
    
    return (
      <input 
        type={field.type || 'text'} 
        value={value || ''} 
        onChange={(e) => onChange(e.target.value)}
        disabled={!isEditing}
      />
    );
  };

  if (loading) return <div className="loading">Ładowanie {title.toLowerCase()}...</div>;

  return (
    <div className="editable-table">
      <div className="table-header">
        <h1>{icon} {title}</h1>
        {canAdd && (
          <button 
            className="btn-primary" 
            onClick={() => setShowAddForm(!showAddForm)}
          >
            ➕ Dodaj nowy
          </button>
        )}
      </div>

      {message && (
        <div className={`alert ${message.includes('✅') ? 'alert-success' : 'alert-error'}`}>
          {message}
        </div>
      )}

      {showAddForm && (
        <div className="add-form">
          <h3>Dodaj nowy element</h3>
          <form onSubmit={handleCreate}>
            <div className="form-grid">
              {fields.map(field => (
                <div key={field.key} className="form-group">
                  <label>{field.label} {field.required && '*'}</label>
                  {renderField(field, newItem[field.key], (value) => 
                    setNewItem({...newItem, [field.key]: value}), true
                  )}
                </div>
              ))}
            </div>
            <div className="form-actions">
              <button type="submit" className="btn-primary">Dodaj</button>
              <button type="button" className="btn-secondary" onClick={() => setShowAddForm(false)}>
                Anuluj
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              {fields.map(field => (
                <th key={field.key}>{field.label}</th>
              ))}
              <th>Akcje</th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr key={item.id}>
                {fields.map(field => (
                  <td key={field.key}>
                    {editingItem === item.id ? 
                      renderField(field, item[field.key], (value) => {
                        const updatedItem = {...item, [field.key]: value};
                        setItems(items.map(i => i.id === item.id ? updatedItem : i));
                      }, true) :
                      (field.type === 'checkbox' ? (item[field.key] ? '✅' : '❌') : (item[field.key] || '-'))
                    }
                  </td>
                ))}
                <td className="actions">
                  {editingItem === item.id ? (
                    <>
                      <button 
                        className="btn-save" 
                        onClick={() => handleUpdate(item.id, item)}
                      >
                        💾
                      </button>
                      <button 
                        className="btn-cancel" 
                        onClick={() => setEditingItem(null)}
                      >
                        ❌
                      </button>
                    </>
                  ) : (
                    <>
                      <button 
                        className="btn-edit" 
                        onClick={() => setEditingItem(item.id)}
                      >
                        ✏️
                      </button>
                      {canDelete && (
                        <button 
                          className="btn-delete" 
                          onClick={() => handleDelete(item.id)}
                        >
                          🗑️
                        </button>
                      )}
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {items.length === 0 && (
          <div className="no-data">
            <p>Brak danych do wyświetlenia</p>
            {canAdd && (
              <button className="btn-primary" onClick={() => setShowAddForm(true)}>
                ➕ Dodaj pierwszy element
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Clients List Component
const ClientsList = () => {
  return (
    <EditableTable
      title="Lista Klientów IPTV"
      endpoint="/clients"
      icon="👥"
      fields={[
        { key: 'name', label: 'Nazwa', type: 'text', required: true },
        { key: 'login', label: 'Login', type: 'text' },
        { key: 'expires_date', label: 'Data wygaśnięcia', type: 'date' },
        { key: 'telegram_id', label: 'Telegram ID', type: 'number' },
        { key: 'contact_value', label: 'Kontakt', type: 'text' },
        { key: 'status', label: 'Status', type: 'select', options: [
          { value: 'active', label: 'Aktywny' },
          { value: 'inactive', label: 'Nieaktywny' },
          { value: 'suspended', label: 'Zawieszony' }
        ]}
      ]}
    />
  );
};

// Add Client Component
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

  return (
    <div className="add-client">
      <h1>➕ Dodaj Nowego Klienta</h1>
      
      {message && (
        <div className={`alert ${message.includes('✅') ? 'alert-success' : 'alert-error'}`}>
          {message}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="client-form">
        <div className="form-section">
          <h3>📋 Podstawowe informacje</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Nazwa klienta *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
                placeholder="Jan Kowalski"
              />
            </div>
            
            <div className="form-group">
              <label>Okres subskrypcji (dni)</label>
              <input
                type="number"
                value={formData.subscription_period}
                onChange={(e) => setFormData({...formData, subscription_period: parseInt(e.target.value)})}
                min="1"
              />
            </div>
            
            <div className="form-group">
              <label>Telegram ID</label>
              <input
                type="number"
                value={formData.telegram_id}
                onChange={(e) => setFormData({...formData, telegram_id: e.target.value})}
                placeholder="123456789"
              />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>🔐 Dane dostępowe</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Login</label>
              <input
                type="text"
                value={formData.login}
                onChange={(e) => setFormData({...formData, login: e.target.value})}
                placeholder="client_login"
              />
            </div>
            
            <div className="form-group">
              <label>Hasło</label>
              <div className="password-input">
                <input
                  type="text"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  placeholder="Wprowadź hasło lub wygeneruj"
                />
                <button type="button" onClick={generatePassword} className="btn-generate">
                  🎲 Generuj
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>📞 Kontakt</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Typ kontaktu</label>
              <select
                value={formData.contact_type_id}
                onChange={(e) => setFormData({...formData, contact_type_id: e.target.value})}
              >
                <option value="">Wybierz typ kontaktu</option>
                {contactTypes.map(type => (
                  <option key={type.id} value={type.id}>{type.name}</option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label>Dane kontaktowe</label>
              <input
                type="text"
                value={formData.contact_value}
                onChange={(e) => setFormData({...formData, contact_value: e.target.value})}
                placeholder="email@example.com lub +48123456789"
              />
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Dodawanie...' : '✅ Dodaj klienta'}
          </button>
        </div>
      </form>
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
      
      case 'clients':
        return <ClientsList />;
      
      case 'add-client':
        return <AddClient />;
      
      case 'panels':
        return (
          <EditableTable
            title="Panele IPTV"
            endpoint="/panels"
            icon="📺"
            fields={[
              { key: 'name', label: 'Nazwa', type: 'text', required: true },
              { key: 'url', label: 'URL', type: 'text' },
              { key: 'description', label: 'Opis', type: 'textarea' }
            ]}
          />
        );
      
      case 'apps':
        return (
          <EditableTable
            title="Android Applications"
            endpoint="/apps"
            icon="📱"
            fields={[
              { key: 'name', label: 'Nazwa', type: 'text', required: true },
              { key: 'url', label: 'URL', type: 'text' },
              { key: 'package_name', label: 'Nazwa pakietu', type: 'text' },
              { key: 'app_code', label: 'Kod aplikacji', type: 'textarea' },
              { key: 'description', label: 'Opis', type: 'textarea' }
            ]}
            canAdd={true}
          />
        );
      
      case 'smart-tv-activations':
        return (
          <EditableTable
            title="Aktywacja Smart TV"
            endpoint="/smart-tv-activations"
            icon="📺"
            fields={[
              { key: 'app_name', label: 'Nazwa aplikacji', type: 'text', required: true },
              { key: 'activation_price', label: 'Cena za aktywację', type: 'number', required: true },
              { key: 'currency', label: 'Waluta', type: 'select', required: true, options: [
                { value: 'PLN', label: 'PLN - Polski Złoty' },
                { value: 'EUR', label: 'EUR - Euro' },
                { value: 'USD', label: 'USD - Dolar amerykański' },
                { value: 'GBP', label: 'GBP - Funt brytyjski' },
                { value: 'CZK', label: 'CZK - Korona czeska' }
              ]},
              { key: 'description', label: 'Opis aktywacji', type: 'textarea' },
              { key: 'is_active', label: 'Aktywna', type: 'checkbox' }
            ]}
          />
        );
      
      case 'contact-types':
        return (
          <EditableTable
            title="Typy Kontaktów"
            endpoint="/contact-types"
            icon="📞"
            fields={[
              { key: 'name', label: 'Nazwa', type: 'text', required: true },
              { key: 'url_pattern', label: 'Wzorzec URL', type: 'text' },
              { key: 'description', label: 'Opis', type: 'textarea' }
            ]}
          />
        );
      
      case 'payment-methods':
        return (
          <EditableTable
            title="Metody Płatności"
            endpoint="/payment-methods"
            icon="💳"
            fields={[
              { key: 'method_id', label: 'ID Metody', type: 'text', required: true },
              { key: 'name', label: 'Nazwa', type: 'text', required: true },
              { key: 'description', label: 'Opis', type: 'textarea' },
              { key: 'is_active', label: 'Aktywna', type: 'checkbox' },
              { key: 'fee_percentage', label: 'Opłata (%)', type: 'number' },
              { key: 'min_amount', label: 'Min. kwota', type: 'number' },
              { key: 'max_amount', label: 'Max. kwota', type: 'number' },
              { key: 'instructions', label: 'Instrukcje', type: 'textarea' }
            ]}
          />
        );
      
      case 'pricing-config':
        return (
          <EditableTable
            title="Konfiguracja Cennika"
            endpoint="/pricing-config"
            icon="💰"
            fields={[
              { key: 'service_type', label: 'Typ usługi', type: 'text', required: true },
              { key: 'price', label: 'Cena', type: 'number', required: true },
              { key: 'currency', label: 'Waluta', type: 'text' },
              { key: 'duration_days', label: 'Czas trwania (dni)', type: 'number', required: true },
              { key: 'is_active', label: 'Aktywna', type: 'checkbox' },
              { key: 'discount_percentage', label: 'Rabat (%)', type: 'number' },
              { key: 'description', label: 'Opis', type: 'textarea' }
            ]}
          />
        );
      
      case 'questions':
        return (
          <EditableTable
            title="Pytania FAQ"
            endpoint="/questions"
            icon="❓"
            fields={[
              { key: 'question', label: 'Pytanie', type: 'textarea', required: true },
              { key: 'answer', label: 'Odpowiedź', type: 'textarea', required: true },
              { key: 'category', label: 'Kategoria', type: 'text' },
              { key: 'is_active', label: 'Aktywne', type: 'checkbox' },
              { key: 'display_order', label: 'Kolejność', type: 'number' }
            ]}
          />
        );
      
      case 'smart-tv-apps':
        return (
          <EditableTable
            title="Smart TV Apps"
            endpoint="/smart-tv-apps"
            icon="📺"
            fields={[
              { key: 'name', label: 'Nazwa', type: 'text', required: true },
              { key: 'platform', label: 'Platforma', type: 'text' },
              { key: 'download_url', label: 'URL pobierania', type: 'text' },
              { key: 'instructions', label: 'Instrukcje', type: 'textarea' },
              { key: 'version', label: 'Wersja', type: 'text' },
              { key: 'is_active', label: 'Aktywna', type: 'checkbox' }
            ]}
            canAdd={true}
          />
        );
      
      case 'android-apps':
        return (
          <EditableTable
            title="Android Apps"
            endpoint="/android-apps"
            icon="🤖"
            fields={[
              { key: 'name', label: 'Nazwa', type: 'text', required: true },
              { key: 'package_name', label: 'Nazwa pakietu', type: 'text' },
              { key: 'download_url', label: 'URL pobierania', type: 'text' },
              { key: 'play_store_url', label: 'URL Play Store', type: 'text' },
              { key: 'instructions', label: 'Instrukcje', type: 'textarea' },
              { key: 'version', label: 'Wersja', type: 'text' },
              { key: 'is_active', label: 'Aktywna', type: 'checkbox' },
              { key: 'minimum_android_version', label: 'Min. Android', type: 'text' },
              { key: 'file_size', label: 'Rozmiar pliku', type: 'text' }
            ]}
            canAdd={true}
          />
        );

      case 'telegram-bot':
        return <TelegramBot />;
      
      case 'settings':
        return (
          <div className="settings">
            <h1>⚙️ Ustawienia systemu</h1>
            <div className="settings-grid">
              <div className="setting-section interactive" onClick={() => alert('🛢️ Baza danych: SQLite z pełnym wsparciem relacji SQL. Można migrować do MySQL/PostgreSQL.')}>
                <h3>🛢️ Baza danych SQL</h3>
                <p>System działa na SQLite z pełnym wsparciem relacji</p>
                <small>Kliknij aby zobaczyć szczegóły</small>
              </div>
              <div className="setting-section interactive" onClick={() => window.open(`${API}/export-csv/clients`, '_blank')}>
                <h3>📊 Export Klientów</h3>
                <p>Eksportuj wszystkich klientów do pliku CSV</p>
                <small>Kliknij aby pobrać</small>
              </div>
              <div className="setting-section interactive" onClick={() => window.open(`${API}/export-csv/panels`, '_blank')}>
                <h3>📺 Export Paneli</h3>
                <p>Eksportuj wszystkie panele do pliku CSV</p>
                <small>Kliknij aby pobrać</small>
              </div>
            </div>
          </div>
        );
      
      default:
        return <Dashboard setActiveView={setActiveView} />;
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