export default function Modal({ file, content, highlightRange, onClose }) {
  return (
    <div className="modalOverlay" onClick={() => setPreviewFile(null)}>
      <div className="modalContent" onClick={(e) => e.stopPropagation()}>
        <h3 className="modalTitle">{file}</h3>
        <pre className="codeBlock">
          {content.split('\n').map((line, index) => {
            const lineNumber = index + 1;

            const isHighlighted =
              highlightRange &&
              highlightRange.start &&
              highlightRange.end &&
              lineNumber >= highlightRange.start &&
              lineNumber <= highlightRange.end;

            return (
              <div key={index} className={isHighlighted ? 'highlightLine' : ''}>
                <span className="lineNumber">{lineNumber}</span>
                <span className="lineContent">{line}</span>
              </div>
            );
          })}
        </pre>

        <button className="closeButton" onClick={() => onClose()}>
          x
        </button>
      </div>
    </div>
  );
}
