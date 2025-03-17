import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import configuration
from config import UPLOAD_DIR, USER_DB_FILE, MESSAGE_DB_FILE, GROUP_DB_FILE, GROUP_MESSAGE_DB_FILE

# Import models
from models.database import UserDB, MessageDB, GroupDB, GroupMessageDB

# Import services
from services.auth import AuthService
from services.friend import FriendService
from services.message import MessageService
from services.group import GroupService

# Import controllers
import controllers.auth as auth_controller
import controllers.users as users_controller
import controllers.friends as friends_controller
import controllers.messages as messages_controller
import controllers.groups as groups_controller

# Initialize app
app = FastAPI(title="User API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Initialize databases
user_db = UserDB(USER_DB_FILE)
message_db = MessageDB(MESSAGE_DB_FILE)
group_db = GroupDB(GROUP_DB_FILE)
group_message_db = GroupMessageDB(GROUP_MESSAGE_DB_FILE)

# Initialize services
auth_service = AuthService(user_db)
friend_service = FriendService(user_db)
message_service = MessageService(message_db, user_db)
group_service = GroupService(group_db, user_db, group_message_db)

# Initialize controllers
auth_router, get_current_user = auth_controller.initialize(auth_service)
users_router = users_controller.initialize(user_db, get_current_user)
friends_router = friends_controller.initialize(friend_service, get_current_user)
messages_router = messages_controller.initialize(message_service, get_current_user)
groups_router = groups_controller.initialize(group_service, get_current_user)

# Register routers
app.include_router(auth_router, tags=["Authentication"], prefix="")
app.include_router(users_router, tags=["Users"], prefix="/users")
app.include_router(friends_router, tags=["Friends"], prefix="/friends")
app.include_router(messages_router, tags=["Messages"], prefix="/messages")
app.include_router(groups_router, tags=["Groups"], prefix="/groups")

@app.get("/")
async def root():
    return {"message": "Welcome to the User API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)