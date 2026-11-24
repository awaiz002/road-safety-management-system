import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import MapView from './components/MapView';
import ReportAccident from './components/ReportAccident';
import RecordManagement from './components/RecordManagement';
import TrafficRules from './components/TrafficRules';
import EmergencyHub from './components/EmergencyHub';
import AuthModal from './components/AuthModal';
import SOSModal from './components/SOSModal';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem('rsms_user');
      return saved ? JSON.parse(saved) : null;
    } catch (e) {
      localStorage.removeItem('rsms_user');
      return null;
    }
  });

  const [accidents, setAccidents] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [rules, setRules] = useState([]);
  const [emergencyContacts, setEmergencyContacts] = useState([]);

  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isSOSModalOpen, setIsSOSModalOpen] = useState(false);
  const [reportInitialCoords, setReportInitialCoords] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [apiNotification, setApiNotification] = useState('');

  // Fetch all core historical accident data from Flask Python backend
  const fetchAllData = async () => {
    try {
      const [accRes, hsRes, anRes, ruleRes, emRes] = await Promise.all([
        fetch('/api/accidents').then(r => r.ok ? r.json() : {}).catch(() => ({})),
        fetch('/api/hotspots').then(r => r.ok ? r.json() : {}).catch(() => ({})),
        fetch('/api/analytics').then(r => r.ok ? r.json() : {}).catch(() => ({})),
        fetch('/api/traffic-rules').then(r => r.ok ? r.json() : {}).catch(() => ({})),
        fetch('/api/emergency-contacts').then(r => r.ok ? r.json() : {}).catch(() => ({})),
      ]);

      if (accRes && accRes.success) setAccidents(accRes.data || []);
      if (hsRes && hsRes.success) setHotspots(hsRes.data || []);
      if (anRes && anRes.success) setAnalytics(anRes);
      if (ruleRes && ruleRes.success) setRules(ruleRes.data || []);
      if (emRes && emRes.success) setEmergencyContacts(emRes.data || []);
    } catch (err) {
      console.error('Error loading data from backend:', err);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  // Handler for Automated Open API Data Generation
  const handleGenerateFromOpenApi = async (count = 15) => {
    setIsGenerating(true);
    try {
      const res = await fetch('/api/accidents/generate-from-api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count, clear_existing: true })
      });
      const data = await res.json();
      if (data.success) {
        setApiNotification(`⚡ Generated ${data.count} records from OpenStreetMap & Weather Open API`);
        setTimeout(() => setApiNotification(''), 4500);
        await fetchAllData();
      }
    } catch (err) {
      console.error('Open API Generation Error:', err);
      setApiNotification('⚠️ Could not connect to Open API service');
      setTimeout(() => setApiNotification(''), 4000);
    } finally {
      setIsGenerating(false);
    }
  };

  // Auth handlers
  const handleAuthSuccess = (user) => {
    setCurrentUser(user);
    localStorage.setItem('rsms_user', JSON.stringify(user));
    fetchAllData();
    setApiNotification('⚡ Live Vijay Nagar crash data freshly synchronized on login!');
    setTimeout(() => setApiNotification(''), 4500);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('rsms_user');
  };

  // Switch to report tab with map clicked coordinates
  const handleSelectReportLocation = (lat, lng) => {
    setReportInitialCoords({ lat, lng });
    setActiveTab('report');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#f8fafc' }}>
      
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        currentUser={currentUser}
        onOpenAuth={() => setIsAuthModalOpen(true)}
        onLogout={handleLogout}
        onOpenSOSModal={() => setIsSOSModalOpen(true)}
      />

      {/* Floating Notification for Open API Activity */}
      {apiNotification && (
        <div style={{
          position: 'fixed',
          top: '80px',
          right: '20px',
          zIndex: 9999,
          background: '#0f172a',
          color: '#ffffff',
          padding: '10px 18px',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
          fontSize: '0.85rem',
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          border: '1px solid #334155',
          animation: 'fadeIn 0.2s ease-in-out'
        }}>
          {apiNotification}
        </div>
      )}

      {/* Main Tab Routing */}
      <main style={{ flex: 1 }}>
        {activeTab === 'dashboard' && (
          <Dashboard
            analytics={analytics}
            hotspots={hotspots}
            recentAccidents={accidents}
            onNavigateTab={setActiveTab}
            onGenerateFromOpenApi={handleGenerateFromOpenApi}
            isGenerating={isGenerating}
          />
        )}

        {activeTab === 'map' && (
          <MapView
            accidents={accidents}
            hotspots={hotspots}
            onSelectReportLocation={handleSelectReportLocation}
            onViewAccidentDetails={(_acc) => {
              setActiveTab('records');
            }}
          />
        )}

        {activeTab === 'report' && (
          <ReportAccident
            currentUser={currentUser}
            initialCoords={reportInitialCoords}
            onReportSubmitted={() => {
              fetchAllData();
            }}
            onSwitchToMap={() => setActiveTab('map')}
          />
        )}

        {activeTab === 'records' && (
          <RecordManagement
            accidents={accidents}
            currentUser={currentUser}
            onRefreshData={fetchAllData}
            onNavigateToMap={() => setActiveTab('map')}
          />
        )}

        {activeTab === 'rules' && (
          <TrafficRules rules={rules} />
        )}

        {activeTab === 'emergency' && (
          <EmergencyHub
            contacts={emergencyContacts}
            onOpenSOSModal={() => setIsSOSModalOpen(true)}
          />
        )}
      </main>

      {/* Footer */}
      <footer style={{
        background: '#ffffff',
        borderTop: '1px solid #e2e8f0',
        padding: '16px 20px',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: '#64748b'
      }}>
        <div>
          Road Safety Management & Analysis System • Focused Study: Vijay Nagar Square, Indore (M.P.)
        </div>
        <div style={{ marginTop: '4px', fontSize: '0.72rem', color: '#94a3b8' }}>
          Major Project • Python Flask • React.js • SQLite • OpenStreetMap
        </div>
      </footer>

      {/* Auth Modal */}
      {isAuthModalOpen && (
        <AuthModal
          isOpen={isAuthModalOpen}
          onClose={() => setIsAuthModalOpen(false)}
          onAuthSuccess={handleAuthSuccess}
          onSuccess={handleAuthSuccess}
        />
      )}

      {/* Emergency SOS Modal */}
      {isSOSModalOpen && (
        <SOSModal
          isOpen={isSOSModalOpen}
          onClose={() => setIsSOSModalOpen(false)}
          contacts={emergencyContacts}
        />
      )}
    </div>
  );
}
