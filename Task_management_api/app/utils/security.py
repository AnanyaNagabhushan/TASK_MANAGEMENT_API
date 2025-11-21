from passlib.hash import scrypt

def hash_password(password):
    return scrypt.hash(password)

def verify_password(password, hashed):
    return scrypt.verify(password, hashed)
