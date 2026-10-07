from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExamScores(BaseModel):
    cae1: float
    cae2: float
    put: float

class StudentData(BaseModel):
    name: str
    enrollment: str
    attendance: float
    marks: Dict[str, ExamScores]

@app.post("/api/analyze")
def analyze_performance(data: StudentData):
    subjects = list(data.marks.keys())
    total_score = 0
    max_possible = len(subjects) * 130  # CAE1(30) + CAE2(30) + PUT(70) = 130 per subject
    
    analysis_details = []
    weak_subjects = []
    strong_subjects = []

    for sub, scores in data.marks.items():
        sub_total = scores.cae1 + scores.cae2 + scores.put
        total_score += sub_total
        
        # Percentage calculation per subject out of 130
        sub_percentage = (sub_total / 130) * 100
        
        if sub_percentage < 50:
            weak_subjects.append(sub)
        elif sub_percentage >= 75:
            strong_subjects.append(sub)

        analysis_details.append({
            "subject": sub,
            "cae1": scores.cae1,
            "cae2": scores.cae2,
            "put": scores.put,
            "total": sub_total,
            "average": round(sub_percentage, 2)
        })

    overall_percentage = round((total_score / max_possible) * 100, 2) if max_possible > 0 else 0

    recommendations = []
    if data.attendance < 75:
        recommendations.append(f"⚠️ Your attendance ({data.attendance}%) is below the 75% requirement. Please attend regular classes to avoid attendance shortage.")
    
    if weak_subjects:
        recommendations.append(f"🎯 You need to focus more on the following subjects: **{', '.join(weak_subjects)}**. Revise their core concepts and practice previous years' questions.")
    else:
        recommendations.append("🌟 Your performance across all subjects is excellent! Keep up this consistency.")

    if strong_subjects:
        recommendations.append(f"🏆 You have a strong command over: **{', '.join(strong_subjects)}**. Try solving advanced problems to score even better.")

    recommendations.append("💡 **General Tip:** Review your mistakes from the PUT exams and actively participate in faculty doubt-clearing sessions.")

    return {
        "name": data.name,
        "enrollment": data.enrollment,
        "attendance": data.attendance,
        "overall_percentage": overall_percentage,
        "subject_analysis": analysis_details,
        "recommendations": recommendations,
        "weak_subjects": weak_subjects
    }