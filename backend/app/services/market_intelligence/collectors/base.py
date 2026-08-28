from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseCollector(ABC):
    @abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for products/suppliers on the source.
        Returns a list of dicts:
        {
            "source": str,
            "supplier_name": str,
            "product_name": str,
            "sku": str | None,
            "manufacturer": str | None,
            "price": float,
            "currency": str,
            "unit": str,
            "pack_quantity": int,
            "availability": str,
            "product_url": str | None,
            "collected_at": str (ISO format UTC)
        }
        """
        pass
