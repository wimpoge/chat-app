import hashlib
import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status
from typing import Optional, Tuple, Dict

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

class AuthService:
    def __init__(self, user_db):
        self.user_db = user_db
    
    def hash_password(self, password, salt=None):
        if salt is None:
            salt = os.urandom(32)
        elif isinstance(salt, str):
            salt = bytes.fromhex(salt)
        
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        
        return {
            'hash': hash_obj.hex(),
            'salt': salt.hex()
        }
    
    def register(self, username, password, email) -> Tuple[bool, str]:
        if self.user_db.get_user(username):
            return False, "Username already exists"
        
        password_data = self.hash_password(password)
        
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_data['hash'],
            'salt': password_data['salt'],
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'profile_image': None,
            'friends': []
        }
        
        self.user_db.add_user(username, user_data)
        return True, "Registration successful"
    
    def verify_password(self, username, password) -> bool:
        user = self.user_db.get_user(username)
        if not user:
            return False
        
        salt = user['salt']
        password_data = self.hash_password(password, salt)
        
        return password_data['hash'] == user['password_hash']
    
    def change_password(self, username, current_password, new_password) -> Tuple[bool, str]:
        if not self.verify_password(username, current_password):
            return False, "Current password is incorrect"
        
        password_data = self.hash_password(new_password)
        
        update_data = {
            'password_hash': password_data['hash'],
            'salt': password_data['salt']
        }
        
        self.user_db.update_user(username, update_data)
        return True, "Password changed successfully"
    
    def update_login(self, username) -> None:
        self.user_db.update_user(username, {'last_login': datetime.now().isoformat()})

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def get_current_user(self, token: str) -> Dict:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = self.user_db.get_user(username)
        if user is None:
            raise credentials_exception
        return user