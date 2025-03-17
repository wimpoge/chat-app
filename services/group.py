from typing import List, Dict, Optional, Tuple

class GroupService:
    def __init__(self, group_db, user_db, group_message_db):
        self.group_db = group_db
        self.user_db = user_db
        self.group_message_db = group_message_db
    
    def create_group(self, title: str, creator: str, members: List[str]) -> Optional[Dict]:
        """Create a new group with the given title and members"""
        # Validate that all members exist
        valid_members = []
        for username in members:
            if self.user_db.get_user(username):
                valid_members.append(username)
        
        # Create the group
        return self.group_db.create_group(title, creator, valid_members)
    
    def get_group(self, group_id: str) -> Optional[Dict]:
        """Get a group by ID"""
        return self.group_db.get_group(group_id)
    
    def get_group_with_member_details(self, group_id: str) -> Optional[Dict]:
        """Get a group with full member details"""
        group = self.group_db.get_group(group_id)
        if not group:
            return None
        
        members_details = []
        for username in group["members"]:
            user = self.user_db.get_user(username)
            if user:
                members_details.append({
                    "username": username,
                    "email": user.get("email", ""),
                    "profile_image": user.get("profile_image")
                })
        
        group_with_details = group.copy()
        group_with_details["members_details"] = members_details
        return group_with_details
    
    def get_user_groups(self, username: str) -> List[Dict]:
        """Get all groups a user is a member of"""
        return self.group_db.get_user_groups(username)
    
    def add_member(self, group_id: str, username: str) -> bool:
        """Add a member to a group"""
        # Check if user exists
        if not self.user_db.get_user(username):
            return False
        
        return self.group_db.add_member(group_id, username)
    
    def remove_member(self, group_id: str, username: str) -> bool:
        """Remove a member from a group"""
        return self.group_db.remove_member(group_id, username)
    
    def delete_group(self, group_id: str, username: str) -> Tuple[bool, str]:
        """Delete a group if the user is the creator"""
        group = self.group_db.get_group(group_id)
        if not group:
            return False, "Group not found"
        
        if group["creator"] != username:
            return False, "Only the group creator can delete the group"
        
        self.group_db.delete_group(group_id)
        return True, "Group deleted successfully"
    
    def send_message(self, group_id: str, sender: str, content: str) -> Optional[Dict]:
        """Send a message to a group"""
        # Check if group exists and user is a member
        group = self.group_db.get_group(group_id)
        if not group or sender not in group["members"]:
            return None
        
        return self.group_message_db.add_message(group_id, sender, content)
    
    def get_group_messages(self, group_id: str, username: str) -> Optional[List[Dict]]:
        """Get all messages in a group if the user is a member"""
        group = self.group_db.get_group(group_id)
        if not group or username not in group["members"]:
            return None
        
        return self.group_message_db.get_group_messages(group_id)