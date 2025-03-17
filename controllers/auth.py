from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from models.schemas import Token, UserCreate, PasswordChange
from services.auth import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def initialize(auth_service):
    """Initialize controller with required services"""
    
    @router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
    async def register_user(user: UserCreate):
        success, message = auth_service.register(user.username, user.password, user.email)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
        return {"message": message}

    @router.post("/token", response_model=Token)
    async def login(form_data: OAuth2PasswordRequestForm = Depends()):
        if not auth_service.verify_password(form_data.username, form_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        auth_service.update_login(form_data.username)
        
        access_token = auth_service.create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}

    @router.post("/users/change-password", response_model=dict)
    async def change_password(password_data: PasswordChange):
        success, message = auth_service.change_password(
            password_data.username,
            password_data.current_password,
            password_data.new_password
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
        return {"message": message}
    
    # Add dependency for getting the current authenticated user
    async def get_current_user(token: str = Depends(oauth2_scheme)):
        return auth_service.get_current_user(token)
    
    return router, get_current_user