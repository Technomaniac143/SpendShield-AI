from typing import Dict, Any

class FinancialExposureEngine:
    
    @staticmethod
    def calculate_exposure(
        quantity_variance: float = 0.0,
        price_variance: float = 0.0,
        unit_price: float = 0.0,
        quantity: float = 0.0,
        duplicate_amount: float = 0.0,
        inventory_quantity: float = 0.0,
        inventory_value: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates financial exposure across various dimensions.
        """
        gross_exposure = 0.0
        details = {}
        
        if quantity_variance > 0:
            qty_exposure = quantity_variance * unit_price
            gross_exposure += qty_exposure
            details["quantity_exposure"] = qty_exposure
            
        if price_variance > 0:
            prc_exposure = price_variance * quantity
            gross_exposure += prc_exposure
            details["price_exposure"] = prc_exposure
            
        if duplicate_amount > 0:
            gross_exposure += duplicate_amount
            details["duplicate_exposure"] = duplicate_amount
            
        if inventory_quantity > 0 and inventory_value > 0:
            inv_exposure = inventory_quantity * inventory_value
            gross_exposure += inv_exposure
            details["inventory_exposure"] = inv_exposure
            
        return {
            "gross_exposure": round(gross_exposure, 2),
            "recoverable_exposure": round(gross_exposure, 2), # Simplified for MVP
            "details": details
        }
