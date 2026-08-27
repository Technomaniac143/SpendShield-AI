import json
from typing import Dict, Any, List
from app.agents.tools import AVAILABLE_TOOLS
from app.agents.prompts import SYSTEM_PROMPT, RECOMMENDATION_PROMPT
from app.core.config import settings

class AuditAgent:
    """
    Orchestrates the investigation by calling predefined tools and using an LLM to synthesize the results.
    """
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.execution_log: List[Dict[str, Any]] = []

    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        if tool_name not in AVAILABLE_TOOLS:
            return json.dumps({"error": f"Tool {tool_name} not found"})
        
        try:
            # Inject tenant_id automatically for security
            kwargs["tenant_id"] = self.tenant_id
            result = await AVAILABLE_TOOLS[tool_name](**kwargs)
            
            self.execution_log.append({
                "tool": tool_name,
                "input": kwargs,
                "output": json.loads(result),
                "status": "SUCCESS"
            })
            return result
        except Exception as e:
            err = {"error": str(e)}
            self.execution_log.append({
                "tool": tool_name,
                "input": kwargs,
                "output": err,
                "status": "FAIL"
            })
            return json.dumps(err)

    async def investigate_supplier(self, supplier_id: str, invoice_id: str = None) -> Dict[str, Any]:
        """
        Runs the standard orchestration loop.
        In a real LLM setup, this would be a ReAct loop.
        For the MVP hackathon, we explicitly execute the critical tools and then synthesize.
        """
        evidence = []
        
        # 1. Supplier Profile
        res = await self.execute_tool("get_supplier_profile", supplier_id=supplier_id)
        evidence.append(f"Supplier Profile: {res}")
        
        # 2. Graph Traversal
        res = await self.execute_tool("traverse_supplier_graph", supplier_id=supplier_id)
        evidence.append(f"Graph Intelligence: {res}")
        
        # 3. True Cost
        res = await self.execute_tool("calculate_true_cost", supplier_id=supplier_id)
        evidence.append(f"True Cost: {res}")
        
        if invoice_id:
            # 4. 3-Way Match
            res = await self.execute_tool("run_three_way_match", invoice_id=invoice_id)
            evidence.append(f"3-Way Match: {res}")
            
            # 5. Duplicate Detection
            res = await self.execute_tool("find_duplicate_invoices", invoice_id=invoice_id)
            evidence.append(f"Duplicates: {res}")
            
            # 6. Price Anomaly
            res = await self.execute_tool("detect_price_anomaly", invoice_id=invoice_id)
            evidence.append(f"Price Anomaly: {res}")
            
            # 7. Exposure
            res = await self.execute_tool("calculate_financial_exposure", investigation_id="INV-001")
            evidence.append(f"Exposure: {res}")

        # In a real implementation, we call the LLM here with `evidence` to get the final JSON
        # For the hackathon MVP without a guaranteed live LLM key, we mock the final synthesis.
        
        final_synthesis = {
            "finding": "Invoice quantity exceeds received quantity and price deviates by 11.6%.",
            "confidence": 0.93,
            "financial_exposure": 40000,
            "recommendation": "HOLD_PAYMENT"
        }
        
        return {
            "orchestration_log": self.execution_log,
            "synthesis": final_synthesis
        }
