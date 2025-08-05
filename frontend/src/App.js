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
    { key: 'contact-types', label: '📞 Kontakty', icon: '📞' },
    { key: 'payment-methods', label: '💳 Płatności', icon: '💳' },
    { key: 'pricing-config', label: '💰 Cennik', icon: '💰' },
    { key: 'questions', label: '❓ FAQ', icon: '❓' },
    { key: 'smart-tv-apps', label: '📺 Smart TV Apps', icon: '📺' },
    { key: 'android-apps', label: '🤖 Android Apps', icon: '🤖' },
    { key: 'settings', label: '⚙️ Ustawienia', icon: '⚙️' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('tv_panel_token');
    setAuth(false);
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>🛢️ TV Panel SQL</h2>
        <div className="version">v3.0 SQL Edition</div>
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
          <small>🛢️ SQLite Database</small>
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
        <h2>🚀 Zarządzanie danymi JSON</h2>
        <div className="action-buttons">
          <button className="btn-action" onClick={() => window.open(`${API}/export-csv/clients`, '_blank')}>
            📊 Eksport CSV Klientów
          </button>
          <button className="btn-action" onClick={() => window.open(`${API}/export-csv/panels`, '_blank')}>
            📺 Eksport Paneli
          </button>
          <button className="btn-action" onClick={() => alert('Import JSON: Użyj Upload w sekcjach zarządzania')}>
            📥 Import JSON
          </button>
          <button className="btn-action">🔐 Generator haseł</button>
        </div>
      </div>

      <div className="json-data-overview">
        <h2>📋 Przegląd danych JSON</h2>
        <div className="data-grid">
          <div className="data-card">
            <h3>💳 Metody płatności</h3>
            <p>Zarządzaj dostępnymi opcjami płatności</p>
          </div>
          <div className="data-card">
            <h3>💰 Konfiguracja cennika</h3>
            <p>Ustawiaj ceny i pakiety subskrypcji</p>
          </div>
          <div className="data-card">
            <h3>❓ Pytania FAQ</h3>
            <p>Zarządzaj często zadawanymi pytaniami</p>
          </div>
          <div className="data-card">
            <h3>📺 Aplikacje Smart TV</h3>
            <p>Konfiguruj aplikacje dla Smart TV</p>
          </div>
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
        <select
          value={value || ''}
          onChange={(e) => onChange(field.key, e.target.value)}
          disabled={!isEditing}
        >
          <option value="">Wybierz...</option>
          {field.options.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      );
    }
    
    if (field.type === 'textarea') {
      return (
        <textarea
          value={value || ''}
          onChange={(e) => onChange(field.key, e.target.value)}
          rows={3}
          disabled={!isEditing}
        />
      );
    }
    
    if (field.type === 'checkbox') {
      return (
        <input
          type="checkbox"
          checked={value || false}
          onChange={(e) => onChange(field.key, e.target.checked)}
          disabled={!isEditing}
        />
      );
    }
    
    return (
      <input
        type={field.type || 'text'}
        value={value || ''}
        onChange={(e) => onChange(field.key, e.target.value)}
        disabled={!isEditing}
        step={field.type === 'number' ? '0.01' : undefined}
      />
    );
  };

  if (loading) return <div className="loading">Ładowanie {title.toLowerCase()}...</div>;

  return (
    <div className="editable-table">
      <div className="table-header">
        <h1>{icon} {title}</h1>
        <div className="table-controls">
          {canAdd && (
            <button 
              onClick={() => setShowAddForm(!showAddForm)}
              className="btn-primary"
            >
              ➕ Dodaj nowy
            </button>
          )}
        </div>
      </div>

      {message && (
        <div className={`alert ${message.includes('✅') ? 'alert-success' : 'alert-error'}`}>
          {message}
        </div>
      )}

      {showAddForm && canAdd && (
        <form onSubmit={handleCreate} className="add-form">
          <h3>➕ Dodaj nowy element</h3>
          <div className="form-grid">
            {fields.map(field => (
              <div key={field.key} className="form-group">
                <label>{field.label}</label>
                {renderField(field, newItem[field.key], (key, value) => 
                  setNewItem({...newItem, [key]: value}), true
                )}
              </div>
            ))}
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-success">✅ Zapisz</button>
            <button type="button" onClick={() => setShowAddForm(false)} className="btn-secondary">
              ❌ Anuluj
            </button>
          </div>
        </form>
      )}

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              {fields.map(field => (
                <th key={field.key}>{field.label}</th>
              ))}
              <th>Akcje</th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr key={item.id} className={editingItem?.id === item.id ? 'editing' : ''}>
                <td>{item.id}</td>
                {fields.map(field => (
                  <td key={field.key}>
                    {editingItem?.id === item.id ? (
                      renderField(field, editingItem[field.key], (key, value) =>
                        setEditingItem({...editingItem, [key]: value}), true
                      )
                    ) : (
                      <span className={`field-${field.type || 'text'}`}>
                        {field.type === 'checkbox' ? (item[field.key] ? '✅' : '❌') : 
                         item[field.key]?.toString() || '-'}
                      </span>
                    )}
                  </td>
                ))}
                <td>
                  <div className="action-buttons">
                    {editingItem?.id === item.id ? (
                      <>
                        <button 
                          onClick={() => handleUpdate(item.id, editingItem)}
                          className="btn-success"
                          title="Zapisz"
                        >
                          ✅
                        </button>
                        <button 
                          onClick={() => setEditingItem(null)}
                          className="btn-secondary"
                          title="Anuluj"
                        >
                          ❌
                        </button>
                      </>
                    ) : (
                      <>
                        <button 
                          onClick={() => setEditingItem(item)}
                          className="btn-edit"
                          title="Edytuj"
                        >
                          ✏️
                        </button>
                        {canDelete && (
                          <button 
                            onClick={() => handleDelete(item.id)}
                            className="btn-delete"
                            title="Usuń"
                          >
                            🗑️
                          </button>
                        )}
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Clients Component with full editing
const ClientsList = () => {
  return (
    <EditableTable
      title="Lista Klientów IPTV"
      endpoint="/clients"
      icon="👥"
      fields={[
        { key: 'line_id', label: 'ID Linii', type: 'text' },
        { key: 'name', label: 'Nazwa', type: 'text', required: true },
        { key: 'expires_date', label: 'Data wygaśnięcia', type: 'date' },
        { key: 'login', label: 'Login', type: 'text' },
        { key: 'password', label: 'Hasło', type: 'text' },
        { key: 'mac', label: 'MAC', type: 'text' },
        { key: 'contact_value', label: 'Kontakt', type: 'text' },
        { key: 'status', label: 'Status', type: 'select', options: [
          { value: 'active', label: 'Aktywny' },
          { value: 'inactive', label: 'Nieaktywny' },
          { value: 'suspended', label: 'Zawieszony' }
        ]},
        { key: 'notes', label: 'Notatki', type: 'textarea' }
      ]}
    />
  );
};

// Add Client Form
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
          </div>

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
        return (
          <EditableTable
            title="Panele IPTV"
            endpoint="/panels"
            icon="📺"
            fields={[
              { key: 'name', label: 'Nazwa', type: 'text', required: true },
              { key: 'url', label: 'URL', type: 'url' },
              { key: 'description', label: 'Opis', type: 'textarea' }
            ]}
          />
        );
      
      case 'apps':
        return (
          <EditableTable
            title="Aplikacje IPTV"
            endpoint="/apps"
            icon="📱"
            fields={[
              { key: 'name', label: 'Nazwa', type: 'text', required: true },
              { key: 'url', label: 'URL', type: 'url' },
              { key: 'description', label: 'Opis', type: 'textarea' }
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
              { key: 'instructions', label: 'Instrukcje', type: 'textarea' },
              { key: 'icon', label: 'Ikona', type: 'text' }
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
              { key: 'duration_days', label: 'Okres (dni)', type: 'number' },
              { key: 'is_active', label: 'Aktywny', type: 'checkbox' },
              { key: 'discount_percentage', label: 'Zniżka (%)', type: 'number' },
              { key: 'description', label: 'Opis', type: 'textarea' },
              { key: 'features', label: 'Funkcje (JSON)', type: 'textarea' }
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
              { key: 'is_active', label: 'Aktywne', type: 'checkbox' }
            ]}
          />
        );
      
      case 'smart-tv-apps':
        return (
          <EditableTable
            title="Aplikacje Smart TV"
            endpoint="/smart-tv-apps"
            icon="📺"
            fields={[
              { key: 'name', label: 'Nazwa', type: 'text', required: true },
              { key: 'platform', label: 'Platforma', type: 'text' },
              { key: 'download_url', label: 'URL pobierania', type: 'url' },
              { key: 'version', label: 'Wersja', type: 'text' },
              { key: 'is_active', label: 'Aktywna', type: 'checkbox' },
              { key: 'instructions', label: 'Instrukcje', type: 'textarea' },
              { key: 'requirements', label: 'Wymagania', type: 'textarea' }
            ]}
            canAdd={true} // Enable adding new Smart TV apps
          />
        );
      
      case 'android-apps':
        return (
          <EditableTable
            title="Aplikacje Android"
            endpoint="/android-apps"
            icon="🤖"
            fields={[
              { key: 'name', label: 'Nazwa', type: 'text', required: true },
              { key: 'package_name', label: 'Nazwa pakietu', type: 'text' },
              { key: 'download_url', label: 'URL pobierania', type: 'url' },
              { key: 'version', label: 'Wersja', type: 'text' },
              { key: 'is_active', label: 'Aktywna', type: 'checkbox' },
              { key: 'minimum_android_version', label: 'Min. Android', type: 'text' },
              { key: 'file_size', label: 'Rozmiar pliku', type: 'text' }
            ]}
            canAdd={true} // Enable adding new Android apps
          />
        );
      
      case 'settings':
        return (
          <div className="settings">
            <h1>⚙️ Ustawienia systemu</h1>
            <div className="settings-grid">
              <div className="setting-section">
                <h3>🛢️ Baza danych SQL</h3>
                <p>System działa na SQLite z pełnym wsparciem relacji</p>
              </div>
              <div className="setting-section">
                <h3>📊 Import/Export</h3>
                <p>Wszystkie dane można eksportować do CSV</p>
              </div>
              <div className="setting-section">
                <h3>✏️ Edycja inline</h3>
                <p>Wszystkie tabele obsługują edycję w miejscu</p>
              </div>
            </div>
          </div>
        );
      
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