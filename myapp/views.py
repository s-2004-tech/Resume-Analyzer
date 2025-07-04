# myapp/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import Student, Resume
from .forms import ResumeUploadForm
from .resume_parser import extract_skills   # <- your own helper

# ------------ Utility helpers ------------------------------------------------

def _get_or_create_student(user: User) -> Student:
    """
    Returns the Student linked to `user`.
    If it doesn't exist, create a minimal Student record on the fly.
    """
    student, _ = Student.objects.get_or_create(
        user=user,
        defaults={
            "name": user.get_full_name() or user.username,
            "email": user.email,
            "college": None,
        },
    )
    return student


# ------------ Views -----------------------------------------------------------

def home(request):
    return render(request, "home.html")


@login_required
def upload_resume(request):
    """
    1. Accept a PDF file from ResumeUploadForm.
    2. Attach it to the logged‑in user's Student profile (auto‑creating the
       Student object if necessary).
    3. Parse the PDF → extract skills → choose the best matching job.
    4. Render result.html with the skill list and best job match.
    """
    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # ------------------------------------------------------------------
            # 1️⃣  Get (or lazily create) the Student object for this user
            # ------------------------------------------------------------------
            student = _get_or_create_student(request.user)

            # ------------------------------------------------------------------
            # 2️⃣  Save the Resume instance
            # ------------------------------------------------------------------
            resume: Resume = form.save(commit=False)
            resume.student = student
            resume.save()

            # ------------------------------------------------------------------
            # 3️⃣  Read & parse the PDF
            #      ⚠️  Using .read() may choke on binary; keep it simple here.
            # ------------------------------------------------------------------
            file_path = resume.file.path
            try:
                with open(file_path, "rb") as f:
                    raw_bytes = f.read()
                text = raw_bytes.decode("utf-8", errors="ignore")
            except Exception as exc:
                messages.error(request, f"Could not read your PDF: {exc}")
                return redirect("upload_resume")

            skills = extract_skills(text)

            # ------------------------------------------------------------------
            # 4️⃣  Very small rule‑based job matcher
            # ------------------------------------------------------------------
            jobs = {
                "Backend Developer": ["python", "django", "sql"],
                "ML Engineer": ["machine learning", "python"],
                "Frontend Developer": ["html", "css", "javascript"],
            }
            matches = {
                job: len(set(req) & set(skills)) for job, req in jobs.items()
            }
            best_match = max(matches, key=matches.get) if matches else "No match found"

            return render(
                request,
                "result.html",
                {"skills": skills, "match": best_match, "resume": resume},
            )
    else:
        form = ResumeUploadForm()

    return render(request, "upload.html", {"form": form})
