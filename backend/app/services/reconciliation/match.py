from typing import List, Dict, Any
from app.models.invoice import Invoice, InvoiceItem
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.goods_receipt import GoodsReceipt, GoodsReceiptItem

class ReconciliationEngine:
    """
    Handles PO-GRN-Invoice 3-way matching.
    """
    
    @staticmethod
    def match_three_way(invoice: Invoice, po: PurchaseOrder, grns: List[GoodsReceipt]) -> Dict[str, Any]:
        """
        Deterministic reconciliation between an Invoice, its PO, and associated GRNs.
        """
        reasons = []
        financial_exposure = 0.0
        status = "PASS"
        
        # Aggregate received quantities
        received_quantities = {}
        for grn in grns:
            for item in grn.items:
                product_id = item.product_id
                received_quantities[product_id] = received_quantities.get(product_id, 0.0) + item.accepted_quantity
                
        # Match invoice items against PO and GRN
        for inv_item in invoice.items:
            # Check quantity variance
            product_id = inv_item.product_id
            received_qty = received_quantities.get(product_id, 0.0)
            
            if inv_item.quantity > received_qty:
                qty_variance = inv_item.quantity - received_qty
                exposure = qty_variance * inv_item.unit_price
                financial_exposure += exposure
                status = "FAIL"
                reasons.append(f"Invoice quantity ({inv_item.quantity}) exceeds received quantity ({received_qty}) for product {product_id}.")
                
            # Find PO item for price variance
            po_item = next((pi for pi in po.items if pi.product_id == product_id), None)
            if po_item:
                if inv_item.unit_price > po_item.unit_price:
                    status = "FAIL"
                    exposure = (inv_item.unit_price - po_item.unit_price) * inv_item.quantity
                    financial_exposure += exposure
                    reasons.append(f"Invoice unit price ({inv_item.unit_price}) exceeds PO unit price ({po_item.unit_price}) for product {product_id}.")
            else:
                status = "FAIL"
                reasons.append(f"Product {product_id} on invoice not found in PO.")

        return {
            "status": status,
            "financial_exposure": financial_exposure,
            "reasons": reasons
        }
