import { useEffect, useState } from 'react';

const API = 'http://localhost:5000/api';

export default function App() {
  const [length, setLength] = useState(16);
  const [options, setOptions] = useState({ uppercase: true, lowercase: true, numbers: true, symbols: true });
  const [password, setPassword] = useState('');
  const [strength, setStrength] = useState(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [apiOnline, setApiOnline] = useState(false);

  useEffect(() => {
    fetch(`${API}/health`).then(r => r.ok && setApiOnline(true)).catch(() => setApiOnline(false));
  }, []);

  async function generate() {
    setBusy(true); setMessage('');
    try {
      const response = await fetch(`${API}/generate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ length: Number(length), ...options })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Could not generate password.');
      setPassword(data.password); setStrength(data.strength);
    } catch (error) { setMessage(error.message); }
    finally { setBusy(false); }
  }

  async function copyPassword() {
    if (!password) return;
    try { await navigator.clipboard.writeText(password); setMessage('Password copied to clipboard.'); }
    catch { setMessage('Clipboard access unavailable. Select and copy the password manually.'); }
  }

  function toggle(key) { setOptions(current => ({ ...current, [key]: !current[key] })); }

  return <main className="page">
    <nav className="topbar"><div className="brand"><span className="brand-icon">◆</span> SecureKey</div><span className={`status ${apiOnline ? 'online' : 'offline'}`}>{apiOnline ? 'API connected' : 'API disconnected'}</span></nav>
    <section className="hero">
      <div className="eyebrow">PASSWORD SECURITY TOOL</div>
      <h1>Create stronger<br/><span>passwords.</span></h1>
      <p className="intro">Generate unique, hard-to-guess passwords in seconds. Customize the rules to fit your needs.</p>
      <section className="generator card">
        <div className="section-heading"><div><h2>Your password</h2><p>Generated securely by the backend</p></div><span className="lock">⌑</span></div>
        <div className="password-box"><code>{password || 'Click generate to create a password'}</code><button className="copy" onClick={copyPassword} disabled={!password} aria-label="Copy password">Copy</button></div>
        {strength && <div className="strength-row"><span>Strength: <b>{strength.label}</b></span><div className="strength-bars">{[1,2,3,4,5].map(n => <i key={n} className={n <= strength.score ? 'filled' : ''}/>)}</div></div>}
        <div className="divider"/>
        <div className="length-row"><label htmlFor="length">Password length</label><strong>{length}</strong></div>
        <input id="length" className="range" type="range" min="8" max="64" value={length} onChange={e => setLength(e.target.value)} />
        <div className="range-labels"><span>8 characters</span><span>64 characters</span></div>
        <h3>Include character types</h3>
        <div className="options">
          {[
            ['uppercase','Uppercase letters','A–Z'], ['lowercase','Lowercase letters','a–z'],
            ['numbers','Numbers','0–9'], ['symbols','Symbols','!@#']
          ].map(([key,label,example]) => <label className="option" key={key}><input type="checkbox" checked={options[key]} onChange={() => toggle(key)}/><span className="checkmark"/><span className="option-text">{label}<small>{example}</small></span></label>)}
        </div>
        <button className="generate" onClick={generate} disabled={busy}>{busy ? 'Generating…' : '✦  Generate password'}</button>
        {message && <p className="message" role="status">{message}</p>}
      </section>
      <div className="features"><div><span>01</span><b>Secure randomness</b><small>Uses Python's secrets module</small></div><div><span>02</span><b>Your rules</b><small>Choose length and complexity</small></div><div><span>03</span><b>Instant feedback</b><small>Check password strength</small></div></div>
      <footer>Built with React + Flask · Educational project</footer>
    </section>
  </main>;
}
