import sqlite3
import datetime
import os
import logging
from fpdf import FPDF

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class CertificateAgent:
    def __init__(self):
        """Initialize the Certificate Agent with database setup."""
        self.db = "users.db"  # FIXED: Now using the correct database
        self.create_certificates_table()

    def create_certificates_table(self):
        """Ensure the certificates table exists in the database."""
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS certificates (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT,
                            certificate_type TEXT,
                            issue_date TEXT,
                            certificate_path TEXT
                        )''')

        conn.commit()
        conn.close()
        logging.info("✅ Certificates table initialized successfully.")

    def fetch_user_details(self, user_id):
        """Fetch user details dynamically from the users table."""
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute("SELECT name, role FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return {"name": result[0], "role": result[1]}  # 'Student' or 'Employee'
        return None

    def generate_certificate(self, user_id, certificate_type):
        """Generate a certificate in PDF format."""
        user_details = self.fetch_user_details(user_id)

        if not user_details:
            return "❌ User ID not found in database!"

        # Enforce certificate type rules
        if certificate_type == "bonafide" and user_details["role"] != "Student":
            return "❌ Bonafide certificates are only issued to students."
        if certificate_type == "noc" and user_details["role"] != "Employee":
            return "❌ NOC certificates are only issued to employees."

        # Generate certificate
        issue_date = datetime.date.today().strftime("%Y-%m-%d")
        os.makedirs("certificates", exist_ok=True)
        file_name = f"certificates/{user_id}_{certificate_type}_{issue_date}.pdf"

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=16)
        pdf.cell(200, 10, f"{certificate_type.upper()} CERTIFICATE", ln=True, align='C')
        pdf.ln(20)

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"This is to certify that {user_details['name']} has been issued a {certificate_type} certificate.")

        pdf.ln(10)
        pdf.cell(200, 10, f"Issue Date: {issue_date}", ln=True, align='L')
        pdf.output(file_name)

        # Store certificate record
        self.store_certificate(user_id, certificate_type, issue_date, file_name)
        return f"✅ {certificate_type.capitalize()} Certificate generated successfully! Saved as {file_name}"

    def store_certificate(self, user_id, certificate_type, issue_date, file_path):
        """Save certificate details in the database."""
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO certificates (user_id, certificate_type, issue_date, certificate_path)
                          VALUES (?, ?, ?, ?)''',
                       (user_id, certificate_type, issue_date, file_path))
        conn.commit()
        conn.close()
        logging.info(f"✅ Certificate record stored for {user_id}.")

    def verify_certificate(self, user_id, certificate_type):
        """Check if a certificate has been issued to the user."""
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute("SELECT issue_date, certificate_path FROM certificates WHERE user_id=? AND certificate_type=?",
                       (user_id, certificate_type))
        record = cursor.fetchone()
        conn.close()

        if record:
            return f"✅ Certificate found! Issued on {record[0]}. File: {record[1]}"
        else:
            return "❌ No certificate found for the given user ID and type."

    def handle_query(self, user_id, query):
        """Process user queries related to certificates."""
        query = query.lower()

        if not user_id:
            return "❌ Please provide a valid User ID (e.g., STU001 for students, EMP001 for employees)."

        # Extract certificate type
        certificate_types = ["bonafide", "noc"]
        certificate_type = next((ct for ct in certificate_types if ct in query), None)
        if not certificate_type:
            return "❌ Please specify the certificate type (Bonafide, NOC)."

        # Handle verification requests
        if "verify" in query or "check" in query:
            return self.verify_certificate(user_id, certificate_type)

        # Generate the certificate
        return self.generate_certificate(user_id, certificate_type)


# Run the Certificate Agent
if __name__ == "__main__":
    certificate_agent = CertificateAgent()

    while True:
        user_id = input("\n🔑 Enter User ID (or type 'exit' to quit): ").strip()
        if user_id.lower() == "exit":
            print("👋 Exiting Certificate Agent...")
            break

        query = input("✏️ Enter your query: ").strip()
        response = certificate_agent.handle_query(user_id, query)
        print("\n📌 Response:", response)
