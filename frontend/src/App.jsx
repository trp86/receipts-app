import { useState } from 'react';
import Camera from './components/Camera';
import ResultDisplay from './components/ResultDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import { uploadReceipt } from './services/api';
import './App.css';

function App() {
  const [view, setView] = useState('camera'); // 'camera' | 'loading' | 'result'
  const [receiptData, setReceiptData] = useState(null);
  const [error, setError] = useState(null);

  const handlePhotoCapture = async (imageData) => {
    setView('loading');
    setError(null);

    try {
      console.log('Sending image to backend...');
      const response = await uploadReceipt(imageData);

      if (response.success && response.data) {
        console.log('Receipt parsed successfully:', response.data);
        setReceiptData(response.data);
        setView('result');
      } else {
        throw new Error('Failed to parse receipt');
      }
    } catch (err) {
      console.error('Upload failed:', err);
      setError(err.message || 'Failed to process receipt. Please try again.');
      setView('camera');
    }
  };

  const handleReset = () => {
    setView('camera');
    setReceiptData(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>📸 Receipt Scanner</h1>
      </header>

      <main className="app-main">
        {view === 'camera' && (
          <Camera onCapture={handlePhotoCapture} />
        )}

        {view === 'loading' && (
          <LoadingSpinner />
        )}

        {view === 'result' && receiptData && (
          <ResultDisplay data={receiptData} onReset={handleReset} />
        )}

        {error && (
          <div className="error-message">
            <p>❌ {error}</p>
            <button onClick={handleReset}>Try Again</button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
