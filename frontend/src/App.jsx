import { useState, useRef, useEffect } from 'react';
import MessageRenderer from './components/MessageRenderer';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [repoId, setRepoId] = useState(''); // Empty by default
  const [loading, setLoading] = useState(false);

  const assistantIndexRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading || !repoId.trim()) return;

    setLoading(true);

    const userMessage = { role: 'user', content: input };
    const assistantMessage = { role: 'assistant', content: '' };

    setMessages((prev) => {
      const updated = [...prev, userMessage, assistantMessage];
      assistantIndexRef.current = updated.length - 1;
      return updated;
    });

    try {
      const response = await fetch('http://127.0.0.1:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repo_id: repoId,
          question: input,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch response');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let done = false;

      let fullText = '';

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;

        if (value) {
          const chunk = decoder.decode(value, { stream: true });

          // Prevent duplication
          if (!fullText.endsWith(chunk)) {
            fullText += chunk;

            setMessages((prev) => {
              const updated = [...prev];
              const index = assistantIndexRef.current;

              if (index !== null && updated[index]) {
                updated[index].content = fullText;
              }

              return updated;
            });
          }
        }
      }
    } catch (error) {
      console.error(error);

      setMessages((prev) => {
        const updated = [...prev];
        const index = assistantIndexRef.current;

        if (index !== null && updated[index]) {
          updated[index].content = 'Error retrieving response from server.';
        }

        return updated;
      });
    }

    setInput('');
    setLoading(false);
  };

  return (
    <div className="page">
      <div className="container">
        <h1 className="title">AI Codebase Assistant</h1>

        {/* Repo Input */}
        <div style={{ marginBottom: '15px' }}>
          <input
            style={{
              padding: '8px',
              width: '100%',
              borderRadius: '6px',
              border: '1px solid #ccc',
            }}
            placeholder="Enter repo id (must be ingested first)"
            value={repoId}
            onChange={(e) => setRepoId(e.target.value)}
          />

          {!repoId && (
            <div style={{ fontSize: '12px', opacity: 0.6, marginTop: '5px' }}>
              Please enter a repo id before asking questions.
            </div>
          )}
        </div>

        {/* Chat Window */}
        <div className="chatWindow">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role === 'user' ? 'user' : 'assistant'}`}>
              <div className="role">{msg.role === 'user' ? 'You' : 'Assistant'}</div>
              <div className="content">
                <MessageRenderer content={msg.content} />
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Input Row */}
        <div className="inputRow">
          <input
            className="input"
            placeholder="Ask about the codebase..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            disabled={!repoId.trim()}
          />

          <button className="button" onClick={sendMessage} disabled={loading || !repoId.trim()}>
            {loading ? 'Thinking...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
