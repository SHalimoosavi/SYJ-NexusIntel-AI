from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.models.organization import Organization
from app.services.organization_service import get_organization, get_organizations


def test_organization_queries_are_scoped_to_tenant():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        first = Organization(name="Tenant One", slug="tenant-one")
        second = Organization(name="Tenant Two", slug="tenant-two")
        session.add_all([first, second])
        session.commit()
        session.refresh(first)
        session.refresh(second)

        assert [item.id for item in get_organizations(session, first.id)] == [first.id]
        assert get_organization(session, second.id, first.id) is None
        assert get_organization(session, first.id, first.id).id == first.id
        assert len(get_organizations(session)) == 2
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
