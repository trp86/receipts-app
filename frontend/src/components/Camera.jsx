import { useRef, useState, useEffect, useMemo } from 'react';
import Webcam from 'react-webcam';

function Camera({ onCapture, isProcessing }) {
  const webcamRef = useRef(null);
  const fileInputRef = useRef(null);
  const [hasPermission, setHasPermission] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isMobile, setIsMobile] = useState(false);
  const [cameraAttempt, setCameraAttempt] = useState(0);

  // Detect if device is mobile
  useEffect(() => {
    const checkMobile = window.innerWidth <= 768 ||
                        /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
    setIsMobile(checkMobile);
  }, []);

  const handleUserMedia = () => {
    setHasPermission(true);
  };

  const handleUserMediaError = (error) => {
    console.error('Camera error:', error);
    // If first attempt failed on mobile, try fallback
    if (cameraAttempt === 0 && isMobile) {
      console.log('Retrying with fallback camera...');
      setCameraAttempt(1);
    } else {
      setHasPermission(false);
    }
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

  // Adaptive video constraints with fallback
  const videoConstraints = useMemo(() => {
    const baseConstraints = {
      width: { ideal: 1920 },
      height: { ideal: 1080 }
    };

    // First attempt on mobile: try rear camera
    if (cameraAttempt === 0 && isMobile) {
      return {
        ...baseConstraints,
        facingMode: { ideal: 'environment' }
      };
    }

    // Fallback or desktop: use any available camera
    return baseConstraints;
  }, [isMobile, cameraAttempt]);

  if (hasPermission === false) {
    return (
      <div className="camera-error">
        <p>❌ Camera not available</p>
        <p>Please use Upload Image button below</p>
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
              autoPlay={true}
              playsInline={true}
              muted={true}
              screenshotFormat="image/jpeg"
              screenshotQuality={0.95}
              videoConstraints={videoConstraints}
              onUserMedia={handleUserMedia}
              onUserMediaError={handleUserMediaError}
              className="webcam"
            />
            {hasPermission && (
              <div className="capture-guide">
                <div className="guide-box"></div>
              </div>
            )}
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
            <button onClick={handleRetake} className="btn-secondary" disabled={isProcessing}>
              🔄 Retake
            </button>
            <button onClick={handleConfirm} className="btn-primary" disabled={isProcessing}>
              ✅ Use Image
            </button>
          </div>
          {isProcessing && (
            <div className="processing-overlay">
              <div className="spinner"></div>
              <p>Processing receipt...</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Camera;
