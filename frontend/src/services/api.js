import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const uploadReceipt = async (imageData) => {
  try {
    // Convert base64 to blob
    const response = await fetch(imageData);
    const blob = await response.blob();

    // Create FormData
    const formData = new FormData();
    formData.append('file', blob, 'receipt.jpg');

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
