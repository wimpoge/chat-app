from typing import List, Dict, Tuple

class FriendService:
    def __init__(self, user_db):
        self.user_db = user_db
    
    def add_friend(self, username, friend_username) -> Tuple[bool, str]:
        # Validate usernames
        if username == friend_username:
            return False, "Cannot add yourself as a friend"
        
        if not self.user_db.get_user(friend_username):
            return False, "User not found"
        
        # Get current friends list
        user = self.user_db.get_user(username)
        if not user:
            return False, "User not found"
        
        friends = user.get("friends", [])
        
        # Check if already friends
        if friend_username in friends:
            return False, "Already friends with this user"
        
        # Add friend
        friends.append(friend_username)
        self.user_db.update_user(username, {"friends": friends})
        
        return True, f"Added {friend_username} as a friend"
    
    def get_friends(self, username) -> List[Dict]:
        user = self.user_db.get_user(username)
        if not user:
            return []
        
        friends = user.get("friends", [])
        friend_details = []
        
        for friend_username in friends:
            friend = self.user_db.get_user(friend_username)
            if friend:
                friend_details.append({
                    "username": friend_username,
                    "email": friend.get("email", ""),
                    "profile_image": friend.get("profile_image")
                })
        
        return friend_details
    
    def get_non_friends(self, username) -> List[Dict]:
        user = self.user_db.get_user(username)
        if not user:
            return []
        
        friends = user.get("friends", [])
        all_users = self.user_db.get_all_users(exclude_username=username)
        
        return [user for user in all_users if user["username"] not in friends]