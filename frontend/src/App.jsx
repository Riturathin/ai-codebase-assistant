import { useState, useRef, useEffect } from 'react';
import MessageRenderer from './components/MessageRenderer';
import Modal from './commons/Modal';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [repoId, setRepoId] = useState(''); // Empty by default
  const [loading, setLoading] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);
  const [previewContent, setPreviewContent] = useState('');
  const [highlightRange, setHighlightRange] = useState(null);

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

  const handlePreviewFile = (filePath) => {
    setPreviewFile(filePath);
    setPreviewContent('');
    setHighlightRange(null);
  };

  return (
    <div className="page">
      <div className="container">
        <h2 className="title">AI Codebase Assistant</h2>

        {/* Repo Input */}
        <div style={{ marginBottom: '15px' }}>
          <input
            className="repo-input"
            placeholder="Enter a valid repo name (e.g. user/repo or github.com/user/repo)"
            value={repoId}
            onChange={(e) => setRepoId(e.target.value)}
          />

          {!repoId && (
            <div style={{ fontSize: '12px', opacity: 0.6, color: '#fff', marginTop: '5px' }}>
              Enter a valid repo name.
            </div>
          )}
        </div>

        {/* Chat Window */}
        <div className="chatWindow">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role === 'user' ? 'user' : 'assistant'}`}>
              <div className="role">{msg.role === 'user' ? 'You' : 'Assistant'}</div>
              <div className="content">
                <MessageRenderer
                  content={msg.content}
                  onFileClick={async (filePath, startLine, endLine) => {
                    const cleanPath = filePath.replace(/[`"' ]/g, '');

                    const res = await fetch(
                      `http://127.0.0.1:8000/file?repo_id=${repoId}&file_path=${encodeURIComponent(cleanPath)}`
                    );

                    if (!res.ok) {
                      console.error('File fetch failed');
                      return;
                    }

                    const data = await res.json();

                    setPreviewFile(filePath);
                    setPreviewContent(data.content);
                    setHighlightRange({ start: startLine, end: endLine });
                  }}
                />
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Input Row */}
        <div className="inputRow">
          <textarea
            id="chatbot-textarea"
            className="input"
            placeholder="Ask about the codebase..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault(); // prevent newline
                sendMessage();
              }
            }}
            disabled={!repoId.trim()}
          />

          <button className="button" onClick={sendMessage} disabled={loading || !repoId.trim()}>
            {loading ? 'Thinking...' : 'Send'}
          </button>
        </div>
      </div>
      {previewFile && (
        <Modal
          title={previewFile}
          file={previewFile}
          content={previewContent}
          highlightRange={highlightRange}
          onClose={() => handlePreviewFile(null)}
        />
      )}
    </div>
  );
}

export default App;
