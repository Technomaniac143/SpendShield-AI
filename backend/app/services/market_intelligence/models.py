from datetime import datetime
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

def identifier() -> str:
    return str(uuid4())

class MarketSupplier(Base):
    __tablename__ = "market_suppliers"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    name: Mapped[str] = mapped_column(String(256))
    normalized_name: Mapped[str] = mapped_column(String(256), index=True, unique=True)
    website: Mapped[str | None] = mapped_column(String(256), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    location: Mapped[str | None] = mapped_column(String(256), nullable=True)
    supplier_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source: Mapped[str] = mapped_column(String(64))
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class MarketProduct(Base):
    __tablename__ = "market_products"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    name: Mapped[str] = mapped_column(String(256))
    normalized_name: Mapped[str] = mapped_column(String(256), index=True, unique=True)
    manufacturer: Mapped[str | None] = mapped_column(String(256), nullable=True)
    model: Mapped[str | None] = mapped_column(String(256), nullable=True)
    sku: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class MarketPriceObservation(Base):
    __tablename__ = "market_price_observations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("market_suppliers.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("market_products.id", ondelete="CASCADE"), index=True)
    
    price: Mapped[float] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3))
    unit: Mapped[str] = mapped_column(String(32), default="piece")
    pack_quantity: Mapped[int] = mapped_column(Integer, default=1)
    normalized_unit_price: Mapped[float] = mapped_column(Numeric(18, 6))
    normalized_unit: Mapped[str] = mapped_column(String(32), default="piece")
    
    availability: Mapped[str] = mapped_column(String(32), default="IN_STOCK")
    source: Mapped[str] = mapped_column(String(64))
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    
    tax_included: Mapped[bool] = mapped_column(Boolean, default=False)
    shipping_included: Mapped[bool] = mapped_column(Boolean, default=False)
    
    raw_product_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    raw_supplier_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    freshness: Mapped[str | None] = mapped_column(String(32), nullable=True)
    
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class MarketCollectionJob(Base):
    __tablename__ = "market_collection_jobs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    source: Mapped[str] = mapped_column(String(64))
    query: Mapped[str] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(32), default="PENDING")
    records_found: Mapped[int] = mapped_column(Integer, default=0)
    records_inserted: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
