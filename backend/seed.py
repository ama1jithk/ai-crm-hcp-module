"""Seed a handful of demo HCPs. Run: python seed.py"""
from app.database import SessionLocal, Base, engine
from app import models

Base.metadata.create_all(bind=engine)

db = SessionLocal()

demo_hcps = [
    dict(first_name="Anjali", last_name="Rao", specialty="Cardiology",
         institution="City General Hospital", email="anjali.rao@cityhospital.example",
         phone="+91-98765-43210", territory="Kerala North",
         preferred_products=["CardioGuard 10mg", "CardioGuard XR"]),
    dict(first_name="Thomas", last_name="Mathew", specialty="Endocrinology",
         institution="Sunrise Clinic", email="t.mathew@sunriseclinic.example",
         phone="+91-98765-11122", territory="Kerala North",
         preferred_products=["GlucoBalance", "GlucoBalance Plus"]),
    dict(first_name="Priya", last_name="Nair", specialty="Oncology",
         institution="Regional Cancer Centre", email="priya.nair@rcc.example",
         phone="+91-98765-99887", territory="Kerala Central",
         preferred_products=["OncoCare Infusion"]),
]

for data in demo_hcps:
    exists = db.query(models.HCP).filter(models.HCP.email == data["email"]).first()
    if not exists:
        db.add(models.HCP(**data))

db.commit()
db.close()
print("Seeded demo HCPs.")
