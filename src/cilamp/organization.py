"""Deterministic fictional employee generation for simulation mode."""

from __future__ import annotations

from cilamp.domain import Employee, EmployeeStatus
from cilamp.iam_catalog import ROLES


FIRST_NAMES = (
    "Aarav", "Aisha", "Amelia", "Arjun", "Daniel", "Diya", "Elena", "Ethan",
    "Fatima", "Ishaan", "James", "Kavya", "Layla", "Liam", "Maya", "Meera",
    "Neha", "Noah", "Olivia", "Priya", "Rohan", "Sara", "Sofia", "Vihaan", "Zara",
)
LAST_NAMES = (
    "Anderson", "Bose", "Brown", "Chen", "Davis", "Garcia", "Gupta", "Iyer",
    "Johnson", "Khan", "Kim", "Kumar", "Lee", "Martin", "Mehta", "Miller",
    "Patel", "Rao", "Shah", "Singh",
)

# A realistic mid-sized distribution. Values total exactly 500.
ROLE_COUNTS = {
    "Developer": 120,
    "Engineering Manager": 30,
    "Finance Analyst": 55,
    "Finance Manager": 15,
    "HR Administrator": 35,
    "Sales User": 95,
    "Sales Manager": 25,
    "IT Administrator": 35,
    "Security Administrator": 15,
    "Marketing User": 75,
}


def generate_employees() -> tuple[Employee, ...]:
    """Generate the same 500 fictional identities on every clean seed."""

    employees: list[Employee] = []
    sequence = 1
    for role in ROLES:
        for _ in range(ROLE_COUNTS[role.name]):
            first_name = FIRST_NAMES[(sequence - 1) % len(FIRST_NAMES)]
            last_name = LAST_NAMES[((sequence - 1) // len(FIRST_NAMES)) % len(LAST_NAMES)]
            employee_id = f"CIL{sequence:04d}"
            employees.append(
                Employee(
                    employee_id=employee_id,
                    display_name=f"{first_name} {last_name}",
                    email=f"{first_name.lower()}.{last_name.lower()}.{sequence:04d}@example.iamconcen",
                    department=role.department,
                    job_role=role.name,
                    status=EmployeeStatus.ACTIVE,
                )
            )
            sequence += 1

    return tuple(employees)
