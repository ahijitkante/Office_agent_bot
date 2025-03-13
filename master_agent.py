import logging
import sqlite3
from leave_agent import LeaveAgent
from certificates_agent import CertificateAgent
from academic_agent import AcademicAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MasterAgent:
    def __init__(self):
        """Initialize sub-agents and verify database connectivity."""
        self.agents = {
            "leave": LeaveAgent(),
            "certificate": CertificateAgent(),
            "academic": AcademicAgent()
        }
        self.db_path = "users.db"
        self.verify_database()

    def verify_database(self):
        """Ensure the users table exists in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT CHECK(role IN ('Employee', 'Student')) NOT NULL
                )
            ''')
            conn.commit()
            conn.close()
            logging.info("✅ Database verified: 'users' table is ready.")
        except sqlite3.Error as e:
            logging.error(f"❌ Database error: {e}")

    def validate_user(self, user_id):
        """Check if the user exists in the database and return their role."""
        try:
            user_id = user_id.strip().upper()  # Normalize user ID format
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                logging.info(f"✅ User '{user_id}' found as {result[0]}.")
                return result[0]  # Return role (Employee/Student)
            else:
                logging.error(f"❌ User ID '{user_id}' not found in database!")
                return None  # Invalid user ID
        except sqlite3.Error as e:
            logging.error(f"❌ Database error while validating user: {e}")
            return None

    def classify_intent(self, query):
        """Determine which agent should handle the query based on keywords."""
        query = query.lower()

        leave_keywords = {"leave", "vacation", "sick", "casual", "apply for leave"}
        certificate_keywords = {"certificate", "bonafide", "noc", "generate certificate"}
        academic_keywords = {"academic calendar", "semester calendar", "backlog exam", "schedule", "exam date", "syllabus"}

        if any(word in query for word in leave_keywords):
            return "leave"
        elif any(word in query for word in certificate_keywords):
            return "certificate"
        elif any(word in query for word in academic_keywords):
            return "academic"
        else:
            return None  # No valid intent detected

    def route_query(self, user_id, query):
        """Validate user and route the query to the appropriate agent."""
        role = self.validate_user(user_id)
        if not role:
            return "❌ Access denied: Invalid user ID."

        intent = self.classify_intent(query)
        if not intent:
            return "❌ Sorry, I couldn't understand your request. Please rephrase."

        agent = self.agents.get(intent)
        if agent:
            logging.info(f"✅ Routing query '{query}' to {intent} agent for {role}.")
            try:
                return agent.handle_query(user_id, query)  # ✅ Ensure (user_id, query) is passed correctly
            except TypeError as e:
                logging.error(f"❌ Agent function error: {e}")
                return "❌ Internal error: Agent method received incorrect parameters."
            except Exception as e:
                logging.error(f"❌ Unexpected error: {e}")
                return "❌ An unexpected error occurred."

        return "❌ No suitable agent found for your request."

if __name__ == "__main__":
    master_agent = MasterAgent()
    
    while True:
        user_id = input("\n🔑 Enter User ID (or type 'exit' to quit): ").strip()
        if user_id.lower() == "exit":
            print("👋 Exiting Master Agent...")
            break

        query = input("✏️ Enter your query: ").strip()
        response = master_agent.route_query(user_id, query)

        print("\n📌 Response:", response)
