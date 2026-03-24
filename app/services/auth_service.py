from sqlalchemy.orm import Session
from app.models import User


class AuthService:
    def __init__(self, session: Session):
        self.session = session

    def authenticate(self, login: str, password: str):
        user = (
            self.session.query(User)
            .filter(User.login == login)
            .first()
        )

        if not user or user.password != password:
            return None

        return user
