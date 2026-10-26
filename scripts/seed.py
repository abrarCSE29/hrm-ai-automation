"""Seed demo data."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.models import Employee, PendingSalary, Salary
from app.db.session import SessionLocal

db = SessionLocal()
if db.query(Employee).count() == 0:
    db.add(Employee(employee_id="E001", name="Alice", email="alice@example.com", department="Engineering", manager_id="MGR-001"))
    db.add(Employee(employee_id="E002", name="Bob", email="bob@example.com", department="HR", manager_id="MGR-002"))
    db.commit()
    print("Seeded employees.")
else:
    print("Employees already seeded.")

if db.query(Salary).count() == 0:
    db.add(Salary(employee_id="E001", amount=50000.0, currency="BDT", effective_date="2026-01-01"))
    db.add(Salary(employee_id="E002", amount=45000.0, currency="BDT", effective_date="2026-01-01"))
    db.commit()
    print("Seeded salaries.")
else:
    print("Salaries already seeded.")

if db.query(PendingSalary).count() == 0:
    db.add(PendingSalary(employee_id="E001", amount=5000.0, description="Bonus arrears", due_date="2026-10-31", status="pending"))
    db.add(PendingSalary(employee_id="E002", amount=2500.0, description="Overtime pay", due_date="2026-10-31", status="pending"))
    db.commit()
    print("Seeded pending salaries.")
else:
    print("Pending salaries already seeded.")

db.close()
