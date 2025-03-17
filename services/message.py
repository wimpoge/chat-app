from typing import List, Dict

class MessageService:
    def __init__(self, message_db, user_db):
        self.message_db = message_db
        self.user_db = user_db
    
    def send_message(self, sender, recipient, content) -> Dict:
        # Check if recipient exists
        if not self.user_db.get_user(recipient):
            return None
        
        # Send message
        return self.message_db.add_message(sender, recipient, content)
    
    def get_conversation(self, username1, username2) -> List[Dict]:
        # Check if user exists
        if not self.user_db.get_user(username2):
            return []
        
        # Get conversation
        return self.message_db.get_messages(username1, username2)