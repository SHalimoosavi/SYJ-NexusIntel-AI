from fastapi import Depends, HTTPException

from app.core.dependencies import get_current_user


def require_roles(allowed_roles: list[str]):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.get("role_name") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user

    return role_checker
