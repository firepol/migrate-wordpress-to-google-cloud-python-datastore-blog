from dataclasses import dataclass

from flask_login import UserMixin
from google.cloud import datastore


@dataclass
class User(UserMixin):
    id: str
    name: str
    email: str
    profile_pic: str

    @staticmethod
    def get(user_id):
        client = datastore.Client()
        key = client.key('User', user_id)
        data = client.get(key)

        if not data:
            return None

        user = User(id=data.key.id_or_name, name=data['name'], email=data['email'], profile_pic=data['profile_pic'])
        return user

    @staticmethod
    def create(data):
        client = datastore.Client()
        key = client.key('User', data.id)
        user = datastore.Entity(key=key)
        user['name'] = data.name
        user['email'] = data.email
        user['profile_pic'] = data.profile_pic
        client.put(user)
        return user
