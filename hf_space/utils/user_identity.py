import hashlib


def numeric_user_id(user_id):
    normalized_user_id = str(user_id).strip()
    if not normalized_user_id:
        return 1

    candidate = normalized_user_id
    if candidate.startswith("user_"):
        candidate = candidate[len("user_"):]

    if candidate.isdecimal():
        return int(candidate)

    digest = hashlib.sha256(candidate.casefold().encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") & ((1 << 63) - 1) or 1
