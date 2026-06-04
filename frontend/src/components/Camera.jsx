import { useRef, useState } from 'react';
import Webcam from 'react-webcam';

function Camera({ onCapture }) {
  const webcamRef = useRef(null);
  const fileInputRef = useRef(null);
  const [hasPermission, setHasPermission] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);

  const handleUserMedia = () => {
    setHasPermission(true);
  };

  const handleUserMediaError = () => {
    setHasPermission(false);
  };

  const capturePhoto = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
  };

  const handleConfirm = () => {
    if (capturedImage) {
      onCapture(capturedImage);
    }
  };

  const handleRetake = () => {
    setCapturedImage(null);
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCapturedImage(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const videoConstraints = {
    facingMode: { ideal: 'environment' }, // Use rear camera on mobile
    width: { ideal: 1920 },
    height: { ideal: 1080 }
  };

  if (hasPermission === false) {
    return (
      <div className="camera-error">
        <p>❌ Camera permission denied</p>
        <p>Please enable camera access to scan receipts</p>
      </div>
    );
  }

  return (
    <div className="camera-container">
      {!capturedImage ? (
        <>
          <div className="camera-view">
            {hasPermission === null && (
              <div className="camera-loading">
                <p>📷 Initializing camera...</p>
              </div>
            )}
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              screenshotQuality={0.95}
              videoConstraints={videoConstraints}
              onUserMedia={handleUserMedia}
              onUserMediaError={handleUserMediaError}
              className="webcam"
            />
          </div>
          <div className="camera-controls">
            <button onClick={capturePhoto} className="btn-capture">
              📸 Capture Receipt
            </button>
            <button onClick={triggerFileInput} className="btn-upload">
              📁 Upload Image
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
          </div>
        </>
      ) : (
        <>
          <div className="preview">
            <img src={capturedImage} alt="Captured receipt" />
          </div>
          <div className="preview-controls">
            <button onClick={handleRetake} className="btn-secondary">
              ↺ Retake
            </button>
            <button onClick={handleConfirm} className="btn-primary">
              ✓ Process Receipt
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default Camera;
