"""
Generate 48 realistic university academic policy PDFs using ReportLab.
Run:  python pdf_generator.py
Output: backend/data/documents/
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import ListFlowable, ListItem
import os

OUTPUT_DIR = Path(__file__).parent / "data" / "documents"

# ── Brand colours ────────────────────────────────────────────────────────────
NAVY   = HexColor("#1a2e5a")
GOLD   = HexColor("#c8a94a")
LIGHT  = HexColor("#f0f4f8")
GRAY   = HexColor("#4a5568")
LGRAY  = HexColor("#e2e8f0")
RED    = HexColor("#c53030")
GREEN  = HexColor("#276749")

UNIVERSITY_NAME = "Westbrook University"
POLICY_OFFICE   = "Office of Academic Affairs"


# ── Style helpers ─────────────────────────────────────────────────────────────

def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "uni_name": ParagraphStyle(
            "uni_name", fontSize=18, fontName="Helvetica-Bold",
            textColor=NAVY, alignment=TA_CENTER, spaceAfter=2,
        ),
        "uni_sub": ParagraphStyle(
            "uni_sub", fontSize=10, fontName="Helvetica",
            textColor=GOLD, alignment=TA_CENTER, spaceAfter=4,
        ),
        "doc_title": ParagraphStyle(
            "doc_title", fontSize=15, fontName="Helvetica-Bold",
            textColor=NAVY, alignment=TA_CENTER, spaceBefore=6, spaceAfter=4,
        ),
        "meta": ParagraphStyle(
            "meta", fontSize=9, fontName="Helvetica",
            textColor=GRAY, alignment=TA_CENTER, spaceAfter=2,
        ),
        "h1": ParagraphStyle(
            "h1", fontSize=12, fontName="Helvetica-Bold",
            textColor=NAVY, spaceBefore=14, spaceAfter=4, leftIndent=0,
        ),
        "h2": ParagraphStyle(
            "h2", fontSize=11, fontName="Helvetica-Bold",
            textColor=GRAY, spaceBefore=8, spaceAfter=3, leftIndent=12,
        ),
        "body": ParagraphStyle(
            "body", fontSize=10, fontName="Helvetica",
            textColor=black, spaceBefore=3, spaceAfter=3,
            leading=15, alignment=TA_JUSTIFY, leftIndent=12,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontSize=10, fontName="Helvetica",
            textColor=black, spaceBefore=2, spaceAfter=2,
            leading=14, leftIndent=28, bulletIndent=16,
        ),
        "footer": ParagraphStyle(
            "footer", fontSize=8, fontName="Helvetica",
            textColor=GRAY, alignment=TA_CENTER,
        ),
        "toc_item": ParagraphStyle(
            "toc_item", fontSize=10, fontName="Helvetica",
            textColor=NAVY, spaceBefore=2, spaceAfter=2, leftIndent=16,
        ),
    }
    return styles


def header_block(styles, policy_number, effective_date, revision="1.0"):
    elems = []
    # ── Top colour bar ──
    elems.append(Table(
        [[""]],
        colWidths=[7.5 * inch], rowHeights=[6],
        style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY)]),
    ))
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(UNIVERSITY_NAME, styles["uni_name"]))
    elems.append(Paragraph(POLICY_OFFICE, styles["uni_sub"]))
    elems.append(Spacer(1, 4))
    # ── Meta row ──
    meta_data = [[
        Paragraph(f"Policy No: <b>{policy_number}</b>", styles["meta"]),
        Paragraph(f"Effective: <b>{effective_date}</b>", styles["meta"]),
        Paragraph(f"Revision: <b>{revision}</b>", styles["meta"]),
    ]]
    meta_table = Table(meta_data, colWidths=[2.5 * inch, 2.5 * inch, 2.5 * inch])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, LGRAY),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, LGRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elems.append(meta_table)
    elems.append(Spacer(1, 8))
    elems.append(HRFlowable(width="100%", thickness=1.5, color=GOLD))
    elems.append(Spacer(1, 6))
    return elems


def section(styles, number, title, paragraphs, bullets=None, sub_sections=None):
    elems = []
    elems.append(Paragraph(f"{number}. {title}", styles["h1"]))
    for para in paragraphs:
        elems.append(Paragraph(para, styles["body"]))
    if bullets:
        for b in bullets:
            elems.append(Paragraph(f"• {b}", styles["bullet"]))
    if sub_sections:
        for ss_num, ss_title, ss_paras, ss_bullets in sub_sections:
            elems.append(Paragraph(f"{ss_num} {ss_title}", styles["h2"]))
            for p in ss_paras:
                elems.append(Paragraph(p, styles["body"]))
            if ss_bullets:
                for b in ss_bullets:
                    elems.append(Paragraph(f"• {b}", styles["bullet"]))
    elems.append(Spacer(1, 4))
    return elems


def build_pdf(filename, title, policy_number, effective_date, sections_data):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = build_styles()
    story = []

    story += header_block(styles, policy_number, effective_date)
    story.append(Paragraph(title, styles["doc_title"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LGRAY))
    story.append(Spacer(1, 10))

    for sec in sections_data:
        num     = sec.get("num", "")
        stitle  = sec.get("title", "")
        paras   = sec.get("paragraphs", [])
        bullets = sec.get("bullets", [])
        subs    = sec.get("sub_sections", [])
        story += section(styles, num, stitle, paras, bullets, subs)

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LGRAY))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"© {UNIVERSITY_NAME} — {POLICY_OFFICE} | For questions contact: academicaffairs@westbrook.edu",
        styles["footer"],
    ))

    doc.build(story)
    print(f"  Generated: {filename}")


# ═══════════════════════════════════════════════════════════════════════════
#  DOCUMENT DEFINITIONS  (48 documents across 8 categories)
# ═══════════════════════════════════════════════════════════════════════════

DOCUMENTS = [

    # ── 1. GRADING POLICY ──────────────────────────────────────────────────

    {
        "filename": "grading_policy_undergraduate.pdf",
        "title": "Undergraduate Grading Policy",
        "policy_number": "ACAD-GRD-001",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose and Scope",
                "paragraphs": [
                    "This policy establishes the grading standards for all undergraduate courses at Westbrook University. It applies to all full-time and part-time undergraduate students enrolled in credit-bearing courses.",
                    "The grading system at Westbrook University is designed to accurately reflect each student's mastery of course material and to maintain the academic integrity of the institution's degrees.",
                ],
            },
            {
                "num": "2", "title": "Letter Grade Scale and Grade Points",
                "paragraphs": [
                    "The following letter grades and associated grade-point values are used at Westbrook University for all undergraduate coursework:",
                ],
                "bullets": [
                    "A  (4.0) — Excellent: Outstanding mastery of all course objectives",
                    "A- (3.7) — Excellent: Near-outstanding performance",
                    "B+ (3.3) — Good: Clearly above-average performance",
                    "B  (3.0) — Good: Average to above-average mastery",
                    "B- (2.7) — Good: Marginally above average",
                    "C+ (2.3) — Satisfactory: Meets most course objectives",
                    "C  (2.0) — Satisfactory: Meets minimum course requirements",
                    "C- (1.7) — Passing: Marginally meets requirements",
                    "D+ (1.3) — Minimal Pass: Below expectations but passing",
                    "D  (1.0) — Minimal Pass: Minimum passing grade",
                    "F  (0.0) — Failure: Does not meet course requirements",
                    "W  (—)  — Withdrawal: No grade-point impact (see Withdrawal Policy)",
                    "I  (—)  — Incomplete: Temporary grade (see Incomplete Grade Policy ACAD-GRD-005)",
                ],
            },
            {
                "num": "3", "title": "GPA Calculation",
                "paragraphs": [
                    "A student's Grade Point Average (GPA) is calculated by dividing the total quality points earned by the total number of credit hours attempted. Quality points are calculated by multiplying the grade-point value by the credit hours of each course.",
                    "Example: A student earning a B (3.0) in a 3-credit course earns 9 quality points. Cumulative GPA is recalculated at the end of every semester and reflected on the official transcript within 10 business days after grades are submitted.",
                    "Transfer credits accepted by the university do not affect the Westbrook GPA but are noted on the transcript separately.",
                ],
            },
            {
                "num": "4", "title": "Minimum Passing Requirements",
                "paragraphs": [
                    "A grade of D (1.0) or higher is considered a passing grade for general elective and free-elective courses. However, courses designated as core requirements, major requirements, or prerequisite courses require a minimum grade of C (2.0) to be considered successfully completed.",
                    "Students must maintain a cumulative GPA of 2.0 or higher to remain in good academic standing. Falling below this threshold triggers the Academic Warning and Probation procedures outlined in the Academic Standing Policy (ACAD-GRD-004).",
                ],
            },
            {
                "num": "5", "title": "Grade Submission Deadlines",
                "paragraphs": [
                    "Faculty must submit final grades no later than 72 hours after the scheduled final examination for each course. Grades submitted after this deadline are subject to review by the Academic Standards Committee.",
                    "Midterm grades for all 100- and 200-level courses are submitted at the mid-point of the semester and serve as advisory indicators for students at risk of course failure.",
                ],
            },
            {
                "num": "6", "title": "Grade Disputes",
                "paragraphs": [
                    "Students who believe a final grade is incorrect must first contact their instructor within 10 business days of grade posting. If unresolved, students may escalate to the department chair within an additional 10 business days. Further appeals follow the Grade Change Request Guidelines (ACAD-GRD-003).",
                ],
            },
            {
                "num": "7", "title": "Related Policies",
                "bullets": [
                    "ACAD-GRD-002 — GPA Appeals Procedure",
                    "ACAD-GRD-003 — Grade Change Request Guidelines",
                    "ACAD-GRD-004 — Academic Standing Policy",
                    "ACAD-GRD-005 — Incomplete Grade Policy",
                    "ACAD-GRD-006 — Pass/Fail Grading Option",
                ],
            },
        ],
    },

    {
        "filename": "gpa_appeals_procedure.pdf",
        "title": "GPA Appeals Procedure",
        "policy_number": "ACAD-GRD-002",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "This procedure provides a structured process for undergraduate students to formally appeal a GPA determination that they believe is the result of a calculation error, an improperly recorded grade, or exceptional extenuating circumstances.",
                ],
            },
            {
                "num": "2", "title": "Eligibility",
                "paragraphs": [
                    "A student is eligible to submit a GPA appeal if: (a) the student can demonstrate a mathematical error in grade computation; (b) a grade was recorded incorrectly due to administrative error; or (c) the student experienced extraordinary extenuating circumstances (e.g., documented medical emergency, death of an immediate family member) that prevented completion of coursework.",
                    "Appeals based solely on dissatisfaction with grades or instructor grading philosophy will not be considered.",
                ],
            },
            {
                "num": "3", "title": "Submission Timeline",
                "paragraphs": [
                    "GPA appeals must be submitted to the Office of Academic Affairs within 30 calendar days of the official grade posting for the semester in question. Late submissions will only be accepted in cases where the student can demonstrate they were unable to file due to the same extenuating circumstances cited in the appeal.",
                ],
            },
            {
                "num": "4", "title": "Appeal Process",
                "paragraphs": [
                    "Step 1: The student completes the GPA Appeal Form available through the Academic Affairs portal and attaches all relevant supporting documentation.",
                    "Step 2: The completed form is reviewed by the student's academic advisor within 5 business days to confirm eligibility.",
                    "Step 3: Eligible appeals are forwarded to the Academic Standards Committee, which convenes bi-weekly. The Committee reviews the appeal and issues a written decision within 15 business days.",
                    "Step 4: If the appeal is granted, the Registrar's Office updates the academic record within 5 business days. If denied, the student may escalate to the Dean of Academic Affairs within 10 business days.",
                ],
            },
            {
                "num": "5", "title": "Possible Outcomes",
                "bullets": [
                    "Grade correction applied and GPA recalculated",
                    "Retroactive Incomplete grade granted (subject to Incomplete Grade Policy)",
                    "Course withdrawal approved with no GPA impact",
                    "Appeal denied — original grade stands",
                ],
            },
            {
                "num": "6", "title": "Documentation Required",
                "bullets": [
                    "Completed GPA Appeal Form (Form AA-07)",
                    "Official grade report or transcript excerpt",
                    "Written statement explaining the grounds for appeal",
                    "Supporting documentation (medical records, official death certificate, etc.)",
                    "Instructor correspondence (if applicable)",
                ],
            },
        ],
    },

    {
        "filename": "grade_change_request_guidelines.pdf",
        "title": "Grade Change Request Guidelines",
        "policy_number": "ACAD-GRD-003",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "A grade change request is a formal mechanism through which a course instructor may correct or amend a final grade that has been officially recorded. This document outlines who may initiate a grade change, the permissible grounds, procedural steps, and applicable timelines.",
                ],
            },
            {
                "num": "2", "title": "Who May Initiate a Grade Change",
                "paragraphs": [
                    "Only the instructor of record for a course may initiate a grade change request. Students may not directly request a grade change; however, students may prompt an instructor to review a grade by submitting a grade dispute per the Undergraduate Grading Policy (ACAD-GRD-001, Section 6).",
                    "In cases where the original instructor is unavailable (e.g., has left the university), the Department Chair may initiate the change after a review of the course records.",
                ],
            },
            {
                "num": "3", "title": "Permissible Grounds for Grade Change",
                "bullets": [
                    "Clerical or computational error by the instructor",
                    "Grading a student's work against incorrect criteria",
                    "Completion of an Incomplete (I) grade within the approved timeframe",
                    "Resolution of an academic integrity investigation (grade may increase or decrease)",
                    "Court order or administrative directive",
                ],
            },
            {
                "num": "4", "title": "Timeline",
                "paragraphs": [
                    "Grade changes must be submitted within 60 calendar days of the end of the semester in which the course was offered. Changes requested after 60 days but within one academic year require Department Chair countersignature. Changes requested after one full academic year require countersignature from both the Department Chair and the Dean of Academic Affairs.",
                    "No grade changes are permitted more than three academic years after the original grade was recorded, except by extraordinary petition to the Provost.",
                ],
            },
            {
                "num": "5", "title": "Procedure",
                "paragraphs": [
                    "The instructor submits the Grade Change Request Form (Form REG-04) via the Faculty Portal. The form requires the original grade, the proposed new grade, and a written justification. The Registrar reviews the submission for completeness and forwards it to the appropriate approving authority based on timeline. Approved changes are reflected in the academic record within 3 business days.",
                ],
            },
        ],
    },

    {
        "filename": "academic_standing_policy.pdf",
        "title": "Academic Standing Policy",
        "policy_number": "ACAD-GRD-004",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "Westbrook University is committed to student success. This policy defines the criteria for academic standing categories and describes the support mechanisms and consequences associated with each standing level.",
                ],
            },
            {
                "num": "2", "title": "Academic Standing Categories",
                "paragraphs": ["Academic standing is evaluated at the end of each fall and spring semester based on the student's cumulative GPA:"],
                "bullets": [
                    "Good Standing: Cumulative GPA ≥ 2.0. Students in good standing may register for courses without restriction.",
                    "Academic Warning: Cumulative GPA 1.75–1.99. Students are notified by the Registrar and are strongly encouraged to meet with their academic advisor.",
                    "Academic Probation: Cumulative GPA below 1.75. Students are placed on probation and must complete a mandatory Academic Success Plan with their advisor within 2 weeks of semester end.",
                    "Academic Suspension: Second consecutive semester with GPA below 1.75 while on probation. Students are suspended for one full academic year and must apply for readmission.",
                    "Academic Dismissal: Students who return from suspension and again fall below a 1.75 GPA within two semesters are subject to academic dismissal from the university.",
                ],
            },
            {
                "num": "3", "title": "Notification",
                "paragraphs": [
                    "Students entering Academic Warning or Probation are notified via their official Westbrook University email address within 5 business days of final grade posting. Notifications are also sent to the student's academic advisor and, for students under 18, to the student's designated guardian.",
                ],
            },
            {
                "num": "4", "title": "Appeals",
                "paragraphs": [
                    "Students placed on Academic Suspension may appeal their standing by submitting a written petition to the Academic Standards Committee within 15 business days of the suspension notice. Appeals must include documentation of extenuating circumstances and an Academic Recovery Plan. See GPA Appeals Procedure (ACAD-GRD-002) for full appeal guidelines.",
                ],
            },
            {
                "num": "5", "title": "Re-enrollment After Suspension",
                "paragraphs": [
                    "Students returning after suspension must submit a Reinstatement Application to the Office of Admissions no later than 60 days before the start of the intended semester. Reinstatement is not automatic and requires approval by the Academic Standards Committee.",
                    "Reinstated students are placed on Probation for their first returning semester and must maintain a semester GPA of at least 2.0 to continue enrollment.",
                ],
            },
        ],
    },

    {
        "filename": "incomplete_grade_policy.pdf",
        "title": "Incomplete Grade Policy",
        "policy_number": "ACAD-GRD-005",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Definition",
                "paragraphs": [
                    "An Incomplete (I) grade is a temporary grade assigned when a student has completed the majority of coursework (at least 70%) with a passing grade, but has been prevented from completing remaining requirements due to documented extraordinary circumstances beyond the student's control.",
                    "An Incomplete is not appropriate for students who simply did not complete work or fell behind due to poor time management.",
                ],
            },
            {
                "num": "2", "title": "Eligibility Requirements",
                "bullets": [
                    "Student has completed at least 70% of course assignments and assessments",
                    "Student is passing the course based on work completed to date",
                    "Extraordinary circumstances (illness, family crisis, etc.) prevented completion of remaining work",
                    "Documentation of circumstances is available and verifiable",
                ],
            },
            {
                "num": "3", "title": "Requesting an Incomplete Grade",
                "paragraphs": [
                    "Students must submit an Incomplete Grade Request to the instructor before the last day of classes. The instructor and student jointly complete the Incomplete Grade Contract (Form AA-12), specifying the remaining work, the completion deadline, and the grade that will be assigned if the work is not completed.",
                    "Instructors are not obligated to grant an Incomplete and may decline if course circumstances do not permit it.",
                ],
            },
            {
                "num": "4", "title": "Completion Deadline",
                "paragraphs": [
                    "All incomplete work must be submitted to the instructor within 60 calendar days of the first day of the following regular semester (fall or spring). For spring Incompletes, the deadline falls during the summer.",
                    "If the remaining work is not submitted by the deadline, the Incomplete grade is automatically converted to the grade specified in the Incomplete Grade Contract (typically an F or the grade earned on completed work only).",
                ],
            },
            {
                "num": "5", "title": "Impact on Academic Standing",
                "paragraphs": [
                    "Incomplete grades are not calculated in the GPA until they are resolved. Students with outstanding Incomplete grades are not eligible for the Dean's List or Honors designations. More than two unresolved Incomplete grades in a single semester may trigger a review by the Academic Standards Committee.",
                ],
            },
        ],
    },

    {
        "filename": "pass_fail_option_policy.pdf",
        "title": "Pass/Fail Grading Option Policy",
        "policy_number": "ACAD-GRD-006",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "The Pass/Fail option allows undergraduate students to explore elective coursework outside their major without the risk of negatively impacting their GPA. This policy defines eligible courses, enrollment procedures, and grade conversion rules.",
                ],
            },
            {
                "num": "2", "title": "Eligibility",
                "paragraphs": [
                    "The Pass/Fail option is available to any undergraduate student in good academic standing (GPA ≥ 2.0) who has completed at least 30 credit hours. It may not be used for: courses fulfilling core requirements, major or minor requirements, prerequisite courses, or courses required by a student's college for graduation.",
                ],
            },
            {
                "num": "3", "title": "Limits",
                "bullets": [
                    "Maximum of 2 courses per semester on Pass/Fail",
                    "Maximum of 8 total courses in an undergraduate career on Pass/Fail",
                    "Students may not combine Pass/Fail and audit enrollment in the same semester (more than 2 combined)",
                ],
            },
            {
                "num": "4", "title": "Declaration Deadline and Grade Conversion",
                "paragraphs": [
                    "Students must declare the Pass/Fail option through the Registrar's Office by the end of the third week of the semester. After this deadline, no changes are permitted.",
                    "A grade of C (2.0) or higher converts to a Pass (P) on the transcript. A grade of C- (1.7) or lower converts to a Fail (F). Pass grades do not affect GPA calculations; Fail grades are counted as 0.0 quality points and are reflected in the GPA.",
                ],
            },
            {
                "num": "5", "title": "Disclosure to Graduate Schools",
                "paragraphs": [
                    "Students planning to apply to graduate or professional schools should be aware that many programs scrutinize Pass/Fail grades and may require letter grade equivalents. Students are strongly advised to consult with their academic advisor before electing this option.",
                ],
            },
        ],
    },

    # ── 2. ATTENDANCE POLICY ───────────────────────────────────────────────

    {
        "filename": "class_attendance_policy.pdf",
        "title": "Class Attendance Policy",
        "policy_number": "ACAD-ATT-001",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Policy Statement",
                "paragraphs": [
                    "Westbrook University regards regular class attendance as essential to the educational experience. Students are expected to attend every scheduled class meeting. Consistent attendance is strongly correlated with academic success and professional readiness.",
                ],
            },
            {
                "num": "2", "title": "Attendance Requirements",
                "paragraphs": [
                    "Students are permitted a maximum of 3 unexcused absences per semester in any single course. Exceeding this threshold carries the following academic consequences:",
                ],
                "bullets": [
                    "4 unexcused absences: The instructor may reduce the final course grade by one full letter grade (e.g., B to C).",
                    "5 unexcused absences: The instructor may reduce the final grade by two full letter grades.",
                    "6 or more unexcused absences: The instructor may assign a grade of F for the course, regardless of other performance.",
                ],
            },
            {
                "num": "3", "title": "Recording Attendance",
                "paragraphs": [
                    "Instructors are required to record attendance for every class session using the university's Learning Management System (LMS). Attendance records are made available to students and academic advisors in real time. Students are responsible for monitoring their own attendance status.",
                ],
            },
            {
                "num": "4", "title": "Excused Absences",
                "paragraphs": [
                    "Absences may be excused under the conditions described in the Excused Absence Guidelines (ACAD-ATT-002). The burden of providing documentation rests with the student. Instructors are not required to excuse absences for which no documentation is provided within 72 hours of the absence.",
                ],
            },
            {
                "num": "5", "title": "Late Arrivals and Early Departures",
                "paragraphs": [
                    "Students who arrive more than 10 minutes late to class or who leave class before the session ends without prior instructor permission will be marked as tardy. Three tardies in a single course are equivalent to one unexcused absence. See Tardiness Policy (ACAD-ATT-004) for details.",
                ],
            },
            {
                "num": "6", "title": "Online and Hybrid Courses",
                "paragraphs": [
                    "For fully online courses, attendance is measured through participation in required activities such as discussion boards, quizzes, and synchronous session logins. A student who does not complete any required activity during a given week is considered absent for that week.",
                ],
            },
        ],
    },

    {
        "filename": "excused_absence_guidelines.pdf",
        "title": "Excused Absence Guidelines",
        "policy_number": "ACAD-ATT-002",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "This document defines the circumstances under which an absence from class will be considered excused by Westbrook University and outlines the process for requesting an excused absence.",
                ],
            },
            {
                "num": "2", "title": "Approved Categories of Excused Absence",
                "paragraphs": ["The following circumstances constitute grounds for an excused absence:"],
                "sub_sections": [
                    ("2.1", "Medical Illness",
                     ["A student who is ill and unable to attend class must obtain documentation from a licensed healthcare provider. A doctor's note or clinic visit summary must be submitted to the instructor within 72 hours of the missed class."],
                     ["Note must include date of visit, treatment recommendation, and attestation that the student was seen",
                      "Self-reported illness without documentation is not considered excused"]),
                    ("2.2", "Family Emergency",
                     ["Absences due to the death of an immediate family member (parent, sibling, spouse, child, grandparent) or a serious medical emergency involving an immediate family member are excused. Students must notify the instructor as soon as possible and submit documentation (obituary, hospital admission record, etc.)."],
                     []),
                    ("2.3", "University-Sanctioned Activities",
                     ["Participation in university-sanctioned activities — including athletic competitions, academic conferences, field trips, and performing arts events — constitutes an excused absence when the activity is officially listed in the university calendar and the student provides the instructor with advance written notice at least 5 business days before the absence."],
                     []),
                    ("2.4", "Religious Observances",
                     ["Absences for the observance of religious holidays are excused. Students must notify instructors in writing at least 14 calendar days before the anticipated absence. See Religious Holiday Absence Policy (ACAD-ATT-006)."],
                     []),
                    ("2.5", "Jury Duty and Legal Obligations",
                     ["Students summoned for jury duty or required to appear in court must provide a copy of the court summons. The entire duration of jury service or court appearance is excused."],
                     []),
                    ("2.6", "Military Duty",
                     ["Students called to active military duty or training are excused for the full period of service. See Military Leave Policy (ACAD-WD-006)."],
                     []),
                ],
            },
            {
                "num": "3", "title": "Making Up Missed Work",
                "paragraphs": [
                    "Students with excused absences are entitled to make up missed examinations, quizzes, and assignments. It is the student's responsibility to contact the instructor within 48 hours of returning to campus to arrange make-up opportunities. Instructors must provide a reasonable opportunity to make up missed assessments within 5 business days.",
                ],
            },
        ],
    },

    {
        "filename": "remote_participation_policy.pdf",
        "title": "Remote Participation Policy",
        "policy_number": "ACAD-ATT-003",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "This policy governs the conditions under which a student may participate in a face-to-face course session remotely (via video conferencing) and still be counted as present.",
                ],
            },
            {
                "num": "2", "title": "Eligibility for Remote Participation",
                "paragraphs": [
                    "Remote participation is a privilege, not a right. It is available only when: (a) the student has a documented reason that prevents in-person attendance (illness, medical isolation order, travel for university business); (b) the instructor has pre-approved the remote arrangement in writing; and (c) the course structure is compatible with remote attendance (lectures, seminars — not lab or studio courses).",
                ],
            },
            {
                "num": "3", "title": "Advance Notice Requirement",
                "paragraphs": [
                    "Remote participation requests must be made at least 24 hours before the class session, except in cases of sudden illness, for which a same-day request with documentation may be accepted at the instructor's discretion. Requests submitted after the class has begun will not be granted.",
                ],
            },
            {
                "num": "4", "title": "Technical Requirements",
                "bullets": [
                    "Stable internet connection capable of video streaming",
                    "Functioning camera that must remain on throughout the session",
                    "Working microphone with the ability to participate in discussion",
                    "Quiet environment free from significant background noise",
                    "Use of Westbrook University's approved video conferencing platform (Zoom or Teams)",
                ],
            },
            {
                "num": "5", "title": "Attendance Credit",
                "paragraphs": [
                    "A student who participates remotely with prior approval and remains actively engaged throughout the session (camera on, responsive to questions) will be marked as present. Students who connect but do not participate actively, or whose connection is lost for more than 25% of the session, will be marked as absent.",
                ],
            },
            {
                "num": "6", "title": "Limitations",
                "paragraphs": [
                    "No student may attend more than 5 sessions of any single face-to-face course remotely in a given semester without obtaining a formal accommodation from the Office of Disability Services (ODS). Exceeding this limit without an ODS accommodation results in the absences being recorded as unexcused.",
                ],
            },
        ],
    },

    {
        "filename": "tardiness_policy.pdf",
        "title": "Tardiness and Early Departure Policy",
        "policy_number": "ACAD-ATT-004",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Definition of Tardiness",
                "paragraphs": [
                    "A student is considered tardy if they arrive to a class session more than 10 minutes after the scheduled start time. Students who arrive between 1 and 10 minutes late are considered late but not tardy for the purposes of this policy, though instructors may close doors or restrict entry at their discretion.",
                ],
            },
            {
                "num": "2", "title": "Early Departure",
                "paragraphs": [
                    "Leaving class before the session concludes without the prior permission of the instructor constitutes an early departure and is treated identically to a tardiness mark. Exceptions include genuine emergencies, for which the student must notify the instructor as soon as practicable.",
                ],
            },
            {
                "num": "3", "title": "Impact on Attendance",
                "paragraphs": [
                    "Three instances of tardiness or early departure (combined) in a single course are treated as one unexcused absence for the purposes of the Class Attendance Policy (ACAD-ATT-001). Instructors maintain discretion to impose stricter standards in professional program courses (nursing, education, business) where punctuality is a program learning outcome, provided these standards are clearly disclosed in the course syllabus.",
                ],
            },
            {
                "num": "4", "title": "Notification",
                "paragraphs": [
                    "When a student's tardy count reaches 2 in a semester, the instructor is required to send a written notification to the student and their academic advisor via the LMS attendance alert system.",
                ],
            },
        ],
    },

    {
        "filename": "attendance_appeals_procedure.pdf",
        "title": "Attendance Appeals Procedure",
        "policy_number": "ACAD-ATT-005",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "Students who believe an absence has been incorrectly recorded as unexcused, or who believe attendance-related grade penalties were applied in error, may file a formal attendance appeal using this procedure.",
                ],
            },
            {
                "num": "2", "title": "Grounds for Appeal",
                "bullets": [
                    "Absence was excused but incorrectly recorded as unexcused in the LMS",
                    "Documentation was submitted on time but not acknowledged by the instructor",
                    "Grade penalty applied despite absence being within the permitted threshold",
                    "Procedural error by instructor (e.g., failed to apply university policy correctly)",
                ],
            },
            {
                "num": "3", "title": "Filing a Formal Appeal",
                "paragraphs": [
                    "The student must submit an Attendance Appeal Form (Form AA-09) to the department's administrative coordinator within 5 business days of receiving written notice of the attendance-related action. The form must include a written narrative, all relevant documentation, and LMS screenshots if applicable.",
                    "A copy of the appeal is automatically forwarded to the instructor and the Department Chair.",
                ],
            },
            {
                "num": "4", "title": "Review Process and Timeline",
                "paragraphs": [
                    "The Department Chair reviews all submitted materials and issues a written determination within 10 business days. If the appeal is granted, the instructor is directed to correct the attendance record and recalculate the affected grade. If denied, the student may escalate to the Dean of Academic Affairs within 5 business days.",
                ],
            },
        ],
    },

    {
        "filename": "religious_holiday_absence_policy.pdf",
        "title": "Religious Holiday Absence Policy",
        "policy_number": "ACAD-ATT-006",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Policy Statement",
                "paragraphs": [
                    "Westbrook University is committed to supporting the religious and spiritual diversity of its student body. Students will not be penalized academically for absences required for the observance of a sincerely held religious belief or practice.",
                ],
            },
            {
                "num": "2", "title": "Advance Notice Requirement",
                "paragraphs": [
                    "Students must provide their instructor with written notice of anticipated religious holiday absences at least 14 calendar days before each anticipated absence. For religious holidays that occur at the very beginning of the semester, students must notify instructors on the first day of class.",
                    "Notice should be sent via the student's official Westbrook University email to their instructor and should include the date(s) of absence and the observance being honored.",
                ],
            },
            {
                "num": "3", "title": "Make-Up Work",
                "paragraphs": [
                    "Instructors must provide students observing religious holidays with a reasonable opportunity to make up any missed examinations or other required coursework. Make-up work must be of equivalent academic rigor to the original assignment. Instructors may not impose any additional requirements or burdens on students completing make-up work for religious observances.",
                    "Students are expected to complete make-up work within 1 week of returning from the absence unless an alternative timeline is negotiated with the instructor.",
                ],
            },
            {
                "num": "4", "title": "Instructor Responsibilities",
                "paragraphs": [
                    "Instructors who receive timely notice must acknowledge the request in writing within 3 business days. Instructors may not penalize students for religious absences in any way, including through attendance policies, participation grades, or informal bias. Non-compliance with this policy should be reported to the Office of Equal Opportunity and Diversity.",
                ],
            },
        ],
    },

    # ── 3. EXAM POLICY ────────────────────────────────────────────────────

    {
        "filename": "final_examination_policy.pdf",
        "title": "Final Examination Policy",
        "policy_number": "ACAD-EXM-001",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "Final examinations are a core component of academic assessment at Westbrook University. This policy governs scheduling, administration, and student obligations related to final exams.",
                ],
            },
            {
                "num": "2", "title": "Final Examination Week",
                "paragraphs": [
                    "Final examinations are held during the last full week of each fall and spring semester, as published in the official Academic Calendar. The exam schedule is released no later than 8 weeks before the start of final exam week.",
                    "No regularly scheduled class meetings may be held during final examination week unless the course's final assessment is a project presentation or performance that requires the full class to be present.",
                ],
            },
            {
                "num": "3", "title": "Duration and Format",
                "paragraphs": [
                    "Final examinations are scheduled for a duration of 2 hours and 50 minutes. Instructors may not schedule exams longer than the allotted time. Exams may be written, oral, practical, or take-home as designated in the course syllabus, provided students receive at least 4 weeks' advance notice of the format.",
                ],
            },
            {
                "num": "4", "title": "Attendance at Final Exams",
                "paragraphs": [
                    "Attendance at final examinations is mandatory. Students who are absent from a final exam without a documented excused reason will receive a grade of zero (0) for the exam. Students who miss a final exam due to an excused reason must request a make-up exam within 48 hours of the scheduled exam. See Makeup Exam Procedure (ACAD-EXM-002) for details.",
                ],
            },
            {
                "num": "5", "title": "Conflict Resolution",
                "paragraphs": [
                    "A student who has three or more final exams scheduled within a 24-hour period may request a conflict resolution accommodation. Requests must be submitted to the Registrar's Office no later than 3 weeks before final exam week using Form REG-12.",
                    "Students with two exams scheduled at the same time must also report the conflict to the Registrar's Office immediately. One of the two instructors will be directed to provide an alternative exam time.",
                ],
            },
            {
                "num": "6", "title": "Academic Integrity During Exams",
                "paragraphs": [
                    "All students must comply with the Academic Integrity Policy (ACAD-INT-001) during final examinations. Prohibited materials must be stored out of reach. Electronic devices, including mobile phones, smartwatches, and wireless earbuds, must be turned off and stored unless explicitly authorized by the instructor.",
                ],
            },
        ],
    },

    {
        "filename": "makeup_exam_procedure.pdf",
        "title": "Makeup Exam Procedure",
        "policy_number": "ACAD-EXM-002",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "This procedure establishes the process by which students may request and take a makeup examination for a missed midterm, quiz, or final exam. Makeup exams are granted only for excused absences as defined in the Excused Absence Guidelines (ACAD-ATT-002).",
                ],
            },
            {
                "num": "2", "title": "Requesting a Makeup Exam",
                "paragraphs": [
                    "Students must notify their instructor of the need for a makeup exam as early as possible, and no later than 48 hours after the originally scheduled exam time. Requests must be submitted via the student's official university email and must include the reason for absence and available supporting documentation.",
                    "For final examinations, requests must also be copied to the Department Chair and submitted using the Makeup Final Exam Request Form (Form AA-14).",
                ],
            },
            {
                "num": "3", "title": "Scheduling the Makeup Exam",
                "paragraphs": [
                    "Instructors must schedule the makeup examination within 5 business days of the student's return from the excused absence. For final exams, makeup exams must be administered no later than the grade submission deadline for the semester.",
                    "Makeup exams are administered in the department office, the Testing Center, or another proctored location. The instructor determines the format, which need not be identical to the original exam but must assess the same learning objectives.",
                ],
            },
            {
                "num": "4", "title": "Limitations",
                "bullets": [
                    "Students are entitled to one makeup opportunity per exam",
                    "Makeup exams are not available for unexcused absences",
                    "Students who miss a makeup exam without a new excused absence forfeit the right to a second makeup",
                    "Instructors may impose a reasonable late penalty (up to 10%) for unexcused late exam requests at their discretion",
                ],
            },
        ],
    },

    {
        "filename": "exam_proctoring_guidelines.pdf",
        "title": "Examination Proctoring Guidelines",
        "policy_number": "ACAD-EXM-003",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "These guidelines ensure that all examinations at Westbrook University are administered in a fair, secure, and consistent manner, preserving the integrity of academic assessments.",
                ],
            },
            {
                "num": "2", "title": "Proctor Qualifications",
                "paragraphs": [
                    "All examinations must be proctored by a qualified individual. Qualified proctors include: the course instructor, a teaching assistant approved by the department, a graduate student proctor certified by the Testing Center, or a professional staff member from the Testing Center.",
                    "Students may not serve as proctors for any examination, including those administered by student organizations.",
                ],
            },
            {
                "num": "3", "title": "Proctor Responsibilities",
                "bullets": [
                    "Verify student identity using a valid photo ID before distributing exam materials",
                    "Ensure no unauthorized materials are present at student workstations",
                    "Monitor the room continuously; proctors may not grade papers or use devices during the exam",
                    "Respond to student questions in a manner that does not provide an academic advantage",
                    "Document and report any observed academic integrity violations immediately",
                    "Collect all exam materials at the conclusion of the examination period",
                ],
            },
            {
                "num": "4", "title": "Online Proctoring",
                "paragraphs": [
                    "For online or remote examinations, the university uses approved proctoring software (currently Proctorio). Students must be informed of the software requirement at least 2 weeks before the exam. Students without adequate equipment may request Testing Center access. Proctoring recordings are retained for 90 days and may be reviewed in academic integrity investigations.",
                ],
            },
        ],
    },

    {
        "filename": "examination_accommodations_policy.pdf",
        "title": "Examination Accommodations Policy",
        "policy_number": "ACAD-EXM-004",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Policy Statement",
                "paragraphs": [
                    "Westbrook University is committed to providing equal access to academic assessments for all students. Students with documented disabilities may receive reasonable examination accommodations through the Office of Disability Services (ODS).",
                ],
            },
            {
                "num": "2", "title": "Registering with ODS",
                "paragraphs": [
                    "To receive accommodations, students must first register with ODS and submit documentation of their disability prepared by a qualified healthcare provider. ODS will evaluate the documentation and issue an Accommodation Letter specifying approved accommodations. Students are encouraged to register with ODS at the beginning of their first semester.",
                ],
            },
            {
                "num": "3", "title": "Common Exam Accommodations",
                "bullets": [
                    "Extended time (time-and-a-half or double time) for exams",
                    "Reduced-distraction testing environment",
                    "Use of a computer or assistive technology during written exams",
                    "Permission for breaks during extended exams",
                    "Oral examination in place of written format",
                    "Large-print or screen-reader-accessible exam materials",
                    "Scribe or dictation software for written responses",
                ],
            },
            {
                "num": "4", "title": "Student Responsibilities",
                "paragraphs": [
                    "Students must present their current semester Accommodation Letter to each instructor within the first 2 weeks of class. Accommodations are not retroactive — they apply only from the date the Accommodation Letter is received by the instructor.",
                    "Students who need to schedule an exam at the Testing Center with accommodations must submit a Testing Center Scheduling Form at least 5 business days before the exam.",
                ],
            },
            {
                "num": "5", "title": "Instructor Responsibilities",
                "paragraphs": [
                    "Instructors must honor all accommodations listed in valid ODS Accommodation Letters. Instructors who have concerns about a requested accommodation may consult with ODS but may not unilaterally deny an accommodation. Failure to provide approved accommodations may constitute a violation of the Americans with Disabilities Act.",
                ],
            },
        ],
    },

    {
        "filename": "exam_scheduling_conflict_policy.pdf",
        "title": "Exam Scheduling Conflict Policy",
        "policy_number": "ACAD-EXM-005",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Types of Scheduling Conflicts",
                "paragraphs": [
                    "An exam scheduling conflict occurs when a student has two or more exams scheduled at overlapping times, or when a student has three or more final exams scheduled within a 24-hour period. Both types of conflicts entitle the student to a resolution.",
                ],
            },
            {
                "num": "2", "title": "Resolving Simultaneous Exams",
                "paragraphs": [
                    "When two exams are scheduled at exactly the same time, the student must notify the Registrar's Office within 24 hours of discovering the conflict. The Registrar will contact both instructors and determine which exam will be rescheduled based on course enrollment, instructor flexibility, and availability of testing facilities.",
                    "The rescheduled exam must occur within 2 business days of the original exam time.",
                ],
            },
            {
                "num": "3", "title": "Three-Exams-in-One-Day Rule",
                "paragraphs": [
                    "Students with three or more final exams within any 24-hour period may request that one exam be rescheduled. The student must file a conflict form with the Registrar's Office no later than 3 weeks before the final exam period. The Registrar will coordinate with the relevant departments to reschedule the middle exam.",
                ],
            },
        ],
    },

    {
        "filename": "online_exam_policy.pdf",
        "title": "Online Examination Policy",
        "policy_number": "ACAD-EXM-006",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Scope",
                "paragraphs": [
                    "This policy applies to all examinations delivered through the university's Learning Management System (LMS) or other approved digital platforms, whether for online, hybrid, or face-to-face courses.",
                ],
            },
            {
                "num": "2", "title": "Technical Standards",
                "paragraphs": [
                    "Online exams must be built and administered using the university's approved LMS. Instructors must test all exam settings, including time limits, question randomization, and attempt limits, at least one week before the exam is administered. A test quiz must be available to students to verify browser compatibility.",
                ],
            },
            {
                "num": "3", "title": "Technical Difficulties",
                "paragraphs": [
                    "Students who experience a technical failure (internet outage, browser crash, LMS error) during an online exam must contact the IT Help Desk immediately and document the issue with a screenshot or error message. Students must also notify their instructor within 30 minutes of the disruption.",
                    "If the technical issue is verified by IT, the student will be provided with a rescheduled exam. Technical issues caused by student negligence (e.g., outdated browser, known outage in student's area) do not automatically qualify for a makeup.",
                ],
            },
            {
                "num": "4", "title": "Academic Integrity in Online Exams",
                "paragraphs": [
                    "All online exams are subject to the Academic Integrity Policy (ACAD-INT-001). Students may not use unauthorized resources, share questions with other students, or use any form of electronic assistance unless explicitly authorized. Suspected violations detected through LMS logs or proctoring tools will be referred to the Academic Integrity Office.",
                ],
            },
        ],
    },

    # ── 4. DISCIPLINARY POLICY ────────────────────────────────────────────

    {
        "filename": "student_code_of_conduct.pdf",
        "title": "Student Code of Conduct",
        "policy_number": "STUD-DIS-001",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Introduction",
                "paragraphs": [
                    "The Student Code of Conduct establishes the standards of behavior expected of all Westbrook University students, both on and off campus. Membership in the Westbrook community carries rights and responsibilities; this Code defines the boundaries of acceptable conduct to ensure a safe, inclusive, and academically rigorous environment.",
                ],
            },
            {
                "num": "2", "title": "Jurisdiction",
                "paragraphs": [
                    "This Code applies to all enrolled students, including part-time, online, and graduate students, and governs conduct: (a) on university property; (b) at university-sponsored events; (c) in university-owned online environments; and (d) off campus, when the conduct adversely affects the university community or its members.",
                ],
            },
            {
                "num": "3", "title": "Prohibited Conduct",
                "bullets": [
                    "Physical assault, battery, or threats of violence against any person",
                    "Sexual harassment, sexual assault, or non-consensual intimate conduct",
                    "Harassment, bullying, or discriminatory conduct based on protected characteristics",
                    "Theft, vandalism, or unauthorized use of university property",
                    "Academic dishonesty (see Academic Integrity Policy ACAD-INT-001)",
                    "Possession or use of illegal substances on campus",
                    "Unauthorized possession of weapons",
                    "Disruption of university operations, classes, or events",
                    "Providing false information to university officials",
                    "Retaliation against a person who has filed a complaint in good faith",
                ],
            },
            {
                "num": "4", "title": "Reporting Violations",
                "paragraphs": [
                    "Any member of the university community may report a suspected Code of Conduct violation by submitting a report to the Office of Student Affairs (studentconduct@westbrook.edu) or through the anonymous EthicsPoint reporting portal. Reports should include the nature of the alleged conduct, the parties involved, and any available evidence.",
                ],
            },
            {
                "num": "5", "title": "Investigation and Adjudication",
                "paragraphs": [
                    "Upon receiving a report, the Office of Student Affairs will conduct an initial review within 5 business days to determine if a formal investigation is warranted. Formal investigations are conducted by a trained conduct officer and follow the procedures described in the Disciplinary Procedures Policy (STUD-DIS-002).",
                ],
            },
        ],
    },

    {
        "filename": "disciplinary_procedures.pdf",
        "title": "Student Disciplinary Procedures",
        "policy_number": "STUD-DIS-002",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "This document describes the procedures followed when a student is alleged to have violated the Student Code of Conduct. These procedures are designed to be fair, thorough, and respectful of all parties' rights.",
                ],
            },
            {
                "num": "2", "title": "Notice of Allegation",
                "paragraphs": [
                    "Within 10 business days of initiating a formal investigation, the Office of Student Affairs will send a written Notice of Allegation to the accused student (the Respondent). The notice will include: the specific provision(s) of the Code alleged to have been violated, a summary of the factual basis for the allegation, the date and time of an initial meeting, and information about the student's rights.",
                ],
            },
            {
                "num": "3", "title": "Student Rights During Proceedings",
                "bullets": [
                    "Right to be presumed not responsible unless found responsible through the process",
                    "Right to review all evidence gathered during the investigation",
                    "Right to present a written statement and evidence on their behalf",
                    "Right to have a support person (advisor, friend, family member, or attorney in cases involving potential suspension or dismissal) present at any meeting",
                    "Right to appeal the outcome per the Appeals Process Guidelines (STUD-DIS-003)",
                ],
            },
            {
                "num": "4", "title": "Resolution Pathways",
                "paragraphs": [
                    "Minor violations may be resolved through an Administrative Resolution, an informal process between the student and a conduct officer. Cases involving potential suspension or dismissal proceed to a formal Student Conduct Hearing Board composed of 3 faculty and 2 student representatives.",
                    "All decisions are made using a Preponderance of Evidence standard — whether it is more likely than not that the student violated the Code.",
                ],
            },
            {
                "num": "5", "title": "Sanctions",
                "paragraphs": [
                    "If a student is found responsible, the conduct officer or Hearing Board may impose one or more sanctions as described in the Sanctions and Penalties Policy (STUD-DIS-004). Sanctions are designed to be educational and proportional to the severity of the violation.",
                ],
            },
        ],
    },

    {
        "filename": "disciplinary_appeals_guidelines.pdf",
        "title": "Disciplinary Appeals Process Guidelines",
        "policy_number": "STUD-DIS-003",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "This document describes the process by which a student found responsible for a Code of Conduct violation may appeal the finding and/or sanction.",
                ],
            },
            {
                "num": "2", "title": "Grounds for Appeal",
                "paragraphs": ["Appeals are only accepted on the following grounds:"],
                "bullets": [
                    "Procedural error that substantially affected the outcome of the hearing",
                    "New and material evidence unavailable at the time of the hearing",
                    "The sanction imposed is disproportionate to the severity of the violation",
                    "Bias or conflict of interest by a hearing board member",
                ],
            },
            {
                "num": "3", "title": "Filing Timeline",
                "paragraphs": [
                    "Appeals must be submitted in writing to the Dean of Students within 10 business days of receiving the written outcome letter. Late appeals will only be considered if the student can demonstrate that the delay was caused by circumstances beyond their control.",
                ],
            },
            {
                "num": "4", "title": "Appeals Review",
                "paragraphs": [
                    "The Dean of Students (or designee) reviews the appeal and the complete case file. The Dean may: affirm the original decision; modify the sanction; remand the case to a new hearing board; or overturn the finding. A written decision is issued within 20 business days.",
                    "The Dean's decision is final except in cases involving expulsion, which may be further appealed to the University Provost within 5 business days.",
                ],
            },
        ],
    },

    {
        "filename": "sanctions_and_penalties.pdf",
        "title": "Disciplinary Sanctions and Penalties",
        "policy_number": "STUD-DIS-004",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "When a student is found responsible for a Code of Conduct violation, one or more of the following sanctions may be imposed. Sanctions are cumulative and escalating for repeat violations.",
                ],
            },
            {
                "num": "2", "title": "Sanction Categories",
                "sub_sections": [
                    ("2.1", "Educational Sanctions",
                     ["Assigned for minor, first-time violations. Examples include written reflections, community service, completion of educational workshops, or formal written apology letters."],
                     []),
                    ("2.2", "Conduct Probation",
                     ["A formal status indicating that the student is at risk of suspension if any further violations occur. Conduct probation is typically issued for a defined period (one or two semesters). Probation status is reflected in internal student affairs records but is not noted on the academic transcript unless escalated."],
                     []),
                    ("2.3", "Suspension",
                     ["Temporary separation from the university for a specified period (minimum one semester, maximum two academic years). Suspended students may not access campus facilities, attend classes, or participate in university activities. Suspension is noted on the academic transcript during the period of suspension."],
                     []),
                    ("2.4", "Expulsion",
                     ["Permanent separation from the university. Expulsion is reserved for the most severe violations (e.g., sexual assault, violent crimes, egregious academic dishonesty with institutional impact). Expulsion is permanently noted on the academic transcript."],
                     []),
                ],
            },
        ],
    },

    {
        "filename": "behavioral_intervention_policy.pdf",
        "title": "Behavioral Intervention Policy",
        "policy_number": "STUD-DIS-005",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "This policy establishes the Behavioral Intervention Team (BIT) and defines its role in supporting students who demonstrate concerning behaviors that may pose a risk to themselves or others, without necessarily rising to the level of a formal Code of Conduct violation.",
                ],
            },
            {
                "num": "2", "title": "BIT Composition and Responsibilities",
                "paragraphs": [
                    "The BIT is a multidisciplinary team comprising the Dean of Students (chair), the Director of Counseling Services, the Director of Campus Safety, and at least two faculty or staff representatives. The BIT meets weekly to review referrals and coordinate interventions.",
                ],
            },
            {
                "num": "3", "title": "Referral Process",
                "paragraphs": [
                    "Any member of the university community — student, faculty, or staff — may submit a referral to the BIT through the online CARE Report form. Referrals may concern behaviors including: concerning social media posts, expressions of hopelessness, sudden changes in behavior, threats, or self-isolation.",
                    "Referrals are not disciplinary actions. They are supportive in nature and aim to connect the student with appropriate resources.",
                ],
            },
        ],
    },

    {
        "filename": "campus_safety_regulations.pdf",
        "title": "Campus Safety Regulations",
        "policy_number": "STUD-DIS-006",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "These regulations establish safety standards for all individuals on the Westbrook University campus to ensure a safe and secure environment for study, work, and community life.",
                ],
            },
            {
                "num": "2", "title": "Weapons Policy",
                "paragraphs": [
                    "No weapons of any kind — including firearms, knives with blades longer than 3 inches, explosives, or any device intended to cause bodily harm — are permitted on university property. This applies regardless of whether the individual holds a concealed carry permit. Violations are grounds for immediate removal from campus and referral to law enforcement.",
                ],
            },
            {
                "num": "3", "title": "Substance Policies",
                "paragraphs": [
                    "The use, possession, or distribution of controlled substances in violation of federal or state law is prohibited on campus. Alcohol consumption is permitted only in licensed, designated areas and only by individuals of legal age. The university enforces a strict non-smoking policy within 25 feet of any building entrance.",
                ],
            },
            {
                "num": "4", "title": "Emergency Procedures",
                "paragraphs": [
                    "All students and employees are expected to familiarize themselves with emergency evacuation routes posted in each building. In the event of a campus emergency, the university will issue alerts through the WestBrook Alert System (SMS, email, and digital signage). Students must comply with all instructions from Campus Safety officers and local law enforcement during emergencies.",
                ],
            },
        ],
    },

    # ── 5. ACADEMIC INTEGRITY ─────────────────────────────────────────────

    {
        "filename": "academic_honesty_policy.pdf",
        "title": "Academic Integrity and Honesty Policy",
        "policy_number": "ACAD-INT-001",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Commitment to Academic Integrity",
                "paragraphs": [
                    "Academic integrity is a cornerstone of the Westbrook University academic experience. Students, faculty, and staff are expected to maintain the highest standards of scholarly honesty. Violations of academic integrity undermine the value of the degrees conferred by this institution and harm all members of the academic community.",
                ],
            },
            {
                "num": "2", "title": "Definitions of Academic Dishonesty",
                "sub_sections": [
                    ("2.1", "Plagiarism",
                     ["Presenting another person's words, ideas, data, or creative work as one's own without proper citation. This includes copying text from sources, paraphrasing without attribution, and submitting purchased or AI-generated text without disclosure. See Plagiarism Policy (ACAD-INT-002) for detailed definitions."],
                     []),
                    ("2.2", "Cheating",
                     ["Using unauthorized materials or assistance during an exam or assignment. This includes bringing notes to a closed-book exam, using a cell phone during an assessment, copying from another student's work, and unauthorized collaboration."],
                     []),
                    ("2.3", "Fabrication",
                     ["Inventing or falsifying data, research results, citations, or other information submitted for academic evaluation."],
                     []),
                    ("2.4", "Facilitation of Dishonesty",
                     ["Helping another student commit academic dishonesty, including sharing exam questions, providing answers, or allowing a student to copy one's work."],
                     []),
                ],
            },
            {
                "num": "3", "title": "Consequences",
                "paragraphs": [
                    "Students found responsible for academic dishonesty face consequences proportional to the severity of the violation. Minimum consequences include a zero on the affected assignment. More serious or repeated violations may result in course failure (grade of F) or referral to the Office of Student Affairs for disciplinary action, which may include suspension or expulsion. See Academic Integrity Consequences section in ACAD-INT-002.",
                ],
            },
            {
                "num": "4", "title": "Reporting",
                "paragraphs": [
                    "Instructors who suspect academic dishonesty must report the incident to the Academic Integrity Office within 5 business days of discovery using the Academic Integrity Incident Report Form (Form AI-01). Instructors may not impose grade-based penalties without first following this reporting procedure.",
                ],
            },
        ],
    },

    {
        "filename": "plagiarism_policy.pdf",
        "title": "Plagiarism Detection and Consequences Policy",
        "policy_number": "ACAD-INT-002",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Definition of Plagiarism",
                "paragraphs": [
                    "Plagiarism at Westbrook University includes, but is not limited to: verbatim copying of text without quotation marks and citation; paraphrasing another's ideas without attribution; presenting another student's submitted work as one's own; and submitting text generated by artificial intelligence tools without instructor authorization and disclosure.",
                ],
            },
            {
                "num": "2", "title": "Detection Methods",
                "paragraphs": [
                    "All written submissions in courses using the university LMS are automatically scanned by Turnitin, the university's plagiarism detection platform. Turnitin generates a similarity report that instructors review. A high similarity score triggers an instructor review but does not automatically constitute a finding of plagiarism — proper citation of sources is expected and similarity from quotations is normal.",
                    "Instructors may also use manual review, database searches, and source verification when they suspect plagiarism.",
                ],
            },
            {
                "num": "3", "title": "Consequences by Severity",
                "sub_sections": [
                    ("3.1", "Minor Plagiarism (first offense, unintentional)",
                     ["Grade of zero on the affected assignment, required plagiarism education workshop, and a formal written warning placed in the student's academic integrity file."],
                     []),
                    ("3.2", "Significant Plagiarism (substantial portion of assignment or intentional)",
                     ["Automatic F for the course, academic integrity file notation, and referral to the Academic Integrity Office for further review."],
                     []),
                    ("3.3", "Aggravated Plagiarism (thesis, capstone, or repeated offense)",
                     ["Academic suspension for at least one semester, permanent academic integrity file notation, and potential academic dismissal. Degree conferral may be withheld pending investigation."],
                     []),
                ],
            },
            {
                "num": "4", "title": "Student Rights in Plagiarism Cases",
                "paragraphs": [
                    "Before any sanction is finalized, students are given written notice of the allegation and an opportunity to respond. Students may contest a plagiarism finding through the Academic Integrity Office's review process. Appeals are governed by ACAD-INT-001 and the Disciplinary Appeals Guidelines (STUD-DIS-003).",
                ],
            },
        ],
    },

    {
        "filename": "cheating_exam_fraud_policy.pdf",
        "title": "Cheating and Examination Fraud Policy",
        "policy_number": "ACAD-INT-003",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Prohibited Exam Behaviors",
                "bullets": [
                    "Looking at another student's exam paper without permission",
                    "Communicating with other students during an exam (verbally, via text, or any other means)",
                    "Using any notes, textbooks, or electronic devices not explicitly permitted by the instructor",
                    "Having another person take an exam on one's behalf (contract cheating)",
                    "Removing exam materials from the examination room without authorization",
                    "Altering a graded exam before requesting a regrade",
                ],
            },
            {
                "num": "2", "title": "Exam Fraud and Contract Cheating",
                "paragraphs": [
                    "Contract cheating — paying or arranging for another person to complete academic work — is among the most severe violations of academic integrity. Students found to have engaged in contract cheating face immediate course failure and referral to the Academic Integrity Board, which may impose suspension or expulsion.",
                ],
            },
            {
                "num": "3", "title": "Consequences",
                "paragraphs": [
                    "First-time cheating offense: zero on the exam, mandatory academic integrity workshop, written warning. Second offense: automatic F in the course, placed on Academic Integrity Probation. Third or serious offense: suspension or expulsion, permanent notation on transcript.",
                ],
            },
        ],
    },

    {
        "filename": "ai_usage_academic_policy.pdf",
        "title": "Artificial Intelligence Usage in Academic Work Policy",
        "policy_number": "ACAD-INT-004",
        "effective_date": "January 1, 2025",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "Generative artificial intelligence tools (such as ChatGPT, Claude, Gemini, and similar) are increasingly available to students. This policy establishes how students may and may not use these tools in academic work to preserve learning integrity while acknowledging the evolving technological landscape.",
                ],
            },
            {
                "num": "2", "title": "Default Position",
                "paragraphs": [
                    "Unless explicitly permitted by the instructor in writing, the use of generative AI tools to produce, draft, or substantially revise academic submissions is prohibited. Submitting AI-generated text as one's own work constitutes academic dishonesty equivalent to plagiarism under ACAD-INT-001.",
                ],
            },
            {
                "num": "3", "title": "Permitted Uses (When Authorized by Instructor)",
                "bullets": [
                    "Using AI tools for brainstorming or generating outlines (disclosed in the submission)",
                    "Using AI-powered grammar and spell-check tools (Grammarly, etc.) — always permitted",
                    "Using AI to summarize research sources as a starting point — disclosure required",
                    "AI-generated code used as a starting framework in programming courses — disclosure required",
                ],
            },
            {
                "num": "4", "title": "Disclosure Requirement",
                "paragraphs": [
                    "In any course where the instructor has authorized AI use, students must include an AI Use Disclosure statement at the end of their submission describing which tool was used and how it contributed to the work. Failure to disclose authorized AI use still constitutes academic dishonesty.",
                ],
            },
            {
                "num": "5", "title": "Instructor Responsibilities",
                "paragraphs": [
                    "Instructors must clearly state in their course syllabus and assignment instructions whether AI use is prohibited, permitted with disclosure, or freely permitted for each assignment. Ambiguous or absent AI use policies default to 'prohibited.'",
                ],
            },
        ],
    },

    {
        "filename": "citation_attribution_guidelines.pdf",
        "title": "Citation and Attribution Guidelines",
        "policy_number": "ACAD-INT-005",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "Proper citation and attribution of sources is fundamental to academic writing. These guidelines describe when and how students must cite sources to avoid plagiarism.",
                ],
            },
            {
                "num": "2", "title": "When to Cite",
                "bullets": [
                    "Any direct quotation from a source, even a single phrase",
                    "Any paraphrase or summary of another's idea, argument, or finding",
                    "Data, statistics, charts, or images from external sources",
                    "Theories, models, or frameworks developed by a named scholar",
                    "Course materials, textbooks, and lecture notes",
                ],
            },
            {
                "num": "3", "title": "Accepted Citation Styles",
                "paragraphs": [
                    "Students should use the citation style required by their discipline and instructor. Approved styles at Westbrook include: APA (7th edition) for social sciences, education, and nursing; MLA (9th edition) for humanities; Chicago (17th edition) for history and arts; ACS for chemistry; IEEE for engineering.",
                ],
            },
            {
                "num": "4", "title": "Common Knowledge Exception",
                "paragraphs": [
                    "Facts that are widely known and not attributable to a specific source (e.g., 'The Earth orbits the Sun') do not require citation. When in doubt, cite. Consulting a subject librarian or the Writing Center is encouraged.",
                ],
            },
        ],
    },

    {
        "filename": "research_integrity_policy.pdf",
        "title": "Research Integrity Policy",
        "policy_number": "ACAD-INT-006",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Commitment to Research Integrity",
                "paragraphs": [
                    "Westbrook University upholds the highest standards of integrity in research conducted by its students, faculty, and staff. Research integrity encompasses honest reporting, transparent methodology, proper attribution, and ethical treatment of human and animal subjects.",
                ],
            },
            {
                "num": "2", "title": "Research Misconduct Defined",
                "bullets": [
                    "Fabrication: Making up data or results and recording or reporting them",
                    "Falsification: Manipulating materials, equipment, or processes to alter results",
                    "Plagiarism: Misappropriating another researcher's ideas, data, or writings",
                    "Failure to disclose conflicts of interest in funded research",
                    "Violation of Institutional Review Board (IRB) protocols for human subjects research",
                ],
            },
            {
                "num": "3", "title": "Reporting Research Misconduct",
                "paragraphs": [
                    "Suspected research misconduct should be reported to the Office of Research Integrity (ORI). Reports may be submitted anonymously. The ORI will conduct a preliminary inquiry within 30 days to determine whether a full investigation is warranted.",
                ],
            },
        ],
    },

    # ── 6. FINANCIAL AID POLICY ───────────────────────────────────────────

    {
        "filename": "financial_aid_eligibility.pdf",
        "title": "Financial Aid Eligibility Requirements",
        "policy_number": "FIN-AID-001",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "Westbrook University administers federal, state, and institutional financial aid programs to help students finance their education. This document outlines the eligibility requirements students must meet to receive and maintain financial aid.",
                ],
            },
            {
                "num": "2", "title": "General Eligibility Requirements",
                "bullets": [
                    "U.S. citizenship or eligible non-citizen status for federal aid programs",
                    "Enrolled at least half-time (6 credit hours) in an eligible degree program",
                    "Maintaining Satisfactory Academic Progress (see FIN-AID-004)",
                    "Valid Social Security Number (for FAFSA-based aid)",
                    "Not in default on any federal student loan",
                    "Completion of the Free Application for Federal Student Aid (FAFSA) by the Westbrook priority deadline of February 15 each academic year",
                ],
            },
            {
                "num": "3", "title": "Types of Aid Available",
                "sub_sections": [
                    ("3.1", "Grants",
                     ["Grants are need-based awards that do not require repayment. Federal Pell Grants are available to undergraduates with demonstrated financial need. The Westbrook University Need-Based Grant supplements Pell Grants for eligible students."],
                     []),
                    ("3.2", "Scholarships",
                     ["Merit and need-based scholarships are available from institutional and external sources. See Scholarship Application Procedure (FIN-AID-002) for application details and deadlines."],
                     []),
                    ("3.3", "Federal Loans",
                     ["Subsidized and unsubsidized Direct Loans are available to eligible students. Graduate students may also access Direct PLUS Loans. See Student Loan Guidelines (FIN-AID-003) for full terms and conditions."],
                     []),
                    ("3.4", "Work-Study",
                     ["Federal Work-Study provides part-time employment opportunities for eligible students with financial need. See Work-Study Program Policy (FIN-AID-006)."],
                     []),
                ],
            },
            {
                "num": "4", "title": "Annual Renewal",
                "paragraphs": [
                    "Financial aid is not automatically renewed each year. Students must submit a new FAFSA each academic year by the February 15 priority deadline to maintain eligibility for need-based aid. Scholarship renewals require students to meet specific GPA and credit-hour requirements detailed in the original award letter.",
                ],
            },
        ],
    },

    {
        "filename": "scholarship_application_procedure.pdf",
        "title": "Scholarship Application Procedure",
        "policy_number": "FIN-AID-002",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Scholarship Overview",
                "paragraphs": [
                    "Westbrook University offers a wide range of institutional scholarships recognizing academic merit, community service, leadership, and financial need. This document describes the application process for university-administered scholarships.",
                ],
            },
            {
                "num": "2", "title": "Application Deadlines",
                "bullets": [
                    "Presidential Scholarship (full tuition): November 1 for incoming freshmen",
                    "Dean's Merit Scholarship (50% tuition): December 15 for incoming freshmen",
                    "Westbrook Community Leadership Award: February 1 (all eligible students)",
                    "Departmental Scholarships: Vary by department; check the scholarship portal",
                    "Renewal applications for continuing students: April 30 each year",
                ],
            },
            {
                "num": "3", "title": "Application Requirements",
                "paragraphs": [
                    "All scholarship applications are submitted through the Westbrook Scholarship Portal (scholarships.westbrook.edu). Standard requirements include: completed application form, official transcripts, two letters of recommendation, a personal statement (500–800 words), and documentation of community service or extracurricular activities.",
                    "Some scholarships require additional materials such as creative portfolios, research proposals, or departmental nominations.",
                ],
            },
            {
                "num": "4", "title": "Selection Criteria",
                "paragraphs": [
                    "Scholarship committees evaluate applications based on the specific criteria outlined in each award description. Common criteria include: cumulative GPA (typically 3.0 or higher for merit awards), quality of personal statement, demonstrated leadership, financial need (for need-based awards), and strength of recommendation letters.",
                ],
            },
            {
                "num": "5", "title": "Renewal Requirements",
                "paragraphs": [
                    "Most institutional scholarships require renewal each year. Standard renewal criteria include maintaining a minimum GPA (2.5–3.5 depending on the award), completing a minimum of 30 credit hours per academic year, and remaining enrolled full-time. Students falling below renewal thresholds may appeal through the Financial Aid Appeals Process (FIN-AID-005).",
                ],
            },
        ],
    },

    {
        "filename": "student_loan_guidelines.pdf",
        "title": "Student Loan Guidelines",
        "policy_number": "FIN-AID-003",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Types of Federal Student Loans",
                "paragraphs": [
                    "Westbrook University participates in the William D. Ford Federal Direct Loan Program. The following loan types are available:",
                ],
                "bullets": [
                    "Direct Subsidized Loans: Available to undergraduates with demonstrated financial need. The federal government pays interest while the student is enrolled at least half-time.",
                    "Direct Unsubsidized Loans: Available to undergraduates and graduate students regardless of financial need. Interest accrues from disbursement.",
                    "Direct PLUS Loans: Available to graduate students and parents of dependent undergraduates. Credit check required.",
                ],
            },
            {
                "num": "2", "title": "Loan Limits",
                "paragraphs": [
                    "Annual loan limits depend on year in school and dependency status. Freshmen may borrow up to $5,500 (dependent) or $9,500 (independent) in subsidized and unsubsidized combined. Aggregate limits are $31,000 for dependent undergraduates and $57,500 for independent undergraduates.",
                ],
            },
            {
                "num": "3", "title": "Entrance and Exit Counseling",
                "paragraphs": [
                    "First-time federal loan borrowers at Westbrook must complete online Entrance Counseling and sign a Master Promissory Note (MPN) before funds are disbursed. Students who graduate, withdraw, or drop below half-time enrollment must complete Exit Counseling within 30 days to understand repayment obligations.",
                ],
            },
            {
                "num": "4", "title": "Repayment",
                "paragraphs": [
                    "Repayment begins 6 months after the student graduates, leaves school, or drops below half-time enrollment. Standard repayment plans span 10 years. Income-Driven Repayment plans are available through the federal student aid portal (studentaid.gov).",
                ],
            },
        ],
    },

    {
        "filename": "satisfactory_academic_progress_aid.pdf",
        "title": "Satisfactory Academic Progress Policy for Financial Aid",
        "policy_number": "FIN-AID-004",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "Federal regulations (34 CFR 668.34) require that students receiving financial aid make Satisfactory Academic Progress (SAP) toward their degree. Westbrook University evaluates SAP at the end of each fall and spring semester.",
                ],
            },
            {
                "num": "2", "title": "SAP Standards",
                "sub_sections": [
                    ("2.1", "Qualitative Standard (GPA)",
                     ["Undergraduate students must maintain a cumulative GPA of at least 2.0. Graduate students must maintain a cumulative GPA of at least 3.0."],
                     []),
                    ("2.2", "Quantitative Standard (Pace)",
                     ["Students must successfully complete at least 67% of all credit hours attempted. Incomplete grades, withdrawals, and failures count as attempted but not completed."],
                     []),
                    ("2.3", "Maximum Time Frame",
                     ["Students may not receive aid for more than 150% of the published length of their degree program. For a 120-credit bachelor's degree, the maximum is 180 attempted credit hours."],
                     []),
                ],
            },
            {
                "num": "3", "title": "Consequences of Failing SAP",
                "paragraphs": [
                    "Students who fail to meet SAP standards are placed on Financial Aid Warning for one semester, during which aid continues. If SAP standards are not met by the end of the Warning semester, the student is placed on Financial Aid Suspension and aid is discontinued.",
                ],
            },
            {
                "num": "4", "title": "SAP Appeal",
                "paragraphs": [
                    "Students on Financial Aid Suspension may appeal by submitting a SAP Appeal Form to the Financial Aid Office with documentation of extenuating circumstances (injury, illness, family emergency) and an Academic Plan signed by their advisor. See Financial Aid Appeals (FIN-AID-005).",
                ],
            },
        ],
    },

    {
        "filename": "financial_aid_appeals.pdf",
        "title": "Financial Aid Appeals Process",
        "policy_number": "FIN-AID-005",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "This document describes the process by which students may appeal a financial aid suspension, scholarship revocation, or financial aid eligibility determination.",
                ],
            },
            {
                "num": "2", "title": "Grounds for Appeal",
                "bullets": [
                    "Serious illness or injury of the student during the affected semester",
                    "Death or medical crisis of an immediate family member",
                    "Involuntary call to active military duty",
                    "Natural disaster or other circumstances beyond the student's control",
                    "Documented disability not previously accommodated",
                ],
            },
            {
                "num": "3", "title": "Appeal Submission",
                "paragraphs": [
                    "Appeals must be submitted to the Financial Aid Office within 30 days of the suspension or adverse determination. Required documentation includes: completed SAP Appeal Form, personal written statement, supporting documentation, and an Academic Plan signed by the student's academic advisor.",
                ],
            },
            {
                "num": "4", "title": "Review and Outcome",
                "paragraphs": [
                    "The Financial Aid Appeals Committee reviews appeals within 15 business days. If approved, the student is placed on Financial Aid Probation with specific performance benchmarks (e.g., achieve a 2.5 GPA next semester). If the appeal is denied, the student may re-apply for aid in a subsequent semester after self-financing enrollment and restoring SAP compliance.",
                ],
            },
        ],
    },

    {
        "filename": "work_study_program_policy.pdf",
        "title": "Federal Work-Study Program Policy",
        "policy_number": "FIN-AID-006",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Program Overview",
                "paragraphs": [
                    "The Federal Work-Study (FWS) program provides part-time employment to undergraduate and graduate students who demonstrate financial need, allowing them to earn money to help pay for educational expenses.",
                ],
            },
            {
                "num": "2", "title": "Eligibility",
                "paragraphs": [
                    "Students must have a demonstrated financial need as calculated by the FAFSA, be enrolled at least half-time, and be maintaining SAP. Work-Study awards are made as part of the financial aid package.",
                ],
            },
            {
                "num": "3", "title": "Work Hours and Earnings",
                "paragraphs": [
                    "Students may work a maximum of 20 hours per week during the academic semester. Work-Study wages are paid bi-weekly directly to the student and are not credited to the student's account. Earnings are subject to federal and state income tax. Students must not exceed their Work-Study award amount during an academic year.",
                ],
            },
            {
                "num": "4", "title": "Job Placement",
                "paragraphs": [
                    "Available Work-Study positions are posted on the university's student employment portal. Students apply directly for positions and are hired by the employing department. Positions are available both on campus and with approved off-campus non-profit community service organizations.",
                ],
            },
        ],
    },

    # ── 7. PREREQUISITES & REQUIREMENTS ──────────────────────────────────

    {
        "filename": "core_curriculum_requirements.pdf",
        "title": "Core Curriculum Requirements",
        "policy_number": "ACAD-REQ-001",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "The Westbrook University Core Curriculum ensures that all undergraduate students develop a foundation of knowledge and skills across multiple disciplines. Regardless of major, all students must fulfill the following core requirements for graduation.",
                ],
            },
            {
                "num": "2", "title": "Core Requirement Areas",
                "sub_sections": [
                    ("2.1", "Written Communication (6 credits)",
                     ["Students must complete ENGL 101 (College Writing I) and ENGL 102 (College Writing II) or approved equivalents. A grade of C or higher is required in both courses."],
                     []),
                    ("2.2", "Quantitative Reasoning (3–6 credits)",
                     ["One mathematics course at or above MATH 130 (Pre-Calculus). STEM majors must complete MATH 151 (Calculus I) as part of this requirement."],
                     []),
                    ("2.3", "Natural Sciences (7 credits)",
                     ["Two science courses with laboratory components from different disciplines (e.g., Biology, Chemistry, Physics, Environmental Science)."],
                     []),
                    ("2.4", "Social Sciences (6 credits)",
                     ["Two courses from the social sciences (Economics, Political Science, Psychology, Sociology, Anthropology)."],
                     []),
                    ("2.5", "Humanities and Arts (6 credits)",
                     ["Two courses from the humanities or creative arts. At least one must be a writing-intensive course."],
                     []),
                    ("2.6", "Diversity and Global Studies (3 credits)",
                     ["One course with a diversity, equity, and inclusion or global studies designation."],
                     []),
                    ("2.7", "First-Year Seminar (1 credit)",
                     ["UNIV 101 (First-Year Experience Seminar) required for all entering freshmen."],
                     []),
                ],
            },
            {
                "num": "3", "title": "Transfer Credit and Core Requirements",
                "paragraphs": [
                    "Transfer students who have completed equivalent courses at an accredited institution may petition for core requirement waivers. A Transfer Credit Evaluation is conducted by the Registrar's Office within 30 days of admission. See Transfer Credit Policy (ACAD-REQ-004).",
                ],
            },
        ],
    },

    {
        "filename": "prerequisite_waiver_procedure.pdf",
        "title": "Prerequisite Waiver Procedure",
        "policy_number": "ACAD-REQ-002",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "Prerequisites ensure that students have the foundational knowledge required to succeed in advanced courses. In exceptional cases, a student may request a waiver of a course prerequisite if they can demonstrate equivalent knowledge through prior coursework, professional experience, or standardized assessment.",
                ],
            },
            {
                "num": "2", "title": "Eligibility",
                "paragraphs": [
                    "A student may request a prerequisite waiver if: (a) they have completed equivalent coursework at another institution; (b) they have professional experience that demonstrates mastery of prerequisite material; or (c) they have passed a departmentally administered placement exam at the required level.",
                ],
            },
            {
                "num": "3", "title": "Waiver Process",
                "paragraphs": [
                    "Step 1: The student meets with the instructor of the course for which the prerequisite is being waived. The instructor reviews the student's evidence and provides a written recommendation.",
                    "Step 2: The student submits the Prerequisite Waiver Request Form (Form REG-06) to the Department Chair, attaching the instructor's recommendation and all supporting documentation.",
                    "Step 3: The Department Chair approves or denies the request within 5 business days. Approved waivers are entered in the student's academic record by the Registrar.",
                ],
            },
            {
                "num": "4", "title": "Important Notes",
                "bullets": [
                    "Waiving a prerequisite does not waive the credit-hour requirement for the prerequisite course",
                    "Waivers are specific to one semester and one course section",
                    "Denial of a waiver may be appealed to the Dean of the relevant college within 5 business days",
                ],
            },
        ],
    },

    {
        "filename": "elective_course_guidelines.pdf",
        "title": "Elective Course Guidelines",
        "policy_number": "ACAD-REQ-003",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Types of Electives",
                "paragraphs": [
                    "Westbrook University degree programs include two categories of elective credits: (a) Restricted Electives — courses chosen from a defined list related to the student's major; and (b) Free Electives — any credit-bearing courses that fulfill remaining credit-hour requirements for graduation.",
                ],
            },
            {
                "num": "2", "title": "Minimum Requirements",
                "paragraphs": [
                    "All undergraduate degree programs require a minimum of 120 credit hours for graduation. Typically, 30–45 credit hours are designated as free or restricted electives, depending on the major. Students are encouraged to use elective credits to pursue a minor, certificate, or areas of personal interest.",
                ],
            },
            {
                "num": "3", "title": "Choosing Electives Strategically",
                "paragraphs": [
                    "Students are advised to use elective slots for courses that complement career goals, fulfill minor requirements, or enable double-major completion. Academic advisors can assist with multi-semester elective planning. Elective courses outside the major may fulfill Core Curriculum requirements if properly designated.",
                ],
            },
            {
                "num": "4", "title": "Restrictions",
                "bullets": [
                    "No more than 30 credit hours from a single department may count toward free elective credit",
                    "Remedial or developmental courses (below 100-level) do not count toward graduation credit",
                    "Courses in which a student has received an F may be repeated but both grades count in GPA",
                    "Courses audited (AU) do not count toward credit totals",
                ],
            },
        ],
    },

    {
        "filename": "transfer_credit_policy.pdf",
        "title": "Transfer Credit Policy",
        "policy_number": "ACAD-REQ-004",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Acceptance of Transfer Credits",
                "paragraphs": [
                    "Westbrook University accepts transfer credits from regionally accredited colleges and universities. Credits from institutions accredited by nationally recognized bodies may also be evaluated on a case-by-case basis. Transfer credits are reviewed by the Registrar's Office and relevant academic departments.",
                ],
            },
            {
                "num": "2", "title": "Transfer Evaluation Process",
                "paragraphs": [
                    "Incoming transfer students must submit official transcripts from all previously attended institutions. The Registrar's Office completes a preliminary transfer credit evaluation within 30 days of enrollment. Departmental reviews for major-specific courses are completed within 45 days of the student's first day of classes.",
                ],
            },
            {
                "num": "3", "title": "Transfer Credit Equivalencies",
                "paragraphs": [
                    "Courses that align closely with Westbrook course offerings receive direct equivalencies (e.g., transferred Calculus I = MATH 151). Courses without a direct equivalent may be accepted as general elective credit. Courses graded below a C (2.0) at the transfer institution are not accepted for credit but are listed on the transfer transcript.",
                ],
            },
            {
                "num": "4", "title": "Credit Limits",
                "bullets": [
                    "Maximum 90 transfer credits accepted toward a 120-credit bachelor's degree",
                    "Minimum 30 credit hours must be completed at Westbrook University (residency requirement)",
                    "No more than 60 credit hours from a community college may count toward the degree",
                    "AP, IB, and CLEP credits are evaluated separately per the departmental credit-by-exam policy",
                ],
            },
        ],
    },

    {
        "filename": "course_load_policy.pdf",
        "title": "Course Load Policy",
        "policy_number": "ACAD-REQ-005",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Standard Course Load",
                "paragraphs": [
                    "The standard full-time course load at Westbrook University is 15 credit hours per semester, which allows students to complete a 120-credit bachelor's degree in four years. Students enrolled in 12 or more credit hours are considered full-time for financial aid purposes.",
                ],
            },
            {
                "num": "2", "title": "Maximum Course Load",
                "paragraphs": [
                    "The maximum course load without overload approval is 18 credit hours per semester. Students who wish to enroll in 19 or more credit hours must obtain approval from their academic advisor and the Dean of the college. Overload approval is typically granted to students with a cumulative GPA of 3.5 or higher and no outstanding Incomplete grades.",
                ],
            },
            {
                "num": "3", "title": "Minimum Enrollment for Financial Aid",
                "paragraphs": [
                    "Students receiving financial aid must maintain at least half-time enrollment (6 credit hours). Dropping below half-time triggers a review of financial aid eligibility. Falling below half-time in two consecutive semesters may result in loan repayment obligations beginning 6 months after the student first drops below half-time.",
                ],
            },
            {
                "num": "4", "title": "Part-Time Enrollment",
                "paragraphs": [
                    "Students enrolled in fewer than 12 credit hours per semester are considered part-time. Part-time students are subject to proportional tuition billing and may have limited access to on-campus housing and some student services. Academic advising and library services remain fully available.",
                ],
            },
        ],
    },

    {
        "filename": "major_declaration_requirements.pdf",
        "title": "Major Declaration Requirements",
        "policy_number": "ACAD-REQ-006",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "When to Declare a Major",
                "paragraphs": [
                    "Students at Westbrook University must declare a major no later than the end of their fourth semester (second year) of enrollment. Students who have not declared by this deadline will be placed on an Academic Hold that prevents registration for the following semester until a major is declared.",
                ],
            },
            {
                "num": "2", "title": "Declaration Process",
                "paragraphs": [
                    "To declare a major, students complete the Major Declaration Form (Form REG-01) and submit it to the Registrar's Office. For selective-admission programs (Business, Nursing, Engineering), students must also meet program-specific admission requirements in addition to submitting the declaration form. See the respective college's program requirements.",
                ],
            },
            {
                "num": "3", "title": "Changing a Major",
                "paragraphs": [
                    "Students may change their major at any time by submitting a Change of Major Form to the Registrar. Students are encouraged to consult with advisors in both their current and prospective departments before changing. Changing a major late in the academic career (after 90 credit hours) may require additional time to complete remaining requirements.",
                ],
            },
            {
                "num": "4", "title": "Double Majors and Minors",
                "paragraphs": [
                    "Students may declare a double major by completing the requirements for both programs. At least 50% of the coursework for each major must be distinct (non-overlapping). Students wishing to add a minor should consult the Minor Declaration form and minor requirements for their chosen area.",
                ],
            },
        ],
    },

    # ── 8. WITHDRAWAL & LEAVE POLICY ─────────────────────────────────────

    {
        "filename": "course_withdrawal_procedure.pdf",
        "title": "Course Withdrawal Procedure",
        "policy_number": "ACAD-WD-001",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "Course withdrawal refers to the official process of dropping a course after the add/drop period has ended. This policy distinguishes between withdrawals before and after the academic deadline, and outlines the GPA and financial implications of each.",
                ],
            },
            {
                "num": "2", "title": "Add/Drop Period",
                "paragraphs": [
                    "During the first 10 business days of the semester (the add/drop period), students may add or drop courses without academic penalty. Dropped courses during this period do not appear on the transcript and tuition is fully refunded minus any applicable fees.",
                ],
            },
            {
                "num": "3", "title": "Withdrawal with 'W' Grade",
                "paragraphs": [
                    "After the add/drop period and through the 10th week of the semester, students may withdraw from a course by submitting a Course Withdrawal Form to the Registrar's Office. A grade of 'W' (Withdrawal) is recorded on the transcript. The 'W' grade does not affect GPA but does count as an attempted credit hour for SAP purposes.",
                    "After the 10th week, withdrawals are only permitted in cases of documented extraordinary circumstances and require Dean's approval (Late Withdrawal).",
                ],
            },
            {
                "num": "4", "title": "Financial Implications",
                "paragraphs": [
                    "Tuition refunds for withdrawals after the add/drop period follow the Tuition Refund Schedule (ACAD-WD-003). Students receiving financial aid should consult the Financial Aid Office before withdrawing, as aid recalculation may result in a balance owed.",
                ],
            },
            {
                "num": "5", "title": "Complete Withdrawal from the University",
                "paragraphs": [
                    "Students who wish to withdraw from all courses must contact the Office of Student Affairs and complete the University Withdrawal Form (Form SA-03). Students should also meet with the Financial Aid Office and Housing Office. All financial obligations must be settled before a formal separation is processed.",
                ],
            },
        ],
    },

    {
        "filename": "medical_leave_of_absence.pdf",
        "title": "Medical Leave of Absence Policy",
        "policy_number": "ACAD-WD-002",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Purpose",
                "paragraphs": [
                    "A Medical Leave of Absence (MLOA) allows students who are unable to continue their studies due to a serious physical or mental health condition to take a temporary leave without academic penalty, with a guaranteed right to return.",
                ],
            },
            {
                "num": "2", "title": "Eligibility",
                "paragraphs": [
                    "Any currently enrolled student who has a documented medical or psychiatric condition that prevents satisfactory academic performance may apply for MLOA. The condition must be supported by documentation from a licensed healthcare provider.",
                ],
            },
            {
                "num": "3", "title": "Application Process",
                "paragraphs": [
                    "Students must submit the MLOA Application (Form SA-07) to the Dean of Students Office along with supporting medical documentation. Documentation must include: the provider's name and contact information, the nature of the condition (specific diagnosis not required), the recommended duration of leave, and attestation that the condition is likely to resolve with treatment.",
                ],
            },
            {
                "num": "4", "title": "Duration and Extension",
                "paragraphs": [
                    "MLOA is granted for one semester at a time and may be renewed for up to two consecutive semesters. Students requiring leave beyond two semesters must re-apply with updated medical documentation. In exceptional cases, the Dean of Students may grant a third semester of leave.",
                ],
            },
            {
                "num": "5", "title": "Academic Impact",
                "paragraphs": [
                    "Courses in progress at the time of MLOA approval will receive a grade of 'W' (Withdrawal). Tuition refunds are processed according to the Tuition Refund Schedule. Financial aid implications should be discussed with the Financial Aid Office prior to departure.",
                ],
            },
            {
                "num": "6", "title": "Return from MLOA",
                "paragraphs": [
                    "Students returning from MLOA must submit a Return from Leave Application at least 6 weeks before the start of the intended return semester. Medical clearance from a licensed provider is required, confirming that the student is able to return to full-time academic work. See Return from Leave Procedure (ACAD-WD-005).",
                ],
            },
        ],
    },

    {
        "filename": "tuition_refund_schedule.pdf",
        "title": "Tuition Refund Schedule",
        "policy_number": "ACAD-WD-003",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "This schedule governs the percentage of tuition refunded when a student withdraws from a course or from the university after the add/drop period. Fees (technology, activity, health) are non-refundable after the first day of classes.",
                ],
            },
            {
                "num": "2", "title": "Tuition Refund Schedule",
                "bullets": [
                    "During add/drop period (first 10 business days): 100% tuition refund",
                    "Weeks 3–4 of the semester: 80% tuition refund",
                    "Week 5 of the semester: 60% tuition refund",
                    "Week 6 of the semester: 40% tuition refund",
                    "Week 7 of the semester: 20% tuition refund",
                    "After Week 7: No refund",
                ],
            },
            {
                "num": "3", "title": "Pro-Rated Refunds for Partial Withdrawal",
                "paragraphs": [
                    "When a student withdraws from some but not all courses, refund calculations apply only to the credit hours withdrawn, not to the student's entire tuition bill.",
                ],
            },
            {
                "num": "4", "title": "Medical Withdrawal Refund",
                "paragraphs": [
                    "Students who receive an approved Medical Leave of Absence at any point in the semester receive a refund of 50% of tuition for that semester, regardless of the withdrawal date. This exception does not apply to fees, room, or board charges.",
                ],
            },
            {
                "num": "5", "title": "Federal Title IV Return of Funds",
                "paragraphs": [
                    "Students who receive federal financial aid and withdraw from the university before completing 60% of the semester are subject to the Return of Title IV Funds calculation per federal regulations (34 CFR 668.22). The Financial Aid Office will notify affected students of any resulting balance owed to the university or to the federal government.",
                ],
            },
        ],
    },

    {
        "filename": "administrative_withdrawal_policy.pdf",
        "title": "Administrative Withdrawal Policy",
        "policy_number": "ACAD-WD-004",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Definition",
                "paragraphs": [
                    "An Administrative Withdrawal (AW) occurs when the university, rather than the student, initiates the withdrawal from one or more courses. Administrative withdrawal may result in a grade of 'W' or 'AW' on the transcript and may affect financial aid.",
                ],
            },
            {
                "num": "2", "title": "Grounds for Administrative Withdrawal",
                "bullets": [
                    "Non-payment of tuition or fees after the payment deadline",
                    "Failure to comply with immunization or health requirements",
                    "Failure to meet enrollment prerequisites discovered after registration",
                    "Extended unexcused absence (6 or more consecutive class sessions without contact with instructor or university)",
                    "Safety concerns requiring immediate removal from campus as directed by the Dean of Students",
                    "Academic Suspension or Disciplinary Suspension",
                ],
            },
            {
                "num": "3", "title": "Notification",
                "paragraphs": [
                    "Students subject to administrative withdrawal will be notified via official university email at least 5 business days before the withdrawal is processed, except in emergency safety situations. The notice will specify the grounds for withdrawal and the deadline for compliance or appeal.",
                ],
            },
            {
                "num": "4", "title": "Appeal",
                "paragraphs": [
                    "Students may appeal an administrative withdrawal within 5 business days of the notice by submitting a written appeal to the Registrar's Office with supporting documentation. Appeals are reviewed by the Administrative Withdrawal Review Committee within 10 business days.",
                ],
            },
        ],
    },

    {
        "filename": "return_from_leave_procedure.pdf",
        "title": "Return from Leave of Absence Procedure",
        "policy_number": "ACAD-WD-005",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Overview",
                "paragraphs": [
                    "Students who have been on an approved leave of absence — whether medical, personal, or military — must follow this procedure to return to enrollment at Westbrook University.",
                ],
            },
            {
                "num": "2", "title": "Application Timeline",
                "paragraphs": [
                    "Students must submit a Return from Leave Application to the Office of Student Affairs at least 6 weeks before the first day of the semester in which they intend to return. Applications received after this deadline may result in delayed registration.",
                ],
            },
            {
                "num": "3", "title": "Required Documentation",
                "bullets": [
                    "For Medical Leave: Medical clearance letter from a licensed healthcare provider indicating the student is ready to return to full-time academic duties",
                    "For Military Leave: Copy of discharge or release orders",
                    "For Personal Leave: Written statement from the student explaining readiness to return",
                    "Updated contact and emergency contact information",
                    "Current immunization records if applicable",
                ],
            },
            {
                "num": "4", "title": "Re-enrollment Process",
                "paragraphs": [
                    "Once the Return from Leave Application is approved, the student is reactivated in the student information system and may register for courses during their assigned registration window. Students returning after one academic year of absence must also meet with their academic advisor to update their degree plan.",
                    "Students returning to selective-admission programs (Business, Nursing, Engineering) must also receive clearance from the program director.",
                ],
            },
            {
                "num": "5", "title": "Financial Aid Reinstatement",
                "paragraphs": [
                    "Financial aid is not automatically reinstated upon return. Students must contact the Financial Aid Office at the time of return application to determine aid eligibility for the returning semester. Reinstated aid is subject to SAP review.",
                ],
            },
        ],
    },

    {
        "filename": "military_leave_policy.pdf",
        "title": "Military Leave Policy",
        "policy_number": "ACAD-WD-006",
        "effective_date": "August 1, 2024",
        "sections": [
            {
                "num": "1", "title": "Policy Statement",
                "paragraphs": [
                    "Westbrook University fully supports its student veterans and active-duty military members. This policy ensures that students called to military service can leave and return without academic or financial penalty, consistent with the Servicemembers Civil Relief Act and the Higher Education Opportunity Act.",
                ],
            },
            {
                "num": "2", "title": "Notification Requirements",
                "paragraphs": [
                    "Students who receive orders for active duty, training, or other military service should notify the Office of Student Affairs as soon as possible and provide a copy of their military orders. Notification should also be sent to the Financial Aid Office, Housing Office, and each instructor.",
                ],
            },
            {
                "num": "3", "title": "Academic Options",
                "paragraphs": [
                    "Students called to military service have the following options depending on timing:",
                ],
                "bullets": [
                    "Before the 10th week: Full withdrawal with 'W' grades (no GPA impact) and full tuition refund",
                    "After the 10th week with incomplete work: Instructor may assign an Incomplete (I) grade; student completes work upon return",
                    "After the 10th week with substantially complete work: Instructor may assign a final grade based on work completed",
                ],
            },
            {
                "num": "4", "title": "Financial Aid During Military Leave",
                "paragraphs": [
                    "Students who withdraw due to military service are entitled to a full refund of tuition and fees for the semester. Student loan repayment may be deferred during active duty. Students should contact the Financial Aid Office and the loan servicer immediately upon receiving orders.",
                ],
            },
            {
                "num": "5", "title": "Return to Enrollment",
                "paragraphs": [
                    "Veterans and service members returning from military leave must submit a Return from Leave Application (see ACAD-WD-005) with a copy of discharge or release papers. Students are entitled to return to the same academic program and standing they held prior to their service leave, provided they return within 5 years of the start of their service period.",
                ],
            },
        ],
    },
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating {len(DOCUMENTS)} policy PDFs in: {OUTPUT_DIR}\n")
    for doc_def in DOCUMENTS:
        build_pdf(
            filename=doc_def["filename"],
            title=doc_def["title"],
            policy_number=doc_def["policy_number"],
            effective_date=doc_def["effective_date"],
            sections_data=doc_def["sections"],
        )
    print(f"\nDone — {len(DOCUMENTS)} PDFs generated.")


if __name__ == "__main__":
    main()
