from fpdf import FPDF
from schemas.prompt_test import PromptTestResult

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Guardrail Sentinel Report", ln=True, align="C")
        self.ln(5)

    def add_section(self, title, content):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 10, content)
        self.ln(5)

def build_security_report_pdf(results: list[PromptTestResult], business_type: str, chatbot_url: str, filename: str):
    pdf = PDFReport()
    pdf.add_page()

    pdf.add_section("Business Type", business_type)
    pdf.add_section("Chatbot Endpoint", chatbot_url)

    for i, result in enumerate(results, 1):
        pdf.add_section(f"Prompt {i}", result.prompt)
        pdf.add_section("Response", result.response)
        pdf.add_section("Analysis", result.notes)

    # Basic recommendations (dynamic logic can be added)
    issues = sum(r.is_success for r in results)
    if issues:
        pdf.add_section("Recommendations", "Your chatbot may be leaking sensitive data. We recommend:\n"
                          "- Sanitizing input prompts\n"
                          "- Using output filters\n"
                          "- Implementing role-based restrictions")
    else:
        pdf.add_section("Recommendations", "No issues found. Great job on guardrails!")

    pdf.output(filename)
