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

// Analytics API functions
export const getAnalyticsSummary = async (userId = null) => {
  const params = userId ? { user_id: userId } : {};
  const result = await axios.get(`${API_BASE_URL}/api/analytics/summary`, { params });
  return result.data;
};

export const getSpendingByCategory = async (userId = null) => {
  const params = userId ? { user_id: userId } : {};
  const result = await axios.get(`${API_BASE_URL}/api/analytics/by-category`, { params });
  return result.data;
};

export const getSpendingByMonth = async (userId = null, months = 6) => {
  const params = userId ? { user_id: userId, months } : { months };
  const result = await axios.get(`${API_BASE_URL}/api/analytics/by-month`, { params });
  return result.data;
};

export const getTopStores = async (userId = null, limit = 5) => {
  const params = userId ? { user_id: userId, limit } : { limit };
  const result = await axios.get(`${API_BASE_URL}/api/analytics/top-stores`, { params });
  return result.data;
};

export const getRecentReceipts = async (userId = null, limit = 10) => {
  const params = userId ? { user_id: userId, limit } : { limit };
  const result = await axios.get(`${API_BASE_URL}/api/analytics/recent`, { params });
  return result.data;
};

// Quantity Analytics API functions
export const getQuantitySummary = async (userId = null) => {
  const params = userId ? { user_id: userId } : {};
  const result = await axios.get(`${API_BASE_URL}/api/analytics/quantity/summary`, { params });
  return result.data;
};

export const getTopBulkItems = async (userId = null, limit = 10) => {
  const params = userId ? { user_id: userId, limit } : { limit };
  const result = await axios.get(`${API_BASE_URL}/api/analytics/quantity/bulk-items`, { params });
  return result.data;
};

export const getQuantityByCategory = async (userId = null) => {
  const params = userId ? { user_id: userId } : {};
  const result = await axios.get(`${API_BASE_URL}/api/analytics/quantity/by-category`, { params });
  return result.data;
};

export const getUnitPriceInsights = async (userId = null, limit = 10) => {
  const params = userId ? { user_id: userId, limit } : { limit };
  const result = await axios.get(`${API_BASE_URL}/api/analytics/quantity/unit-prices`, { params });
  return result.data;
};

export const getQuantityTrends = async (userId = null, months = 6) => {
  const params = userId ? { user_id: userId, months } : { months };
  const result = await axios.get(`${API_BASE_URL}/api/analytics/quantity/trends`, { params });
  return result.data;
};
