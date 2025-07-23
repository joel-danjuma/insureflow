# This file makes the 'schemas' directory a Python package.

# Import all schemas to make them available at package level
from .auth import UserCreate as AuthUserCreate, UserResponse, Token, TokenData
from .user import UserCreate, UserUpdate, User, UserInDB, UserBase, UserInDBBase
from .broker import *
from .dashboard import *
from .payment import *
from .policy import *
from .premium import *

# Make the auth UserCreate available as the default UserCreate
# since that's what the CRUD is expecting
UserCreate = AuthUserCreate 