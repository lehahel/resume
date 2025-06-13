from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uuid

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    user = relationship("User", backref="resumes")
    title = Column(String)
    theme = Column(String)
    isPublic = Column(Boolean)
    lastName = Column(String)
    firstName = Column(String)
    middleName = Column(String)
    birthDate = Column(DateTime)
    phoneNumber = Column(String)
    email = Column(String)
    position = Column(String)
    employment = Column(String)
    desiredSalary = Column(Integer)
    workSchedule = Column(String)
    isReadyForTrips = Column(Boolean)
    city = Column(String)
    canRelocate = Column(Boolean)
    citizenship = Column(String)
    gender = Column(String)
    hasChildren = Column(Boolean)
    languages = Column(String)
    driverLicenses = Column(String)
    hasMedicalBook = Column(Boolean)
    personalQualities = Column(String)
    photo = Column(String, nullable=True)
    work_experiences = relationship("WorkExperience", back_populates="resume", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="resume", cascade="all, delete-orphan")

class WorkExperience(Base):
    __tablename__ = "work_experiences"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    organization = Column(String)
    position = Column(String)
    startDate = Column(DateTime)
    endDate = Column(DateTime)
    responsibilities = Column(String)
    resume_id = Column(String, ForeignKey("resumes.id"))
    resume = relationship("Resume", back_populates="work_experiences")

class Education(Base):
    __tablename__ = "educations"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    institution = Column(String)
    faculty = Column(String)
    specialty = Column(String)
    graduationYear = Column(Integer)
    studyForm = Column(String)
    resume_id = Column(String, ForeignKey("resumes.id"))
    resume = relationship("Resume", back_populates="educations")

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 