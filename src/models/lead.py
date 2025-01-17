from dataclasses import dataclass
from datetime import datetime

@dataclass
class Lead:
    name: str
    email: str
    platform: str  # github, linkedin, etc.
    category: str  # developer, business, etc.
    website: str = None
    description: str = None
    location: str = None
    timestamp: datetime = None

    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'platform': self.platform,
            'category': self.category,
            'website': self.website,
            'description': self.description,
            'location': self.location,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        } 