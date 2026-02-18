import { useEffect } from 'react';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';

function MessageRenderer({ content }) {
  useEffect(() => {
    Prism.highlightAll();
  }, [content]);

  const renderContent = () => {
    // Convert triple backtick blocks to <pre><code>
    const parts = content.split(/```/g);

    return parts.map((part, index) => {
      // Code block (odd index)
      if (index % 2 === 1) {
        return (
          <pre key={index} className="codeBlock">
            <code className="language-javascript">{part.trim()}</code>
          </pre>
        );
      }

      // Normal text — convert file paths to clickable links
      const withLinks = part.replace(/(src\/[^\s)]+)/g, `<span class="fileLink">$1</span>`);

      return <div key={index} dangerouslySetInnerHTML={{ __html: withLinks }} />;
    });
  };

  return <div>{renderContent()}</div>;
}

export default MessageRenderer;
