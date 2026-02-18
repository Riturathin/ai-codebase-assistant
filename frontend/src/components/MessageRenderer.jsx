function MessageRenderer({ content, onFileClick }) {
  const renderText = (text) => {
    const lines = text.split('\n');

    return lines.map((line, index) => {
      // 🔹 Detect numbered question header
      if (line.startsWith('##Q##')) {
        const cleanLine = line.replace('##Q##', '').trim();

        return (
          <div key={index} className="questionHeader">
            {cleanLine}
          </div>
        );
      }

      // 🔹 File links
      const parts = line.split(/(`?src\/[^\s)`]+`?)/g);

      return (
        <div key={index}>
          {parts.map((part, i) => {
            if (part.startsWith('src/') || part.startsWith('`src/')) {
              const clean = part.replace(/`/g, '');

              return (
                <span key={i} className="fileLink" onClick={() => onFileClick(clean)}>
                  {part}
                </span>
              );
            }

            if (part.includes('`')) {
              const inlineParts = part.split(/`([^`]+)`/g);

              return inlineParts.map((p, j) =>
                j % 2 === 1 ? (
                  <span key={j} className="inlineCode">
                    {p}
                  </span>
                ) : (
                  <span key={j}>{p}</span>
                )
              );
            }

            return <span key={i}>{part}</span>;
          })}
        </div>
      );
    });
  };

  return <div>{renderText(content)}</div>;
}

export default MessageRenderer;
