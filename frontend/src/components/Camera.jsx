import { useRef, useState, useEffect, useMemo } from 'react';
import Webcam from 'react-webcam';

function Camera({ onCapture, isProcessing }) {
  const webcamRef = useRef(null);
  const fileInputRef = useRef(null);
  const [hasPermission, setHasPermission] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isMobile, setIsMobile] = useState(false);
  const [cameraAttempt, setCameraAttempt] = useState(0);
  const [cameraHint, setCameraHint] = useState(null);
  const [isCapturing, setIsCapturing] = useState(false);

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

  // Smart camera hint detection
  useEffect(() => {
    if (!hasPermission || !webcamRef.current) return;

    const checkVideoQuality = () => {
      try {
        const video = webcamRef.current.video;
        if (!video || video.readyState < 2) return;

        const canvas = document.createElement('canvas');
        canvas.width = 100;
        canvas.height = 100;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, 100, 100);

        const imageData = ctx.getImageData(0, 0, 100, 100);
        const data = imageData.data;
        let brightness = 0;

        for (let i = 0; i < data.length; i += 4) {
          brightness += (data[i] + data[i + 1] + data[i + 2]) / 3;
        }

        brightness = brightness / (data.length / 4);

        if (brightness < 80) {
          setCameraHint('💡 Increase lighting');
          setTimeout(() => setCameraHint(null), 3000);
        }
      } catch (err) {
        // Ignore errors
      }
    };

    const interval = setInterval(checkVideoQuality, 3000);
    return () => clearInterval(interval);
  }, [hasPermission]);

  const capturePhoto = () => {
    // Flash animation
    setIsCapturing(true);

    setTimeout(() => {
      const imageSrc = webcamRef.current.getScreenshot();
      setCapturedImage(imageSrc);
      setIsCapturing(false);
    }, 150);
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
            {cameraHint && hasPermission && (
              <div className="camera-hint">
                {cameraHint}
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
                <div className="guide-box">
                  <div className="guide-corners"></div>
                  <div className="scanning-line"></div>
                </div>
              </div>
            )}
            {isCapturing && <div className="capture-flash"></div>}
          </div>
          <div className="camera-controls-lens">
            <button onClick={capturePhoto} className="btn-capture-lens" title="Capture">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
              </svg>
            </button>
            <button onClick={triggerFileInput} className="btn-upload-secondary">
              📁 Upload
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
          <button onClick={handleRetake} className="btn-retake-corner" disabled={isProcessing} title="Retake">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 2v6h-6M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6M21 12a9 9 0 0 1-15 6.7L3 16"/>
            </svg>
          </button>
          <div className="preview">
            <img src={capturedImage} alt="Captured receipt" />
          </div>
          <div className="preview-controls-lens">
            <button onClick={handleConfirm} className="btn-confirm-large" disabled={isProcessing}>
              ✅ Use This Image
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
