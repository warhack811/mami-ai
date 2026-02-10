from app.core.security import verify_password, get_password_hash

def test_verify_password():
    password = "testpassword"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)

def test_get_password_hash():
    password = "testpassword"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert verify_password(password, hashed_password)

def test_password_hashing_special_characters():
    password = "!@#$%^&*()"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)

def test_empty_password():
    password = ""
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)
    assert not verify_password(" ", hashed_password)
