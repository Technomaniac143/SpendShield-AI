import { investigations } from '../mocks/investigations';
import { Investigation } from '../types';
// import { apiClient } from './api';

export const investigationApi = {
  // In a real application, this would call:
  // return apiClient.get<Investigation>(`/investigations/${id}`).then(res => res.data);
  getById: async (id: string): Promise<Investigation> => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));
    const inv = investigations.find(i => i.id === id);
    if (!inv) throw new Error('Investigation not found');
    return inv;
  },

  getAll: async (): Promise<Investigation[]> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return investigations;
  },
  
  // Real-time investigation simulation (SSE/WebSocket fallback)
  // This simulates the "Moment of Wow" execution trace over time
  simulateRealtimeInvestigation: (targetId: string, onUpdate: (data: Partial<Investigation>) => void) => {
    let currentStep = 0;
    const inv = investigations[0]; // Use demo investigation for simulation
    
    // Create a deeply cloned, initial empty state for the investigation
    const state: Partial<Investigation> = {
      id: `INVEST-${Date.now()}`,
      targetId,
      targetName: 'ABC Industries',
      targetType: 'SUPPLIER',
      status: 'RUNNING',
      steps: inv.steps.map(s => ({ ...s, status: 'WAITING' })),
      findings: [],
      financialExposure: 0,
      potentialSavings: 0,
      riskScore: 0,
      confidence: 0
    };

    onUpdate({ ...state });

    const interval = setInterval(() => {
      if (currentStep < inv.steps.length) {
        // Mark previous as completed
        if (currentStep > 0 && state.steps) {
          state.steps[currentStep - 1].status = 'COMPLETED';
        }
        
        // Mark current as running
        if (state.steps) {
          state.steps[currentStep].status = 'RUNNING';
        }

        // Add findings progressively based on steps
        if (currentStep === 3) state.findings = [inv.findings[0]];
        if (currentStep === 4) state.findings = [inv.findings[0], inv.findings[1]];
        if (currentStep === 6) state.findings = [...inv.findings];

        // Update financial numbers progressively
        if (currentStep >= 7) {
          state.financialExposure = inv.financialExposure;
          state.potentialSavings = inv.potentialSavings;
          state.riskScore = inv.riskScore;
          state.confidence = inv.confidence;
        }

        onUpdate({ ...state });
        currentStep++;
      } else {
        // Finish
        if (state.steps) state.steps[currentStep - 1].status = 'COMPLETED';
        state.status = 'COMPLETED';
        state.primaryFinding = inv.primaryFinding;
        onUpdate({ ...state });
        clearInterval(interval);
      }
    }, 1500); // 1.5 seconds per step for demo purposes

    return () => clearInterval(interval); // Return cleanup function
  }
};
