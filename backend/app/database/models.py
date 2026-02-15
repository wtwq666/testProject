"""ORM 模型：业务表 + 会话表"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class BusinessBase(DeclarativeBase):
    """业务库 Base，仅含 departments, employees, products, sales_records"""
    pass


class SessionBase(DeclarativeBase):
    """会话库 Base，仅含 sessions, messages"""
    pass


# ---------- 业务库表 (smart_data.db) ----------


class Department(BusinessBase):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    manager: Mapped[str] = mapped_column(String(64), nullable=False)
    budget: Mapped[float] = mapped_column(Float, default=0)

    employees = relationship("Employee", back_populates="department")


class Employee(BusinessBase):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    position: Mapped[str] = mapped_column(String(64), nullable=False)
    salary: Mapped[float] = mapped_column(Float, default=0)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)

    department = relationship("Department", back_populates="employees")
    sales_records = relationship("SalesRecord", back_populates="employee")


class Product(BusinessBase):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    price: Mapped[float] = mapped_column(Float, default=0)
    stock: Mapped[int] = mapped_column(Integer, default=0)

    sales_records = relationship("SalesRecord", back_populates="product")


class SalesRecord(BusinessBase):
    __tablename__ = "sales_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    amount: Mapped[float] = mapped_column(Float, default=0)
    sale_date: Mapped[date] = mapped_column(Date, nullable=False)

    product = relationship("Product", back_populates="sales_records")
    employee = relationship("Employee", back_populates="sales_records")


# ---------- 会话库表 (sessions.db) ----------


class Session(SessionBase):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(256), default="新对话")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(SessionBase):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # user | assistant
    content: Mapped[str] = mapped_column(Text, default="")
    chart_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")
