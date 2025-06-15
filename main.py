from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
import os
from datetime import datetime
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi import Response, Request
from io import BytesIO

from database import get_db, User, Resume, WorkExperience as DBWorkExperience, Education as DBEducation
from security import get_password_hash, verify_password
from pydantic import BaseModel, EmailStr, Field
from auth import create_access_token, get_current_user
from pdf import render_resume_pdf  # adjust import if needed

app = FastAPI(
    title="FastAPI Backend",
    description="A modern FastAPI backend application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Backend"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class RegisterRequest(BaseModel):
    Name: str
    Email: str 
    Password: str

class UserData(BaseModel):
    id: str
    name: str
    email: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    user: UserData

class LoginRequest(BaseModel):
    Login: str
    Password: str

class WorkExperience(BaseModel):
    organization: str
    workExpPosition: str
    startDate: datetime
    endDate: datetime
    responsibilities: str

class Education(BaseModel):
    institution: str
    faculty: str
    specialty: str
    graduationYear: int
    studyForm: str

class ResumeRequest(BaseModel):
    title: str
    theme: Optional[str] = None
    isPublic: bool
    lastName: str
    firstName: str
    middleName: Optional[str] = None
    birthDate: datetime
    phoneNumber: Optional[str] = None
    email: str
    position: str
    employment: str
    desiredSalary: Optional[int] = None
    workSchedule: str
    noPatronymic: Optional[bool] = False
    isReadyForTrips: Optional[bool] = False
    city: str
    canRelocate: Optional[bool] = None
    citizenship: str
    gender: Optional[str] = "Мужской"
    hasChildren: Optional[bool] = False
    workExperiences: Optional[List[WorkExperience]] = []
    educations: Optional[List[Education]] = []
    languages: Optional[str] = None
    driverLicenses: Optional[str] = None
    hasMedicalBook: Optional[bool] = False
    personalQualities: Optional[str] = None

class WorkExperienceUpdate(BaseModel):
    organization: Optional[str] = None
    workExpPosition: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    responsibilities: Optional[str] = None

class EducationUpdate(BaseModel):
    institution: Optional[str] = None
    faculty: Optional[str] = None
    specialty: Optional[str] = None
    graduationYear: Optional[int] = None
    studyForm: Optional[str] = None

class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    theme: Optional[str] = Field(default=None)
    isPublic: Optional[bool] = None
    lastName: Optional[str] = None
    firstName: Optional[str] = None
    middleName: Optional[str] = None
    birthDate: Optional[datetime] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    employment: Optional[str] = None
    desiredSalary: Optional[int] = None
    workSchedule: Optional[str] = None
    isReadyForTrips: Optional[bool] = None
    city: Optional[str] = None
    canRelocate: Optional[bool] = None
    citizenship: Optional[str] = None
    gender: Optional[str] = None
    hasChildren: Optional[bool] = None
    workExperiences: Optional[List[WorkExperienceUpdate]] = None
    educations: Optional[List[EducationUpdate]] = None
    languages: Optional[str] = None
    driverLicenses: Optional[str] = None
    hasMedicalBook: Optional[bool] = None
    personalQualities: Optional[str] = None

@app.post("/api/Auth/register", response_model=UserResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == request.Email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(request.Password)
    db_user = User(
        name=request.Name,
        email=request.Email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token({"sub": db_user.id})
    response = JSONResponse(UserResponse(user=UserData.model_validate(db_user)).model_dump())
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax")
    return response

@app.post("/api/Auth/login", response_model=UserResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter((User.email == request.Login) | (User.name == request.Login)).first()
    if not db_user or not verify_password(request.Password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": db_user.id})
    response = JSONResponse(UserResponse(user=UserData.model_validate(db_user)).model_dump())
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax")
    return response

@app.post("/api/Auth/logout")
async def logout():
    response = JSONResponse({"detail": "Logged out successfully"})
    response.delete_cookie(key="access_token")
    return response

@app.get("/api/Auth/check")
async def check_auth(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="User is not authorized")
    return {"username": user.name}


@app.put("/api/Resume/{id}/photo")
async def upload_resume_photo(id: str, PhotoFile: UploadFile = File(...), user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_resume = db.query(Resume).filter(Resume.id == id, Resume.user_id == user.id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    os.makedirs("photos", exist_ok=True)
    filename = f"{id}_{PhotoFile.filename}"
    file_location = os.path.join("photos", filename)
    with open(file_location, "wb") as f:
        content = await PhotoFile.read()
        f.write(content)
    # Save only the filename to the database
    db_resume.photo = filename
    db.commit()
    return {"detail": "Photo uploaded successfully", "filename": filename}

@app.post("/api/Resume")
async def create_resume(resume: ResumeRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_resume = Resume(
        user_id=user.id,
        title=resume.title,
        theme=resume.theme,
        isPublic=resume.isPublic,
        lastName=resume.lastName,
        firstName=resume.firstName,
        middleName=resume.middleName,
        birthDate=resume.birthDate,
        phoneNumber=resume.phoneNumber,
        email=resume.email,
        position=resume.position,
        employment=resume.employment,
        desiredSalary=resume.desiredSalary,
        workSchedule=resume.workSchedule,
        isReadyForTrips=resume.isReadyForTrips,
        city=resume.city,
        canRelocate=resume.canRelocate,
        citizenship=resume.citizenship,
        gender=resume.gender,
        hasChildren=resume.hasChildren,
        languages=resume.languages,
        driverLicenses=resume.driverLicenses,
        hasMedicalBook=resume.hasMedicalBook,
        personalQualities=resume.personalQualities
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)

    # Add work experiences
    for we in resume.workExperiences:
        db_we = DBWorkExperience(
            organization=we.organization,
            position=we.workExpPosition,
            startDate=we.startDate,
            endDate=we.endDate,
            responsibilities=we.responsibilities,
            resume_id=db_resume.id
        )
        db.add(db_we)
    # Add educations
    for edu in resume.educations:
        db_edu = DBEducation(
            institution=edu.institution,
            faculty=edu.faculty,
            specialty=edu.specialty,
            graduationYear=edu.graduationYear,
            studyForm=edu.studyForm,
            resume_id=db_resume.id
        )
        db.add(db_edu)
    db.commit()
    db.refresh(db_resume)

    # Fetch with relationships
    db_resume = db.query(Resume).filter(Resume.id == db_resume.id).first()
    work_experiences = db.query(DBWorkExperience).filter(DBWorkExperience.resume_id == db_resume.id).all()
    educations = db.query(DBEducation).filter(DBEducation.resume_id == db_resume.id).all()

    # Prepare response
    response = {
        "id": db_resume.id,
        "title": db_resume.title,
        "theme": db_resume.theme,
        "isPublic": db_resume.isPublic,
        "lastName": db_resume.lastName,
        "firstName": db_resume.firstName,
        "middleName": db_resume.middleName,
        "birthDate": db_resume.birthDate,
        "phoneNumber": db_resume.phoneNumber,
        "email": db_resume.email,
        "position": db_resume.position,
        "employment": db_resume.employment,
        "desiredSalary": db_resume.desiredSalary,
        "workSchedule": db_resume.workSchedule,
        "isReadyForTrips": db_resume.isReadyForTrips,
        "city": db_resume.city,
        "canRelocate": db_resume.canRelocate,
        "citizenship": db_resume.citizenship,
        "gender": db_resume.gender,
        "hasChildren": db_resume.hasChildren,
        "languages": db_resume.languages,
        "driverLicenses": db_resume.driverLicenses,
        "hasMedicalBook": db_resume.hasMedicalBook,
        "personalQualities": db_resume.personalQualities,
        "workExperiences": [
            {
                "organization": we.organization,
                "workExpPosition": we.position,
                "startDate": we.startDate,
                "endDate": we.endDate,
                "responsibilities": we.responsibilities
            } for we in work_experiences
        ],
        "educations": [
            {
                "institution": edu.institution,
                "faculty": edu.faculty,
                "specialty": edu.specialty,
                "graduationYear": edu.graduationYear,
                "studyForm": edu.studyForm
            } for edu in educations
        ]
    }
    return response

@app.put("/api/Resume/{id}")
async def update_resume(id: str = Path(...), resume_update: ResumeUpdate = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_resume = db.query(Resume).filter(Resume.id == id, Resume.user_id == user.id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    update_data = resume_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "workExperiences" or field == "educations":
            continue  # Nested updates not handled here
        setattr(db_resume, field, value)
    db.commit()
    db.refresh(db_resume)

    # Fetch related work experiences and educations
    work_experiences = db.query(DBWorkExperience).filter(DBWorkExperience.resume_id == db_resume.id).all()
    educations = db.query(DBEducation).filter(DBEducation.resume_id == db_resume.id).all()

    response = {
        "id": db_resume.id,
        "title": db_resume.title,
        "theme": db_resume.theme,
        "isPublic": db_resume.isPublic,
        "lastName": db_resume.lastName,
        "firstName": db_resume.firstName,
        "middleName": db_resume.middleName,
        "birthDate": db_resume.birthDate,
        "phoneNumber": db_resume.phoneNumber,
        "email": db_resume.email,
        "position": db_resume.position,
        "employment": db_resume.employment,
        "desiredSalary": db_resume.desiredSalary,
        "workSchedule": db_resume.workSchedule,
        "isReadyForTrips": db_resume.isReadyForTrips,
        "city": db_resume.city,
        "canRelocate": db_resume.canRelocate,
        "citizenship": db_resume.citizenship,
        "gender": db_resume.gender,
        "hasChildren": db_resume.hasChildren,
        "languages": db_resume.languages,
        "driverLicenses": db_resume.driverLicenses,
        "hasMedicalBook": db_resume.hasMedicalBook,
        "personalQualities": db_resume.personalQualities,
        "workExperiences": [
            {
                "organization": we.organization,
                "workExpPosition": we.position,
                "startDate": we.startDate,
                "endDate": we.endDate,
                "responsibilities": we.responsibilities
            } for we in work_experiences
        ],
        "educations": [
            {
                "institution": edu.institution,
                "faculty": edu.faculty,
                "specialty": edu.specialty,
                "graduationYear": edu.graduationYear,
                "studyForm": edu.studyForm
            } for edu in educations
        ]
    }
    return response

@app.get("/api/Resume/my")
async def get_my_resumes(db: Session = Depends(get_db), user=Depends(get_current_user)):
    resumes = db.query(Resume).filter(Resume.user_id == user.id).all()
    result = []
    for r in resumes:
        work_experiences = db.query(DBWorkExperience).filter(DBWorkExperience.resume_id == r.id).all()
        educations = db.query(DBEducation).filter(DBEducation.resume_id == r.id).all()
        result.append({
            "id": r.id,
            "user_id": r.user_id,
            "title": r.title,
            "theme": r.theme,
            "isPublic": r.isPublic,
            "lastName": r.lastName,
            "firstName": r.firstName,
            "middleName": r.middleName,
            "birthDate": r.birthDate,
            "phoneNumber": r.phoneNumber,
            "email": r.email,
            "position": r.position,
            "employment": r.employment,
            "desiredSalary": r.desiredSalary,
            "workSchedule": r.workSchedule,
            "isReadyForTrips": r.isReadyForTrips,
            "city": r.city,
            "canRelocate": r.canRelocate,
            "citizenship": r.citizenship,
            "gender": r.gender,
            "hasChildren": r.hasChildren,
            "languages": r.languages,
            "driverLicenses": r.driverLicenses,
            "hasMedicalBook": r.hasMedicalBook,
            "personalQualities": r.personalQualities,
            "workExperiences": [
                {
                    "organization": we.organization,
                    "workExpPosition": we.position,
                    "startDate": we.startDate,
                    "endDate": we.endDate,
                    "responsibilities": we.responsibilities
                } for we in work_experiences
            ],
            "educations": [
                {
                    "institution": edu.institution,
                    "faculty": edu.faculty,
                    "specialty": edu.specialty,
                    "graduationYear": edu.graduationYear,
                    "studyForm": edu.studyForm
                } for edu in educations
            ]
        })
    return result

@app.delete("/api/Resume/{id}")
async def delete_resume(id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_resume = db.query(Resume).filter(Resume.id == id, Resume.user_id == user.id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    db.delete(db_resume)
    db.commit()
    return {"detail": "Resume deleted successfully"}

@app.get("/api/Resume/{id}/pdf")
async def get_resume_pdf(id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_resume = db.query(Resume).filter(Resume.id == id, Resume.user_id == user.id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    pdf_bytes = render_resume_pdf(db_resume, getattr(db_resume, "theme", "modern"))
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers={
        "Content-Disposition": f"inline; filename=resume_{id}.pdf"
    })

@app.get("/api/Resume/{id}/photo")
async def get_resume_photo(id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_resume = db.query(Resume).filter(Resume.id == id, Resume.user_id == user.id).first()
    if not db_resume or not db_resume.photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    file_path = os.path.join("photos", db_resume.photo)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Photo file not found")
    return FileResponse(file_path, media_type="image/jpeg", filename=os.path.basename(file_path))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 