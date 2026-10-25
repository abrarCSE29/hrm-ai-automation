"""Seed demo data."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.models import Employee
from app.db.session import SessionLocal

db = SessionLocal()
if db.query(Employee).count() == 0:
    db.add(Employee(employee_id="E001", name="Alice", email="alice@example.com", department="Engineering", manager_id="MGR-001"))
    db.add(Employee(employee_id="E002", name="Bob", email="bob@example.com", department="HR", manager_id="MGR-002"))
    db.commit()
    print("Seeded employees.")
else:
    print("Already seeded.")
db.close()
