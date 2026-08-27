from typing import List, Dict, Any
import numpy as np

class PriceAnomalyEngine:
    
    @staticmethod
    def detect_price_anomaly(current_price: float, historical_prices: List[float], contract_price: float = None) -> Dict[str, Any]:
        """
        Detects if a price is anomalous compared to history or contract.
        Uses robust statistics (Median Absolute Deviation).
        """
        if contract_price is not None:
            variance = (current_price - contract_price) / contract_price
            return {
                "is_anomalous": abs(variance) > 0.05,
                "variance_percent": round(variance * 100, 2),
                "expected_price": contract_price,
                "baseline_type": "CONTRACT",
                "score": min(100.0, abs(variance) * 500)
            }
            
        if not historical_prices or len(historical_prices) < 3:
            return {
                "is_anomalous": False,
                "variance_percent": 0.0,
                "expected_price": current_price,
                "baseline_type": "INSUFFICIENT_DATA",
                "score": 0.0
            }
            
        median = np.median(historical_prices)
        if median == 0:
            return {"is_anomalous": False, "variance_percent": 0.0, "expected_price": 0.0, "baseline_type": "ZERO_MEDIAN", "score": 0}
            
        mad = np.median([abs(p - median) for p in historical_prices])
        
        # If MAD is 0, fallback to 5% of median as the threshold
        threshold = max(mad * 3, median * 0.05)
        
        diff = current_price - median
        variance_percent = diff / median
        
        is_anomalous = abs(diff) > threshold
        
        # Calculate a normalized score 0-100 based on how far past the threshold it is
        score = 0.0
        if is_anomalous:
            score = min(100.0, 50 + (abs(diff) / threshold) * 10)
            
        return {
            "is_anomalous": is_anomalous,
            "variance_percent": round(variance_percent * 100, 2),
            "expected_price": round(median, 2),
            "baseline_type": "HISTORICAL_MEDIAN",
            "score": round(score, 2)
        }
