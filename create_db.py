"""Throwaway script to verify the schema creates correctly.

Run this once to confirm sentinel.db gets created with all five tables.
Not part of the package — just a manual checkpoint.
"""

from sentinel.db import engine
from sentinel.models import Base

Base.metadata.create_all(engine)
print("Done. Tables created:", list(Base.metadata.tables.keys()))