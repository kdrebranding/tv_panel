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
        <h2>📺 TV Panel</h2>
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
        <button onClick={handleLogout} className="btn-logout">
          🚪 Wyloguj
        </button>
      </div>
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

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

  if (loading) return <div className="loading">Ładowanie statystyk...</div>;

  return (
    <div className="dashboard">
      <h1>📊 Panel Główny</h1>
      
      <div className="stats-grid">
        <div className="stat-card total">
          <div className="stat-number">{stats.total_clients || 0}</div>
          <div className="stat-label">Wszyscy klienci</div>
        </div>
        
        <div className="stat-card active">
          <div className="stat-number">{stats.active_clients || 0}</div>
          <div className="stat-label">Aktywni klienci</div>
        </div>
        
        <div className="stat-card warning">
          <div className="stat-number">{stats.expiring_soon || 0}</div>
          <div className="stat-label">Wygasający wkrótce</div>
        </div>
        
        <div className="stat-card danger">
          <div className="stat-number">{stats.expired_clients || 0}</div>
          <div className="stat-label">Wygasłe licencje</div>
        </div>
      </div>
      
      <div className="quick-actions">
        <h2>🚀 Szybkie Akcje</h2>
        <div className="action-buttons">
          <button className="btn-action">📊 Raport miesięczny</button>
          <button className="btn-action">📧 Wyślij przypomnienia</button>
          <button className="btn-action">📥 Import klientów</button>
          <button className="btn-action">🔐 Generator haseł</button>
        </div>
      </div>
    </div>
  );
};

// Clients List Component
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
          <button className="btn-bulk-delete">
            🗑️ Usuń zaznaczone ({selectedClients.length})
          </button>
        </div>
      )}
    </div>
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

// Simple management components for panels, apps, etc.
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
          <p>Panel ustawień w przygotowaniu...</p>
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