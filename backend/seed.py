from app.db import Base, SessionLocal, engine
from app.models import Job, Site, Worker
from app.job_parser import parse_job_description

CITIES = [
    "Bengaluru",
    "Mumbai",
    "Delhi",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Kolkata",
    "Jaipur",
    "Ahmedabad",
    "Lucknow",
    "Noida",
    "Gurugram",
    "Kochi",
    "Indore",
    "Nagpur",
    "Coimbatore",
    "Patna",
    "Bhopal",
    "Chandigarh",
    "Surat",
]

FIRST = ["Ravi", "Sneha", "Amit", "Fatima", "Priya", "Arjun", "Meera", "Imran", "Lakshmi", "Vikram", "Nisha", "Rohit", "Divya", "Karan", "Ayesha"]
LAST = ["Kumar", "Sharma", "Iyer", "Khan", "Nair", "Patel", "Reddy", "Singh", "Das", "Menon", "Gupta", "Pawar", "Yadav", "Pillai", "Joshi"]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Job).count() == 0:
            desc = (
                "We are hiring Warehouse Associates in Bengaluru for a 24x7 fulfillment center. "
                "Must know Hindi and basic English, inventory counting, and be comfortable with night shifts. "
                "1+ years preferred. Forklift certification is a plus."
            )
            db.add(
                Job(
                    title="Warehouse Associate",
                    company="Northline Logistics",
                    location="Bengaluru",
                    description=desc,
                    parsed=parse_job_description(desc, "Warehouse Associate", "Bengaluru"),
                )
            )
            desc2 = (
                "Field Sales Executive for FMCG in Delhi NCR. Strong negotiation, Hindi + English, "
                "and 2 years of distributor sales. Two-wheeler required."
            )
            db.add(
                Job(
                    title="Field Sales Executive",
                    company="Northline Logistics",
                    location="Delhi",
                    description=desc2,
                    parsed=parse_job_description(desc2, "Field Sales Executive", "Delhi"),
                )
            )
        if db.query(Site).count() == 0:
            for i in range(100):
                city = CITIES[i % len(CITIES)]
                site = Site(
                    code=f"S{i+1:03d}",
                    name=f"{city} Site {i+1:03d}",
                    city=city,
                    landline=f"+9111400{i+1:04d}",
                    supervisor_name=f"{FIRST[i % len(FIRST)]} {LAST[i % len(LAST)]}",
                    supervisor_phone=f"+91971{i+1:07d}",
                )
                db.add(site)
                db.flush()
                for w in range(10):
                    idx = i * 10 + w
                    db.add(
                        Worker(
                            employee_code=f"E{idx+1:04d}",
                            name=f"{FIRST[(idx+3) % len(FIRST)]} {LAST[(idx+5) % len(LAST)]}",
                            site_id=site.id,
                            shift=["A", "B", "C"][w % 3],
                            spoken_pin=f"{1000 + (idx % 9000)}",
                            rfid=f"RFID{idx+1:06d}",
                        )
                    )
        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
