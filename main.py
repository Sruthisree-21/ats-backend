from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JOB_KEYWORDS = [
    "Python", "React", "JavaScript", "FastAPI", "Node.js",
    "HTML", "CSS", "API", "REST", "Database", "SQL",
    "Git", "Docker", "AWS", "Cloud", "Photoshop", "Figma",
    "Branding", "UI/UX", "Design", "Project Management"
]

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    if filename.lower().endswith('.pdf'):
        try:
            pdf_file = io.BytesIO(file_content)
            with pdfplumber.open(pdf_file) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
                return text
        except:
            raise HTTPException(status_code=400, detail="Invalid PDF file")
    else:
        try:
            return file_content.decode("utf-8")
        except:
            raise HTTPException(status_code=400, detail="Invalid file encoding")

def find_keywords(text: str, keywords: list) -> dict:
    text_lower = text.lower()
    found = [k for k in keywords if k.lower() in text_lower]
    missing = [k for k in keywords if k.lower() not in text_lower]
    return {"found": found, "missing": missing}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/check_resume")
async def check_resume(file: UploadFile = File(...)):
    try:
        content = await file.read()
        resume_text = extract_text_from_file(content, file.filename)
        result = find_keywords(resume_text, JOB_KEYWORDS)
        return {
            "resume": resume_text[:1000],
            "job": ",".join(JOB_KEYWORDS),
            "result": result,
            "total_keywords": len(JOB_KEYWORDS),
            "found_count": len(result["found"]),
            "missing_count": len(result["missing"]),
            "match_percentage": round((len(result["found"]) / len(JOB_KEYWORDS) * 100), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
