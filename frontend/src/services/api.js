import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const uploadReceipt = async (imageData) => {
  try {
    // Create FormData
    const formData = new FormData();

    // Check if imageData is an array (multiple images)
    if (Array.isArray(imageData)) {
      console.log(`Uploading ${imageData.length} images...`);

      // Convert each base64 image to blob and append
      for (let i = 0; i < imageData.length; i++) {
        const response = await fetch(imageData[i]);
        const blob = await response.blob();
        formData.append('files', blob, `receipt_part_${i + 1}.jpg`);
      }
    } else {
      // Single image (backward compatible)
      console.log('Uploading single image...');
      const response = await fetch(imageData);
      const blob = await response.blob();
      formData.append('files', blob, 'receipt.jpg');
    }

    // Send to backend
    const result = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return result.data;
  } catch (error) {
    console.error('Upload failed:', error);
    throw error;
  }
};
