from sqlalchemy.orm import Session

from app.models.feature_flag import (
    FeatureFlag,
)


DEFAULT_FEATURES = {
    "AI_COPILOT": False,
    "WHATSAPP_AUTOMATION": False,
    "EMAIL_OUTREACH": False,
    "EXECUTIVE_INTELLIGENCE": True,
    "ADVANCED_REPORTING": False,
    "MULTI_AGENT": False,
}


def seed_default_features(
    db: Session,
    organization_id: int,
):
    for feature_name, enabled in (
        DEFAULT_FEATURES.items()
    ):
        existing = (
            db.query(FeatureFlag)
            .filter(
                FeatureFlag.organization_id
                == organization_id,
                FeatureFlag.feature_name
                == feature_name,
            )
            .first()
        )

        if existing:
            continue

        feature = FeatureFlag(
            organization_id=
            organization_id,

            feature_name=
            feature_name,

            is_enabled=
            enabled,
        )

        db.add(feature)

    db.commit()


def feature_enabled(
    db: Session,
    organization_id: int,
    feature_name: str,
):
    feature = (
        db.query(FeatureFlag)
        .filter(
            FeatureFlag.organization_id
            == organization_id,

            FeatureFlag.feature_name
            == feature_name,
        )
        .first()
    )

    if not feature:
        return False

    return feature.is_enabled


def enable_feature(
    db: Session,
    organization_id: int,
    feature_name: str,
):
    feature = (
        db.query(FeatureFlag)
        .filter(
            FeatureFlag.organization_id
            == organization_id,

            FeatureFlag.feature_name
            == feature_name,
        )
        .first()
    )

    if not feature:
        return None

    feature.is_enabled = True

    db.commit()

    db.refresh(feature)

    return feature


def disable_feature(
    db: Session,
    organization_id: int,
    feature_name: str,
):
    feature = (
        db.query(FeatureFlag)
        .filter(
            FeatureFlag.organization_id
            == organization_id,

            FeatureFlag.feature_name
            == feature_name,
        )
        .first()
    )

    if not feature:
        return None

    feature.is_enabled = False

    db.commit()

    db.refresh(feature)

    return feature


def get_features(
    db: Session,
    organization_id: int,
):
    return (
        db.query(FeatureFlag)
        .filter(
            FeatureFlag.organization_id
            == organization_id
        )
        .all()
    )
