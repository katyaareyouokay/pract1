from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Product


class ProductService:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        stmt = select(Product).order_by(Product.photo)
        return self.session.scalars(stmt).all()
