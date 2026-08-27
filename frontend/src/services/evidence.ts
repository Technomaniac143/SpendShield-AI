import { apiClient } from './api';

export interface EvidenceResponse {
  eventId: string;
  recordId: string;
  eventType: string;
  timestamp: string;
  sourceType: string;
  sourceId: string | null;
  metadataHash: string | null;
  documentHash: string;
  previousHash: string | null;
  recordHash: string;
  verificationStatus: string;
  status: string;
}

export const evidenceApi = {
  register: async (eventId: string, formData: FormData) => {
    const response = await apiClient.post(`/evidence/${eventId}/register`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getEvidence: async (eventId: string) => {
    const response = await apiClient.get<EvidenceResponse>(`/evidence/${eventId}`);
    return response.data;
  },

  verify: async (eventId: string) => {
    const response = await apiClient.post<{ status: string; detail?: string }>(`/evidence/${eventId}/verify`);
    return response.data;
  },

  getHistory: async (eventId: string) => {
    const response = await apiClient.get(`/evidence/${eventId}/history`);
    return response.data;
  },

  getBlockchain: async (eventId: string) => {
    const response = await apiClient.get(`/evidence/${eventId}/blockchain`);
    return response.data;
  },

  simulateModification: async (eventId: string) => {
    const response = await apiClient.post(`/evidence/${eventId}/simulate-modification`);
    return response.data;
  }
};
