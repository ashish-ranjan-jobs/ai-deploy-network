import io
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.models.deployment import Deployment
from src.models.user import User


def generate_builder_profile_pdf(user: User, deployments: List[Deployment]) -> bytes:
    """Generate a high-impact branded PDF portfolio for a Founding Builder."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0f172a")  # Slate 900
    brand_blue = colors.HexColor("#2563eb")  # Blue 600
    gold_badge = colors.HexColor("#d97706")  # Amber 600

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )
    badge_style = ParagraphStyle(
        "FoundingBadge",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=gold_badge,
        fontName="Helvetica-Bold",
        spaceAfter=14,
    )
    section_title = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=brand_blue,
        spaceBefore=14,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
    )
    metric_style = ParagraphStyle(
        "MetricHighlight",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#065f46"),
        fontName="Helvetica-Bold",
    )

    story = []

    # Header / Title
    story.append(Paragraph(f"{user.full_name}", title_style))
    if user.title:
        story.append(Paragraph(f"{user.title} {f'at {user.company}' if user.company else ''}", subtitle_style))

    # Founding Builder badge line
    membership_label = user.membership.badge_label if user.membership else "Builder Profile"
    verified_str = " • Verified AI Practitioner" if user.is_verified else " • Submission Pending Verification"
    story.append(Paragraph(f"⭐ {membership_label}{verified_str}", badge_style))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=12))

    # Contact & Links Table
    meta_info = [
        [
            Paragraph(f"<b>Email:</b> {user.email}", body_style),
            Paragraph(f"<b>Location:</b> {user.location or 'Global'}", body_style),
        ],
        [
            Paragraph(f"<b>LinkedIn:</b> {user.linkedin_url or 'N/A'}", body_style),
            Paragraph(f"<b>GitHub:</b> {user.github_url or 'N/A'}", body_style),
        ],
    ]
    t = Table(meta_info, colWidths=[260, 260])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 12))

    # Executive Summary / Bio
    if user.bio:
        story.append(Paragraph("Executive Summary & AI Specialization", section_title))
        story.append(Paragraph(user.bio, body_style))
        story.append(Spacer(1, 12))

    # Deployments Showcase
    story.append(Paragraph(f"Documented AI Deployments ({len(deployments)})", section_title))
    if not deployments:
        story.append(Paragraph("No deployments documented yet.", body_style))
    else:
        for idx, d in enumerate(deployments, 1):
            status_text = "VERIFIED" if d.is_verified else d.verification_status
            status_color = "#16a34a" if d.is_verified else "#ca8a04"

            story.append(Spacer(1, 8))
            dep_header = f"<b>{idx}. {d.title}</b> &nbsp;&nbsp;<font color='{status_color}'>[{status_text}]</font>"
            story.append(
                Paragraph(
                    dep_header,
                    ParagraphStyle("DH", parent=styles["Normal"], fontSize=12, leading=16, textColor=primary_color),
                )
            )

            dep_meta = f"<i>Industry:</i> {d.industry} &nbsp;|&nbsp; <i>AI Stack:</i> {d.ai_tech_used} &nbsp;|&nbsp; <i>Stage:</i> {d.deployment_stage}"
            story.append(Paragraph(dep_meta, subtitle_style))

            story.append(Paragraph("<b>Problem:</b> " + d.problem_statement, body_style))
            story.append(Spacer(1, 4))
            story.append(Paragraph("<b>Solution:</b> " + d.solution_description, body_style))
            story.append(Spacer(1, 4))
            story.append(Paragraph("<b>Measurable Results:</b> " + d.measurable_results, metric_style))
            if d.live_demo_url or d.repo_url:
                links = []
                if d.live_demo_url:
                    links.append(f"Demo: {d.live_demo_url}")
                if d.repo_url:
                    links.append(f"Repo: {d.repo_url}")
                story.append(Paragraph(f"<i>Links:</i> {' | '.join(links)}", subtitle_style))

            story.append(
                HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#f1f5f9"), spaceBefore=8, spaceAfter=8)
            )

    # Footer note
    story.append(Spacer(1, 20))
    footer_text = "Documented & certified via AI Deploy Network (https://aideploynetwork.com) — The Global Directory of Proven AI Implementations."
    story.append(
        Paragraph(
            footer_text,
            ParagraphStyle(
                "Footer", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#94a3b8")
            ),
        )
    )

    doc.build(story)
    return buffer.getvalue()


def generate_deployment_pdf(deployment: Deployment) -> bytes:
    """Generate a single deployment case study PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()

    primary_color = colors.HexColor("#0f172a")
    brand_blue = colors.HexColor("#2563eb")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12,
    )
    section_title = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=brand_blue,
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
    )
    metric_style = ParagraphStyle(
        "MetricHighlight",
        parent=styles["Normal"],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#065f46"),
        fontName="Helvetica-Bold",
    )

    story = []

    # Title
    story.append(Paragraph(f"AI Case Study: {deployment.title}", title_style))
    author_name = deployment.user.full_name if deployment.user else "Builder"
    membership_label = (
        deployment.user.membership.badge_label if deployment.user and deployment.user.membership else "Builder"
    )
    story.append(Paragraph(f"Author: {author_name} ({membership_label})", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=12))

    # Meta Table
    meta = [
        [
            Paragraph(f"<b>Industry:</b> {deployment.industry}", body_style),
            Paragraph(f"<b>Deployment Stage:</b> {deployment.deployment_stage}", body_style),
        ],
        [
            Paragraph(f"<b>AI Tech Stack:</b> {deployment.ai_tech_used}", body_style),
            Paragraph(f"<b>Verification Status:</b> {deployment.verification_status}", body_style),
        ],
    ]
    t = Table(meta, colWidths=[260, 260])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 14))

    # Problem
    story.append(Paragraph("1. Problem Statement", section_title))
    story.append(Paragraph(deployment.problem_statement, body_style))
    story.append(Spacer(1, 10))

    # Solution
    story.append(Paragraph("2. Solution & Architecture", section_title))
    story.append(Paragraph(deployment.solution_description, body_style))
    story.append(Spacer(1, 10))

    # Measurable Results
    story.append(Paragraph("3. Measurable Impact & Production Results", section_title))
    story.append(Paragraph(deployment.measurable_results, metric_style))
    story.append(Spacer(1, 14))

    if deployment.live_demo_url or deployment.repo_url:
        story.append(Paragraph("4. Reference Links", section_title))
        if deployment.live_demo_url:
            story.append(Paragraph(f"<b>Live Demo:</b> {deployment.live_demo_url}", body_style))
        if deployment.repo_url:
            story.append(Paragraph(f"<b>Repository:</b> {deployment.repo_url}", body_style))

    doc.build(story)
    return buffer.getvalue()
