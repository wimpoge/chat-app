import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class UserDB:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def _load(self):
        """Load users from file every time it's needed"""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save(self, users):
        """Save users to file"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.file_path) or '.', exist_ok=True)
        
        with open(self.file_path, 'w') as f:
            json.dump(users, f, indent=4)
    
    def get_user(self, username):
        """Get a user from the database"""
        users = self._load()
        return users.get(username)
    
    def add_user(self, username, user_data):
        """Add a new user to the database"""
        users = self._load()
        users[username] = user_data
        self._save(users)
    
    def update_user(self, username, update_data):
        """Update an existing user"""
        users = self._load()
        if username in users:
            users[username].update(update_data)
            self._save(users)
            return True
        return False
    
    def get_all_users(self, exclude_username=None):
        """Get all users excluding the specified username"""
        users = self._load()
        users_list = []
        for username, user_data in users.items():
            if exclude_username and username == exclude_username:
                continue
            users_list.append({
                "username": username,
                "email": user_data.get("email", ""),
                "profile_image": user_data.get("profile_image")
            })
        return users_list

class MessageDB:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def _load(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save(self, messages):
        with open(self.file_path, 'w') as f:
            json.dump(messages, f, indent=4)
    
    def add_message(self, sender, recipient, content):
        messages = self._load()
        message = {
            "sender": sender,
            "recipient": recipient,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        messages.append(message)
        self._save(messages)
        return message
    
    def get_messages(self, username1, username2):
        messages = self._load()
        return [
            msg for msg in messages 
            if (msg["sender"] == username1 and msg["recipient"] == username2) or
               (msg["sender"] == username2 and msg["recipient"] == username1)
        ]
        
class GroupDB:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def _load(self):
        """Load groups from file"""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save(self, groups):
        """Save groups to file"""
        os.makedirs(os.path.dirname(self.file_path) or '.', exist_ok=True)
        
        with open(self.file_path, 'w') as f:
            json.dump(groups, f, indent=4)
    
    def create_group(self, title, creator, members):
        """Create a new group"""
        groups = self._load()
        
        group_id = str(uuid.uuid4())
        group = {
            "id": group_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "creator": creator,
            "members": list(set(members + [creator]))  # Ensure creator is in members and remove duplicates
        }
        
        groups[group_id] = group
        self._save(groups)
        return group
    
    def get_group(self, group_id):
        """Get a group by ID"""
        groups = self._load()
        return groups.get(group_id)
    
    def update_group(self, group_id, update_data):
        """Update an existing group"""
        groups = self._load()
        if group_id in groups:
            groups[group_id].update(update_data)
            self._save(groups)
            return True
        return False
    
    def delete_group(self, group_id):
        """Delete a group"""
        groups = self._load()
        if group_id in groups:
            del groups[group_id]
            self._save(groups)
            return True
        return False
    
    def get_user_groups(self, username):
        """Get all groups a user is a member of"""
        groups = self._load()
        return [group for group_id, group in groups.items() if username in group["members"]]
    
    def add_member(self, group_id, username):
        """Add a member to a group"""
        group = self.get_group(group_id)
        if not group:
            return False
        
        if username not in group["members"]:
            group["members"].append(username)
            self.update_group(group_id, {"members": group["members"]})
        return True
    
    def remove_member(self, group_id, username):
        """Remove a member from a group"""
        group = self.get_group(group_id)
        if not group:
            return False
        
        if username in group["members"]:
            group["members"].remove(username)
            self.update_group(group_id, {"members": group["members"]})
        return True

class GroupMessageDB:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def _load(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save(self, messages):
        os.makedirs(os.path.dirname(self.file_path) or '.', exist_ok=True)
        
        with open(self.file_path, 'w') as f:
            json.dump(messages, f, indent=4)
    
    def add_message(self, group_id, sender, content):
        messages = self._load()
        message_id = str(uuid.uuid4())
        message = {
            "id": message_id,
            "group_id": group_id,
            "sender": sender,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        messages.append(message)
        self._save(messages)
        return message
    
    def get_group_messages(self, group_id):
        messages = self._load()
        return [msg for msg in messages if msg["group_id"] == group_id]