import argparse

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import Tenant, User
from app.services.auth import create_user
from app.schemas import UserCreateRequest


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a SpendShield administrator")
    parser.add_argument("--tenant-name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.name == args.tenant_name))
        if tenant is None:
            tenant = Tenant(name=args.tenant_name)
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        existing = db.scalar(select(User).where(User.tenant_id == tenant.id, User.email == args.email.lower()))
        if existing is None:
            create_user(db, tenant.id, UserCreateRequest(
                email=args.email, display_name=args.email, password=args.password, roles=["ADMIN"],
            ))
        print(f"tenant_id={tenant.id}")


if __name__ == "__main__":
    main()