def can_export(user_roles: set[str], required_roles: set[str]) -> bool:
    return all(role in user_roles for role in required_roles)
