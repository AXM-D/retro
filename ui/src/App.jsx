import React, { useState, useEffect, useCallback } from 'react'

const API = '/api/v1'

function App() {
  const [view, setView] = useState('dashboard')
  const [dashboard, setDashboard] = useState(null)
  const [events, setEvents] = useState([])
  const [attackers, setAttackers] = useState([])
  const [sensors, setSensors] = useState([])
  const [countermeasures, setCountermeasures] = useState([])
  const [protection, setProtection] = useState({ blocked_ips: [], blocked_countries: [], blocked_domains: [] })
  const [settings, setSettings] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async () => {
    try {
      const [dashRes, eventsRes, attackersRes, sensorsRes, cmRes, protRes, settingsRes] = await Promise.all([
        fetch(`${API}/dashboard`),
        fetch(`${API}/events?limit=50`),
        fetch(`${API}/attackers`),
        fetch(`${API}/sensors`),
        fetch(`${API}/countermeasures`),
        fetch(`${API}/protection`),
        fetch(`${API}/settings`),
      ])
      if (dashRes.ok) setDashboard(await dashRes.json())
      if (eventsRes.ok) setEvents(await eventsRes.json())
      if (attackersRes.ok) setAttackers(await attackersRes.json())
      if (sensorsRes.ok) setSensors(await sensorsRes.json())
      if (cmRes.ok) setCountermeasures(await cmRes.json())
      if (protRes.ok) setProtection(await protRes.json())
      if (settingsRes.ok) setSettings(await settingsRes.json())
      setError(null)
    } catch (e) {
      setError('Connection error - make sure RETRO server is running on port 8500')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData(); const iv = setInterval(fetchData, 5000); return () => clearInterval(iv) }, [fetchData])

  const toggleSensor = async (name, action) => {
    try {
      await fetch(`${API}/sensors/${name}/${action}`, { method: 'POST' })
      fetchData()
    } catch (e) { setError(`Failed to ${action} sensor`) }
  }

  const executeCountermeasure = async (action, target, targetType = 'ip') => {
    try {
      await fetch(`${API}/countermeasures`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, target, target_type: targetType }),
      })
      fetchData()
    } catch (e) { setError('Failed to execute countermeasure') }
  }

  const blockIp = async (ip) => {
    try {
      await fetch(`${API}/protection/block/${ip}`, { method: 'POST' })
      fetchData()
    } catch (e) { setError('Failed to block IP') }
  }

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#0d1117', color: '#58a6ff', fontSize: '18px' }}>
      <div>
        <div style={{ textAlign: 'center', marginBottom: 16, fontSize: 32, fontWeight: 'bold', color: '#f78166' }}>RETRO</div>
        <div>Loading...</div>
      </div>
    </div>
  )

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar view={view} setView={setView} dashboard={dashboard} />
      <main style={{ flex: 1, padding: 24, overflow: 'auto' }}>
        {error && <div style={{ background: '#da3633', color: 'white', padding: '12px 16px', borderRadius: 8, marginBottom: 16 }}>{error}</div>}
        {view === 'dashboard' && <DashboardView dashboard={dashboard} events={events} />}
        {view === 'events' && <EventsView events={events} attackers={attackers} onInvestigate={(id) => fetch(`${API}/osint/investigate`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ event_id: id }) })} />}
        {view === 'attackers' && <AttackersView attackers={attackers} onBlock={blockIp} onOsint={async (ip) => { const r = await fetch(`${API}/osint/ip/${ip}`); setView('dashboard') }} />}
        {view === 'sensors' && <SensorsView sensors={sensors} onToggle={toggleSensor} />}
        {view === 'countermeasures' && <CountermeasuresView countermeasures={countermeasures} onExecute={executeCountermeasure} />}
        {view === 'protection' && <ProtectionView protection={protection} />}
        {view === 'settings' && <SettingsView settings={settings} />}
      </main>
    </div>
  )
}

function Sidebar({ view, setView, dashboard }) {
  const items = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'events', label: 'Events', icon: '⚡' },
    { id: 'attackers', label: 'Attackers', icon: '🎯' },
    { id: 'sensors', label: 'Sensors', icon: '📡' },
    { id: 'countermeasures', label: 'Countermeasures', icon: '🛡️' },
    { id: 'protection', label: 'Protection', icon: '🔒' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ]
  return (
    <nav style={{ width: 220, background: '#161b22', borderRight: '1px solid #30363d', padding: '16px 0', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '0 16px 24px', fontSize: 24, fontWeight: 'bold', color: '#f78166', letterSpacing: 2 }}>RETRO</div>
      {items.map(item => (
        <button key={item.id} onClick={() => setView(item.id)}
          style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 16px', border: 'none', background: view === item.id ? '#1c2128' : 'transparent', color: view === item.id ? '#f78166' : '#8b949e', cursor: 'pointer', fontSize: 14, textAlign: 'left', borderLeft: view === item.id ? '3px solid #f78166' : '3px solid transparent' }}>
          <span>{item.icon}</span> {item.label}
          {item.id === 'events' && dashboard?.total_events > 0 && <span style={{ marginLeft: 'auto', background: '#da3633', color: 'white', borderRadius: 12, padding: '1px 8px', fontSize: 11 }}>{dashboard.total_events}</span>}
        </button>
      ))}
      <div style={{ marginTop: 'auto', padding: '16px', fontSize: 11, color: '#484f58', textAlign: 'center' }}>RETRO v0.1.0<br/>Powered by TaQ Engine</div>
    </nav>
  )
}

function DashboardView({ dashboard, events }) {
  if (!dashboard) return <div>Loading...</div>
  const stats = [
    { label: 'Total Events', value: dashboard.total_events, color: '#58a6ff' },
    { label: 'Unique Attackers', value: dashboard.unique_attackers, color: '#f78166' },
    { label: 'Blocked', value: dashboard.blocked_attackers, color: '#238636' },
    { label: 'Reported', value: dashboard.reported_attackers, color: '#d29922' },
  ]
  return (
    <div>
      <h1 style={{ fontSize: 28, marginBottom: 24, color: '#f78166' }}>Dashboard</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 32 }}>
        {stats.map(s => (
          <div key={s.label} style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: 20 }}>
            <div style={{ color: '#8b949e', fontSize: 13, marginBottom: 8 }}>{s.label}</div>
            <div style={{ fontSize: 36, fontWeight: 'bold', color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>
      <h2 style={{ color: '#58a6ff', marginBottom: 16 }}>Recent Events</h2>
      <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, overflow: 'hidden' }}>
        {events.slice(0, 10).map(e => (
          <div key={e.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', borderBottom: '1px solid #30363d', fontSize: 13 }}>
            <span style={{ color: '#f78166' }}>{e.source_ip}</span>
            <span style={{ color: '#8b949e' }}>{e.event_type}</span>
            <span style={{ color: e.threat_score > 0.5 ? '#da3633' : '#8b949e' }}>Score: {e.threat_score.toFixed(2)}</span>
            <span style={{ color: '#484f58' }}>{new Date(e.timestamp).toLocaleString()}</span>
          </div>
        ))}
        {events.length === 0 && <div style={{ padding: 24, textAlign: 'center', color: '#484f58' }}>No events yet. Start sensors from the Sensors tab.</div>}
      </div>
    </div>
  )
}

function EventsView({ events, attackers }) {
  const threatColor = (s) => s >= 0.7 ? '#da3633' : s >= 0.4 ? '#d29922' : '#238636'
  return (
    <div>
      <h1 style={{ fontSize: 28, marginBottom: 24, color: '#58a6ff' }}>Events</h1>
      <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', padding: '12px 16px', background: '#1c2128', fontSize: 12, color: '#8b949e', fontWeight: 'bold' }}>
          <span>Source</span><span>Type</span><span>Sensor</span><span>Score</span><span>Time</span>
        </div>
        {events.map(e => (
          <div key={e.id} style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', padding: '10px 16px', borderBottom: '1px solid #30363d', fontSize: 13 }}>
            <span style={{ color: '#f78166' }}>{e.source_ip}</span>
            <span>{e.event_type}</span>
            <span style={{ color: '#8b949e' }}>{e.sensor}</span>
            <span style={{ color: threatColor(e.threat_score) }}>{e.threat_score.toFixed(2)}</span>
            <span style={{ color: '#484f58', fontSize: 12 }}>{new Date(e.timestamp).toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function AttackersView({ attackers, onBlock }) {
  return (
    <div>
      <h1 style={{ fontSize: 28, marginBottom: 24, color: '#f78166' }}>Attackers</h1>
      <div style={{ display: 'grid', gap: 12 }}>
        {attackers.map(a => (
          <div key={a.ip} style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span style={{ fontSize: 16, fontWeight: 'bold', color: '#f78166' }}>{a.ip}</span>
              <div style={{ display: 'flex', gap: 8 }}>
                <span style={{ background: a.blocked ? '#238636' : '#30363d', padding: '2px 8px', borderRadius: 12, fontSize: 11 }}>{a.blocked ? 'Blocked' : 'Active'}</span>
                <span style={{ color: '#8b949e' }}>Score: {a.threat_score.toFixed(2)}</span>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 16, fontSize: 13, color: '#8b949e' }}>
              <span>Events: {a.total_events}</span>
              <span>Types: {a.event_types?.join(', ') || 'N/A'}</span>
              <span>First: {new Date(a.first_seen).toLocaleDateString()}</span>
            </div>
            {!a.blocked && <button onClick={() => onBlock(a.ip)} style={{ marginTop: 8, background: '#da3633', color: 'white', border: 'none', padding: '6px 16px', borderRadius: 6, cursor: 'pointer', fontSize: 12 }}>Block IP</button>}
          </div>
        ))}
        {attackers.length === 0 && <div style={{ padding: 24, textAlign: 'center', color: '#484f58' }}>No attackers detected yet.</div>}
      </div>
    </div>
  )
}

function SensorsView({ sensors, onToggle }) {
  return (
    <div>
      <h1 style={{ fontSize: 28, marginBottom: 24, color: '#58a6ff' }}>Sensors</h1>
      <div style={{ display: 'grid', gap: 12 }}>
        {sensors.map(s => (
          <div key={s.name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: 16 }}>
            <div>
              <div style={{ fontWeight: 'bold', marginBottom: 4 }}>{s.name}</div>
              <div style={{ fontSize: 12, color: '#8b949e' }}>Port: {s.config?.port || 'N/A'} | Enabled: {s.config?.enabled ? 'Yes' : 'No'}</div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: s.running ? '#238636' : '#da3633' }} />
              <button onClick={() => onToggle(s.name, s.running ? 'stop' : 'start')}
                style={{ background: s.running ? '#da3633' : '#238636', color: 'white', border: 'none', padding: '6px 16px', borderRadius: 6, cursor: 'pointer', fontSize: 12 }}>
                {s.running ? 'Stop' : 'Start'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function CountermeasuresView({ countermeasures, onExecute }) {
  const [target, setTarget] = useState('')
  const [action, setAction] = useState('firewall_block')
  const actions = ['firewall_block', 'abuse_report', 'dns_block', 'threat_feed', 'takedown_assist']
  return (
    <div>
      <h1 style={{ fontSize: 28, marginBottom: 24, color: '#d29922' }}>Countermeasures</h1>
      <div style={{ display: 'flex', gap: 8, marginBottom: 24, background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: 16 }}>
        <select value={action} onChange={e => setAction(e.target.value)}
          style={{ background: '#0d1117', color: '#c9d1d9', border: '1px solid #30363d', borderRadius: 6, padding: '8px 12px' }}>
          {actions.map(a => <option key={a} value={a}>{a}</option>)}
        </select>
        <input placeholder="Target (IP, domain, etc)" value={target} onChange={e => setTarget(e.target.value)}
          style={{ flex: 1, background: '#0d1117', color: '#c9d1d9', border: '1px solid #30363d', borderRadius: 6, padding: '8px 12px' }} />
        <button onClick={() => onExecute(action, target)}
          style={{ background: '#d29922', color: 'black', border: 'none', padding: '8px 16px', borderRadius: 6, cursor: 'pointer', fontWeight: 'bold' }}>Execute</button>
      </div>
      <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, overflow: 'hidden' }}>
        {countermeasures.map(cm => (
          <div key={cm.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', borderBottom: '1px solid #30363d', fontSize: 13 }}>
            <span style={{ color: '#f78166' }}>{cm.action}</span>
            <span>{cm.target}</span>
            <span style={{ color: cm.status === 'blocked' || cm.status === 'reported' ? '#238636' : '#8b949e' }}>{cm.status}</span>
            <span style={{ color: '#484f58' }}>{cm.executed_at}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function ProtectionView({ protection }) {
  return (
    <div>
      <h1 style={{ fontSize: 28, marginBottom: 24, color: '#238636' }}>Protection</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
        <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: 16 }}>
          <h3 style={{ color: '#58a6ff', marginBottom: 12 }}>Blocked IPs ({protection.blocked_ips?.length || 0})</h3>
          {protection.blocked_ips?.map(ip => <div key={ip} style={{ padding: '4px 0', fontSize: 13, color: '#da3633' }}>🛑 {ip}</div>)}
          {(!protection.blocked_ips || protection.blocked_ips.length === 0) && <div style={{ color: '#484f58', fontSize: 13 }}>No IPs blocked</div>}
        </div>
        <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: 16 }}>
          <h3 style={{ color: '#58a6ff', marginBottom: 12 }}>Blocked Countries ({protection.blocked_countries?.length || 0})</h3>
          {protection.blocked_countries?.map(c => <div key={c} style={{ padding: '4px 0', fontSize: 13, color: '#d29922' }}>🌍 {c}</div>)}
          {(!protection.blocked_countries || protection.blocked_countries.length === 0) && <div style={{ color: '#484f58', fontSize: 13 }}>No countries blocked</div>}
        </div>
        <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: 16 }}>
          <h3 style={{ color: '#58a6ff', marginBottom: 12 }}>Blocked Domains ({protection.blocked_domains?.length || 0})</h3>
          {protection.blocked_domains?.map(d => <div key={d} style={{ padding: '4px 0', fontSize: 13, color: '#d29922' }}>🔗 {d}</div>)}
          {(!protection.blocked_domains || protection.blocked_domains.length === 0) && <div style={{ color: '#484f58', fontSize: 13 }}>No domains blocked</div>}
        </div>
      </div>
    </div>
  )
}

function SettingsView({ settings }) {
  if (!settings) return <div>Loading...</div>
  return (
    <div>
      <h1 style={{ fontSize: 28, marginBottom: 24, color: '#8b949e' }}>Settings</h1>
      <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: 20 }}>
        <div style={{ display: 'grid', gap: 12 }}>
          {Object.entries(settings).filter(([k]) => !['sensors'].includes(k)).map(([key, value]) => (
            <div key={key} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #30363d', fontSize: 14 }}>
              <span style={{ color: '#8b949e' }}>{key.replace(/_/g, ' ')}</span>
              <span>{typeof value === 'boolean' ? (value ? '✅' : '❌') : String(value)}</span>
            </div>
          ))}
        </div>
      </div>
      <h2 style={{ color: '#58a6ff', margin: '24px 0 12px', fontSize: 18 }}>Sensors</h2>
      <div style={{ display: 'grid', gap: 8 }}>
        {Object.entries(settings.sensors || {}).map(([name, cfg]) => (
          <div key={name} style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: 12, fontSize: 13 }}>
            <span style={{ fontWeight: 'bold', color: '#f78166' }}>{name}</span>
            <span style={{ marginLeft: 16, color: '#8b949e' }}>Enabled: {cfg.enabled ? '✅' : '❌'}</span>
            {cfg.port && <span style={{ marginLeft: 16, color: '#8b949e' }}>Port: {cfg.port}</span>}
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
