import uuid
from datetime import datetime
from app.models.tenant import Tenant
from app.models.user import User
from app.core.security import get_password_hash

# Mock seed script for demo purposes.
# In a real execution, this would connect to the DB and insert records.

def generate_demo_data():
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    print("Seeding Tenant...")
    print(f"Tenant ID: {tenant_id}")
    
    print("Seeding Admin User...")
    print(f"Admin Email: admin@demo.com (password: admin)")
    
    print("Seeding Supplier: ABC Industries...")
    supplier_id = uuid.uuid4()
    print(f"Risk Score: 87")
    
    print("Seeding PO-1001...")
    print("1,000 units @ 500 INR")
    
    print("Seeding GRN...")
    print("920 units received")
    
    print("Seeding Invoice...")
    print("1,000 units @ 500 INR")
    
    print("Demo data structure ready to be injected into the database.")

if __name__ == "__main__":
    generate_demo_data()
