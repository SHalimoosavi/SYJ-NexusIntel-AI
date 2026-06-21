from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import (
    get_db,
)

from app.core.dependencies import (
    get_current_user,
)

from app.services.feature_flag_service import (
    feature_enabled,
)


def require_feature(
    feature_name: str,
):
    def feature_checker(
        current_user=Depends(
            get_current_user
        ),
        db: Session = Depends(
            get_db
        ),
    ):
        organization_id = current_user[
            "organization_id"
        ]

        enabled = feature_enabled(
            db,
            organization_id,
            feature_name,
        )

        if not enabled:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Feature disabled: "
                    f"{feature_name}"
                ),
            )

        return current_user

    return feature_checker
