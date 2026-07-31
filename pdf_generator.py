from fpdf import FPDF  # <--- Only 1 import needed!

def generate_quiz_pdf(username, category, score, total, percentage, details):
    # 1. Initialize PDF instance in memory
    pdf = FPDF()
    pdf.add_page()
    
    # 2. Add Header Title (Set font -> Print cell -> Line break)
    pdf.set_font("Helvetica", style="B", size=20)
    pdf.cell(0, 10, "Quiz Performance Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    # 3. Add Candidate Details
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 8, f"Candidate: {username}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Category: {category}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Score: {score} / {total} ({percentage:.1f}%)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Status: {'PASSED' if percentage >= 50 else 'NEEDS IMPROVEMENT'}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # 4. Loop through quiz results and print questions
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, "Detailed Breakdown:", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    for idx, d in enumerate(details, 1):
        # Sanitize text to avoid encoding errors with special characters
        q_text = d['question'].encode('latin-1', 'replace').decode('latin-1')
        user_ans = str(d['selected_answer']).encode('latin-1', 'replace').decode('latin-1')
        corr_ans = str(d['correct_answer']).encode('latin-1', 'replace').decode('latin-1')
        status = "CORRECT" if d['is_correct'] else "INCORRECT"
        
        pdf.set_font("Helvetica", style="B", size=11)
        pdf.cell(0, 6, f"Q{idx}. {q_text}", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 5, f"   Your Answer: {user_ans} [{status}]", new_x="LMARGIN", new_y="NEXT")
        if not d['is_correct']:
            pdf.cell(0, 5, f"   Correct Answer: {corr_ans}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # 5. Output raw bytes directly (FPDF handles bytes in memory natively, no `io.BytesIO` required!)
    return bytes(pdf.output())