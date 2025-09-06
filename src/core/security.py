from passlib.context import CryptContext

# specify the hashing algorithm as bcrypt
# the deprecated option is set to automatically use the latest algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Compare the plain password with the hashed password
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # Generate a hash from the plain password
    return pwd_context.hash(password)

def verify_refresh_token(plain_token: str, hashed_token: str) -> bool:
    # Compare the plain token with the hashed token
    return pwd_context.verify(plain_token, hashed_token)

def get_refresh_token_hash(token: str) -> str:
    # Generate a hash from the plain token
    return pwd_context.hash(token)