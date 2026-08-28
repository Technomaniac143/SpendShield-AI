from typing import Protocol


class EntityResolver(Protocol):
    def resolve_supplier(self, tenant_id: str, value: str): ...
    def resolve_product(self, tenant_id: str, value: str): ...


def normalize(value: str) -> str:
    return " ".join(value.strip().casefold().split())


class DeterministicEntityResolver:
    def __init__(self, db):
        self.db = db

    def resolve_supplier(self, tenant_id: str, value: str):
        from sqlalchemy import select
        from app.models import Supplier

        return self.db.scalar(select(Supplier).where(
            Supplier.tenant_id == tenant_id,
            Supplier.normalized_name == normalize(value),
        ))

    def resolve_product(self, tenant_id: str, value: str):
        from sqlalchemy import select
        from app.models import Product

        return self.db.scalar(select(Product).where(
            Product.tenant_id == tenant_id,
            Product.sku == value.strip(),
        )) or self.db.scalar(select(Product).where(
            Product.tenant_id == tenant_id,
            Product.normalized_name == normalize(value),
        ))