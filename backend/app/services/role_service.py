from sqlalchemy.orm import Session

from app.models.role import Role


DEFAULT_ROLES = [
    {
        "name": "SUPER_ADMIN",
        "description": "Platform administrator",
    },
    {
        "name": "ORGANIZATION_OWNER",
        "description": "Organization owner",
    },
    {
        "name": "MANAGER",
        "description": "Manager",
    },
    {
        "name": "SALES_REPRESENTATIVE",
        "description": "Sales representative",
    },
    {
        "name": "VIEWER",
        "description": "Read-only access",
    },
]


def seed_roles(
    db: Session,
):
    for role_data in DEFAULT_ROLES:

        existing = (
            db.query(Role)
            .filter(
                Role.name
                == role_data["name"]
            )
            .first()
        )

        if existing:
            continue

        role = Role(
            name=role_data["name"],
            description=role_data["description"],
        )

        db.add(role)

    db.commit()


def get_role_by_name(
    db: Session,
    role_name: str,
):
    return (
        db.query(Role)
        .filter(
            Role.name == role_name
        )
        .first()
    )


def get_roles(
    db: Session,
):
    return (
        db.query(Role)
        .order_by(
            Role.id.asc()
        )
        .all()
    )
