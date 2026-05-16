import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, AlertTriangle } from 'lucide-react';
import { chatWithAssistant } from '../services/api';

const SAMPLE_QUERIES = [
  "How do I disable telemetry in Windows?",
  "Harden the Edge browser against phishing",
  "Prevent users from accessing the webcam",
];

export default function AIAssistant() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I am your local Policy Intelligence Assistant powered by ChromaDB + Llama 3 (RAG).\n\nI can answer questions like:\n• "How do I disable telemetry?"\n• "Harden the Edge browser"\n• "Block access to the webcam"\n\nMake sure Ollama is running before asking questions.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async (text) => {
    const question = text || input.trim();
    if (!question || loading) return;

    setInput('');
    setError(null);
    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setLoading(true);

    try {
      const { answer } = await chatWithAssistant(question);
      setMessages((prev) => [...prev, { role: 'assistant', content: answer }]);
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message;
      setError(detail);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '⚠ Could not reach the AI pipeline. Check that Ollama is running and you have indexed the policies (`python main.py`).', isError: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <div style={{ height: 'calc(100vh - 8rem)', display: 'flex', flexDirection: 'column', gap: '0' }}>
      {/* Header */}
      <div style={{
        padding: '1rem 1.5rem',
        borderBottom: '1px solid #333',
        background: '#1a1a1a',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        borderRadius: '0.5rem 0.5rem 0 0',
      }}>
        <Bot size={22} style={{ color: '#0078D4' }} />
        <div>
          <h2 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: '#fff' }}>Local RAG Assistant</h2>
          <p style={{ margin: 0, fontSize: '0.75rem', color: '#888' }}>Powered by ChromaDB + Ollama (offline)</p>
        </div>
      </div>

      {/* Message list */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem',
        background: '#111',
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            display: 'flex',
            gap: '0.75rem',
            flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
            alignItems: 'flex-start',
          }}>
            {/* Avatar */}
            <div style={{
              width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: msg.role === 'user' ? '#0078D4' : '#2d2d2d',
              border: '1px solid #333',
            }}>
              {msg.role === 'user' ? <User size={16} color="#fff" /> : <Bot size={16} color="#0078D4" />}
            </div>

            {/* Bubble */}
            <div style={{
              maxWidth: '72%',
              padding: '0.875rem 1.1rem',
              borderRadius: msg.role === 'user' ? '1rem 0.25rem 1rem 1rem' : '0.25rem 1rem 1rem 1rem',
              background: msg.role === 'user' ? '#0078D4' : '#1f1f1f',
              border: msg.role === 'user' ? 'none' : '1px solid #333',
              color: msg.isError ? '#fca5a5' : '#e5e7eb',
              fontSize: '0.875rem',
              lineHeight: 1.65,
              whiteSpace: 'pre-wrap',
            }}>
              {msg.content}
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
            <div style={{
              width: 32, height: 32, borderRadius: '50%', background: '#2d2d2d',
              border: '1px solid #333', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            }}>
              <Bot size={16} color="#0078D4" />
            </div>
            <div style={{
              padding: '0.875rem 1.1rem', background: '#1f1f1f', border: '1px solid #333',
              borderRadius: '0.25rem 1rem 1rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem',
            }}>
              <Loader2 size={16} style={{ color: '#0078D4', animation: 'spin 1s linear infinite' }} />
              <span style={{ color: '#9ca3af', fontSize: '0.875rem' }}>Searching policy database…</span>
            </div>
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div style={{
            display: 'flex', gap: '0.5rem', alignItems: 'flex-start',
            background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)',
            borderRadius: '0.5rem', padding: '0.75rem 1rem',
          }}>
            <AlertTriangle size={16} style={{ color: '#f87171', flexShrink: 0, marginTop: 2 }} />
            <p style={{ margin: 0, fontSize: '0.8rem', color: '#fca5a5' }}>{error}</p>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Suggested queries */}
      <div style={{
        padding: '0.75rem 1.5rem', background: '#1a1a1a', borderTop: '1px solid #2a2a2a',
        display: 'flex', gap: '0.5rem', flexWrap: 'wrap',
      }}>
        {SAMPLE_QUERIES.map((q) => (
          <button
            key={q}
            onClick={() => sendMessage(q)}
            disabled={loading}
            style={{
              background: 'transparent', border: '1px solid #333', borderRadius: '1rem',
              padding: '0.3rem 0.75rem', fontSize: '0.75rem', color: '#9ca3af', cursor: 'pointer',
              transition: 'all 0.15s',
            }}
            onMouseOver={e => { e.target.style.borderColor = '#0078D4'; e.target.style.color = '#60a5fa'; }}
            onMouseOut={e => { e.target.style.borderColor = '#333'; e.target.style.color = '#9ca3af'; }}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} style={{
        padding: '1rem 1.5rem', background: '#1a1a1a', borderTop: '1px solid #333',
        display: 'flex', gap: '0.75rem', borderRadius: '0 0 0.5rem 0.5rem',
      }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about hardening Windows policies…"
          disabled={loading}
          style={{
            flex: 1, background: '#111', border: '1px solid #333', borderRadius: '0.5rem',
            padding: '0.75rem 1rem', color: '#e5e7eb', fontSize: '0.9rem', outline: 'none',
          }}
          onFocus={e => e.target.style.borderColor = '#0078D4'}
          onBlur={e => e.target.style.borderColor = '#333'}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            background: loading || !input.trim() ? '#1a3a5c' : '#0078D4',
            border: 'none', borderRadius: '0.5rem', padding: '0.75rem 1.25rem',
            color: '#fff', cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
            display: 'flex', alignItems: 'center', gap: '0.5rem', transition: 'background 0.15s',
          }}
        >
          <Send size={17} />
        </button>
      </form>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
