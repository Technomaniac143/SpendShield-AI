"""create tenant-scoped procurement foundation"""
from alembic import op
import sqlalchemy as sa

revision = "0005_procurement_foundation"
down_revision = "0004_evidence_write_permission"
branch_labels = None
depends_on = None

MONEY = sa.Numeric(18, 2)
QUANTITY = sa.Numeric(18, 6)


def upgrade():
    op.create_table(
        "product_categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("normalized_name", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_product_categories_tenant_name"),
    )
    op.create_table(
        "suppliers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("normalized_name", sa.String(256), nullable=False),
        sa.Column("tax_id", sa.String(128)), sa.Column("registration_id", sa.String(128)),
        sa.Column("address", sa.Text), sa.Column("country", sa.String(2)),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_suppliers_tenant_name"),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku", sa.String(128), nullable=False), sa.Column("name", sa.String(256), nullable=False),
        sa.Column("normalized_name", sa.String(256), nullable=False),
        sa.Column("category_id", sa.String(36), sa.ForeignKey("product_categories.id", ondelete="SET NULL")),
        sa.Column("unit_of_measure", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "sku", name="uq_products_tenant_sku"),
    )
    op.create_table(
        "supplier_metrics",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("supplier_id", sa.String(36), sa.ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False),
        *[sa.Column(name, sa.Numeric(7, 2), nullable=False) for name in (
            "on_time_delivery_rate", "late_delivery_rate", "defect_rate", "return_rate", "dispute_rate",
            "price_variance", "invoice_anomaly_rate")],
        sa.Column("supplier_risk_score", sa.Numeric(5, 2)), sa.Column("risk_confidence", sa.Numeric(5, 2)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "contracts",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contract_number", sa.String(128), nullable=False), sa.Column("supplier_id", sa.String(36), sa.ForeignKey("suppliers.id"), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False), sa.Column("start_date", sa.Date, nullable=False), sa.Column("end_date", sa.Date), sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "contract_number", name="uq_contracts_tenant_number"),
    )
    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("po_number", sa.String(128), nullable=False), sa.Column("supplier_id", sa.String(36), sa.ForeignKey("suppliers.id"), nullable=False), sa.Column("order_date", sa.Date, nullable=False), sa.Column("currency", sa.String(3), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("total_amount", MONEY, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "po_number", name="uq_purchase_orders_tenant_number"), sa.CheckConstraint("total_amount >= 0", name="ck_purchase_orders_total_nonnegative"),
    )
    op.create_table(
        "purchase_order_items",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("purchase_order_id", sa.String(36), sa.ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False), sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False), sa.Column("description", sa.String(512), nullable=False), sa.Column("quantity", QUANTITY, nullable=False), sa.Column("unit_price", MONEY, nullable=False), sa.Column("tax", MONEY, nullable=False), sa.Column("discount", MONEY, nullable=False), sa.Column("line_total", MONEY, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("quantity >= 0 AND unit_price >= 0 AND tax >= 0 AND discount >= 0 AND line_total >= 0", name="ck_po_items_nonnegative"),
    )
    op.create_table(
        "goods_receipts",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("grn_number", sa.String(128), nullable=False), sa.Column("po_id", sa.String(36), sa.ForeignKey("purchase_orders.id"), nullable=False), sa.Column("supplier_id", sa.String(36), sa.ForeignKey("suppliers.id"), nullable=False), sa.Column("receipt_date", sa.Date, nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.UniqueConstraint("tenant_id", "grn_number", name="uq_goods_receipts_tenant_number"),
    )
    op.create_table(
        "goods_receipt_items",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("goods_receipt_id", sa.String(36), sa.ForeignKey("goods_receipts.id", ondelete="CASCADE"), nullable=False), sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False), sa.Column("quantity_received", QUANTITY, nullable=False), sa.Column("accepted_quantity", QUANTITY, nullable=False), sa.Column("rejected_quantity", QUANTITY, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.CheckConstraint("quantity_received >= 0 AND accepted_quantity >= 0 AND rejected_quantity >= 0", name="ck_grn_items_nonnegative"),
    )
    op.create_table(
        "invoices",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("invoice_number", sa.String(128), nullable=False), sa.Column("supplier_id", sa.String(36), sa.ForeignKey("suppliers.id"), nullable=False), sa.Column("po_id", sa.String(36), sa.ForeignKey("purchase_orders.id")), sa.Column("invoice_date", sa.Date, nullable=False), sa.Column("currency", sa.String(3), nullable=False), sa.Column("subtotal", MONEY, nullable=False), sa.Column("tax", MONEY, nullable=False), sa.Column("discount", MONEY, nullable=False), sa.Column("total_amount", MONEY, nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("document_id", sa.String(128)), sa.Column("document_hash", sa.String(64)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.UniqueConstraint("tenant_id", "invoice_number", "supplier_id", name="uq_invoices_tenant_number_supplier"), sa.CheckConstraint("subtotal >= 0 AND tax >= 0 AND discount >= 0 AND total_amount >= 0", name="ck_invoices_nonnegative"),
    )
    op.create_table(
        "invoice_items",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("invoice_id", sa.String(36), sa.ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False), sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id")), sa.Column("description", sa.String(512), nullable=False), sa.Column("quantity", QUANTITY, nullable=False), sa.Column("unit_price", MONEY, nullable=False), sa.Column("tax", MONEY, nullable=False), sa.Column("discount", MONEY, nullable=False), sa.Column("line_total", MONEY, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.CheckConstraint("quantity >= 0 AND unit_price >= 0 AND tax >= 0 AND discount >= 0 AND line_total >= 0", name="ck_invoice_items_nonnegative"),
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("invoice_id", sa.String(36), sa.ForeignKey("invoices.id"), nullable=False), sa.Column("amount", MONEY, nullable=False), sa.Column("currency", sa.String(3), nullable=False), sa.Column("payment_date", sa.Date), sa.Column("status", sa.String(32), nullable=False), sa.Column("payment_reference", sa.String(128), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.UniqueConstraint("tenant_id", "payment_reference", name="uq_payments_tenant_reference"), sa.CheckConstraint("amount >= 0", name="ck_payments_amount_nonnegative"),
    )
    op.create_table(
        "inventory",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("warehouse", sa.String(128), nullable=False), sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False), sa.Column("quantity", QUANTITY, nullable=False), sa.Column("unit_cost", MONEY, nullable=False), sa.Column("inventory_value", MONEY, nullable=False), sa.Column("last_movement", sa.Date), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.UniqueConstraint("tenant_id", "warehouse", "product_id", name="uq_inventory_tenant_warehouse_product"), sa.CheckConstraint("quantity >= 0 AND unit_cost >= 0 AND inventory_value >= 0", name="ck_inventory_nonnegative"),
    )
    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("inventory_id", sa.String(36), sa.ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False), sa.Column("quantity", QUANTITY, nullable=False), sa.Column("movement_type", sa.String(32), nullable=False), sa.Column("movement_date", sa.Date, nullable=False), sa.Column("reference", sa.String(128)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.CheckConstraint("quantity >= 0", name="ck_inventory_movements_quantity_nonnegative"),
    )
    op.create_table(
        "quality_events",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("supplier_id", sa.String(36), sa.ForeignKey("suppliers.id"), nullable=False), sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id")), sa.Column("event_date", sa.Date, nullable=False), sa.Column("severity", sa.String(32), nullable=False), sa.Column("description", sa.Text, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "delivery_events",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("supplier_id", sa.String(36), sa.ForeignKey("suppliers.id"), nullable=False), sa.Column("purchase_order_id", sa.String(36), sa.ForeignKey("purchase_orders.id")), sa.Column("expected_date", sa.Date, nullable=False), sa.Column("actual_date", sa.Date), sa.Column("status", sa.String(32), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "disputes",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("supplier_id", sa.String(36), sa.ForeignKey("suppliers.id"), nullable=False), sa.Column("invoice_id", sa.String(36), sa.ForeignKey("invoices.id")), sa.Column("amount", MONEY, nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("reason", sa.Text, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.CheckConstraint("amount >= 0", name="ck_disputes_amount_nonnegative"),
    )

    for table, columns in {
        "product_categories": ["tenant_id", "normalized_name"], "suppliers": ["tenant_id", "normalized_name", "status"], "products": ["tenant_id", "normalized_name", "category_id"], "supplier_metrics": ["tenant_id", "supplier_id"], "contracts": ["tenant_id", "supplier_id", "status"], "purchase_orders": ["tenant_id", "supplier_id", "order_date", "status"], "purchase_order_items": ["tenant_id", "purchase_order_id", "product_id"], "goods_receipts": ["tenant_id", "po_id", "supplier_id", "status"], "goods_receipt_items": ["tenant_id", "goods_receipt_id", "product_id"], "invoices": ["tenant_id", "supplier_id", "po_id", "invoice_date", "status", "document_hash"], "invoice_items": ["tenant_id", "invoice_id", "product_id"], "payments": ["tenant_id", "invoice_id", "status"], "inventory": ["tenant_id", "warehouse", "product_id"], "inventory_movements": ["tenant_id", "inventory_id", "movement_date"], "quality_events": ["tenant_id", "supplier_id", "event_date"], "delivery_events": ["tenant_id", "supplier_id", "expected_date"], "disputes": ["tenant_id", "supplier_id", "status"],
    }.items():
        for column in columns:
            op.create_index(f"ix_{table}_{column}", table, [column])


def downgrade():
    tables = ["disputes", "delivery_events", "quality_events", "inventory_movements", "inventory", "payments", "invoice_items", "invoices", "goods_receipt_items", "goods_receipts", "purchase_order_items", "purchase_orders", "contracts", "supplier_metrics", "products", "suppliers", "product_categories"]
    for table in tables:
        for index in sa.inspect(op.get_bind()).get_indexes(table):
            if index["name"].startswith(f"ix_{table}_"):
                op.drop_index(index["name"], table_name=table)
        op.drop_table(table)