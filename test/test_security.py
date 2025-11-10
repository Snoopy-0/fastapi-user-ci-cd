from app.security import hash_password, verify_password

def test_hash_and_verify_password():
    plain_pw = "mysecretpassword"
    hashed = hash_password(plain_pw)

    assert hashed != plain_pw
    assert verify_password(plain_pw, hashed)
    assert not verify_password("wrongpassword", hashed)
