from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

# Association table for many-to-many relationship between roles and permissions
role_permissions_table = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("user_mgmt.roles.role_id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("user_mgmt.permissions.permission_id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    schema="user_mgmt"
)

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "user_mgmt"}

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    permissions = relationship("Permission", secondary=role_permissions_table, back_populates="roles")
    users = relationship("User", back_populates="role")

class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = {"schema": "user_mgmt"}

    permission_id = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    roles = relationship("Role", secondary=role_permissions_table, back_populates="permissions")

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "user_mgmt"}

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    organization = Column(String(100))
    role_id = Column(Integer, ForeignKey("user_mgmt.roles.role_id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    role = relationship("Role", back_populates="users")

print("User, Role, Permission models defined.")

