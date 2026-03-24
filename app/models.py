from sqlalchemy import (String, Integer, Numeric, Date,
                        ForeignKey, Text, Index, CheckConstraint)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    pass


# справочники
class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[List['User']] = relationship(back_populates='role')


class Supplier(Base):
    __tablename__ = 'suppliers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    products: Mapped[List['Product']] = relationship(back_populates='supplier')


class Manufacturer(Base):
    __tablename__ = 'manufacturers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    products: Mapped[List['Product']] = relationship(
        back_populates='manufacturer')


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    products: Mapped[List['Product']] = relationship(back_populates='category')


class PickupPoint(Base):
    __tablename__ = 'pickup_points'

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=False)

    orders: Mapped[List['Order']] = relationship(back_populates='pickup_point')


class OrderStatus(Base):
    __tablename__ = 'order_statuses'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    display_order: Mapped[Optional[int]] = mapped_column(Integer)
    color_code: Mapped[Optional[str]] = mapped_column(String(7))

    orders: Mapped[List['Order']] = relationship(back_populates='status')


# основные таблицы
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey('roles.id'), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    login: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped['Role'] = relationship(back_populates='users')
    orders: Mapped[List['Order']] = relationship(back_populates='user')


class Product(Base):
    __tablename__ = 'products'

    article: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit: Mapped[str] = mapped_column(String(10), nullable=False)
    price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey('suppliers.id'), nullable=False)
    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey('manufacturers.id'), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey('categories.id'), nullable=False)
    discount: Mapped[int] = mapped_column(Integer, default=0)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    photo: Mapped[Optional[str]] = mapped_column(String(255))

    supplier: Mapped['Supplier'] = relationship(back_populates='products')
    manufacturer: Mapped['Manufacturer'] = relationship(
        back_populates='products')
    category: Mapped['Category'] = relationship(back_populates='products')
    order_items: Mapped[List['OrderItem']] = relationship(
        back_populates='product')


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False)
    order_date: Mapped[Date] = mapped_column(Date, nullable=False)
    delivery_date: Mapped[Date] = mapped_column(Date, nullable=False)
    pickup_point_id: Mapped[int] = mapped_column(
        ForeignKey('pickup_points.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False)
    pickup_code: Mapped[str] = mapped_column(String(20), nullable=False)
    status_id: Mapped[int] = mapped_column(
        ForeignKey('order_statuses.id'), nullable=False)

    pickup_point: Mapped['PickupPoint'] = relationship(back_populates='orders')
    user: Mapped['User'] = relationship(back_populates='orders')
    status: Mapped['OrderStatus'] = relationship(back_populates='orders')
    items: Mapped[List['OrderItem']] = relationship(
        back_populates='order', cascade='all, delete-orphan')


class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_article: Mapped[str] = mapped_column(
        ForeignKey('products.article', ondelete='RESTRICT'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint('quantity > 0'),
    )

    order: Mapped['Order'] = relationship(back_populates='items')
    product: Mapped['Product'] = relationship(back_populates='order_items')


# индексы

Index('idx_users_role', User.role_id)

Index('idx_products_supplier', Product.supplier_id)
Index('idx_products_manufacturer', Product.manufacturer_id)
Index('idx_products_category', Product.category_id)

Index('idx_orders_pickup_point', Order.pickup_point_id)
Index('idx_orders_user', Order.user_id)
Index('idx_orders_status', Order.status_id)

Index('idx_order_items_order', OrderItem.order_id)
Index('idx_order_items_product', OrderItem.product_article)
