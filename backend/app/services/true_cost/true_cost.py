from typing import Dict, Any

class TrueCostEngine:
    
    @staticmethod
    def calculate_true_cost(
        quoted_price: float,
        logistics_cost: float = 0.0,
        quality_cost: float = 0.0,
        delay_cost: float = 0.0,
        inventory_carrying_cost: float = 0.0,
        dispute_cost: float = 0.0,
        expected_failure_cost: float = 0.0,
        discounts: float = 0.0,
        rebates: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates the actual expected procurement cost.
        """
        true_cost = (
            quoted_price
            + logistics_cost
            + quality_cost
            + delay_cost
            + inventory_carrying_cost
            + dispute_cost
            + expected_failure_cost
            - discounts
            - rebates
        )
        
        return {
            "quoted_price": quoted_price,
            "logistics_cost": logistics_cost,
            "quality_cost": quality_cost,
            "delay_cost": delay_cost,
            "inventory_carrying_cost": inventory_carrying_cost,
            "dispute_cost": dispute_cost,
            "expected_failure_cost": expected_failure_cost,
            "discounts": discounts,
            "rebates": rebates,
            "true_cost": round(true_cost, 2)
        }
