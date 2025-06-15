from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uuid
import datetime

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
    theme = Column(String, nullable=True)
    isPublic = Column(Boolean)
    lastName = Column(String, nullable=False)
    firstName = Column(String, nullable=False)
    middleName = Column(String, nullable=True)
    birthDate = Column(DateTime, nullable=False)
    phoneNumber = Column(String, nullable=True)
    email = Column(String, nullable=False)
    position = Column(String, nullable=False)
    employment = Column(String, nullable=False)
    desiredSalary = Column(Integer, nullable=True)
    workSchedule = Column(String, nullable=False)
    isReadyForTrips = Column(Boolean, nullable=True)
    city = Column(String, nullable=False)
    canRelocate = Column(Boolean, nullable=True)
    citizenship = Column(String, nullable=False)
    gender = Column(String, nullable=True)
    hasChildren = Column(Boolean, nullable=True)
    languages = Column(String, nullable=True)
    driverLicenses = Column(String, nullable=True)
    hasMedicalBook = Column(Boolean, nullable=True)
    personalQualities = Column(String, nullable=True)
    work_experiences = relationship("WorkExperience", back_populates="resume", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    photo = relationship("ResumePhoto", back_populates="resume", uselist=False)

class WorkExperience(Base):
    __tablename__ = "work_experiences"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    organization = Column(String, nullable=True)
    position = Column(String, nullable=True)
    startDate = Column(DateTime, nullable=True)
    endDate = Column(DateTime, nullable=True)
    responsibilities = Column(String, nullable=True)
    resume_id = Column(String, ForeignKey("resumes.id"))
    resume = relationship("Resume", back_populates="work_experiences")

class Education(Base):
    __tablename__ = "educations"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    institution = Column(String, nullable=True)
    faculty = Column(String, nullable=True)
    specialty = Column(String, nullable=True)
    graduationYear = Column(Integer, nullable=True)
    studyForm = Column(String, nullable=True)
    resume_id = Column(String, ForeignKey("resumes.id"))
    resume = relationship("Resume", back_populates="educations")

class ResumeRequest(Base):
    __tablename__ = "resume_requests"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    middleName = Column(String, nullable=True)
    position = Column(String, nullable=False)
    employment = Column(String, nullable=False)
    desiredSalary = Column(String, nullable=True)
    workSchedule = Column(String, nullable=False)
    noPatronymic = Column(Boolean, nullable=True, default=False)
    birthDate = Column(String, nullable=False)
    phoneNumber = Column(String, nullable=True)
    email = Column(String, nullable=False)
    isReadyForTrips = Column(Boolean, nullable=True, default=False)
    city = Column(String, nullable=False)
    canRelocate = Column(String, nullable=True)
    citizenship = Column(String, nullable=False)
    maritalStatus = Column(String, nullable=True)
    gender = Column(String, nullable=True, default="Мужской")
    hasChildren = Column(Boolean, nullable=True, default=False)
    driverLicenses = Column(String, nullable=True)  # Will store JSON string of driver licenses
    hasMedicalBook = Column(Boolean, nullable=True, default=False)
    photo = Column(String, nullable=True)
    theme = Column(String, nullable=True)
    languages = Column(String, nullable=True)
    personalQualities = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class ResumePhoto(Base):
    __tablename__ = "resume_photos"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=True)
    resume = relationship("Resume", back_populates="photo")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 