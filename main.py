
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

# Initialize FastAPI
app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb+srv://wildaboutcomputers00s:1234@cluster0.m5rnzqi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["library_management"]
collection = db["students"]

# Pydantic models
class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

class StudentOut(Student):
    id: str

# API endpoints
@app.post("/students", response_model=StudentOut, status_code=201)
def create_student(student: Student):
    inserted_id = collection.insert_one(student.dict()).inserted_id
    return {"id": str(inserted_id), **student.dict()}

@app.get("/students", response_model=list[StudentOut])
def list_students(country: str = None, age: int = None):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}
    students = list(collection.find(query, {"_id": 1, "name": 1, "age": 1, "address": 1}))
    students_out = [{"id": str(student["_id"]), **student} for student in students]
    return students_out


@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: str):
    student = collection.find_one({"_id": ObjectId(student_id)}, {"_id": 0})
    if student:
        return {"id": student_id, **student}
    else:
        raise HTTPException(status_code=404, detail="Student not found")


@app.patch("/students/{student_id}", status_code=204)
def update_student(student_id: str, student: Student):
    update_result = collection.update_one(
        {"_id": ObjectId(student_id)}, {"$set": student.dict(exclude_unset=True)}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students/{student_id}", status_code=200)
def delete_student(student_id: str):
    delete_result = collection.delete_one({"_id": ObjectId(student_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
