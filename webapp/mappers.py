def delete_token_by_name(name):
    """Delete a token"""
    token = find_token_by_name(name)

    if not token:
        return None

    db_session.delete(token)
    db_session.commit()

    return True
