import sqlite3
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AcademicAgent:
    def __init__(self):
        self.db = "academic_data.db"
        self.create_database()

    def create_database(self):
        """Creates the academic events database if it does not exist."""
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS academic_events (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            event_name TEXT UNIQUE,
                            event_date TEXT,
                            event_type TEXT
                        )''')
        conn.commit()
        conn.close()
        logging.info("✅ Database verified: 'academic_events' table is ready.")

    def add_event(self, event_name, event_date, event_type):
        """Insert an academic event into the database if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO academic_events (event_name, event_date, event_type) VALUES (?, ?, ?)", 
                           (event_name, event_date, event_type))
            conn.commit()
            conn.close()
            logging.info(f"✅ Event added: {event_name} on {event_date} ({event_type})")
        except sqlite3.Error as e:
            logging.error(f"❌ Database error while adding event: {e}")

    def get_event(self, query):
        """Fetch academic events based on user query."""
        query = query.lower().strip()
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Match query with known academic keywords
        academic_keywords = {
            "academic calendar": "academic calendar",
            "semester exams": "semester exams",
            "backlog exams": "backlog exams",
            "exam schedule": "semester exams",
            "semester start": "academic calendar"
        }
        search_type = academic_keywords.get(query, query)  # Map common queries to stored event types

        cursor.execute("SELECT event_name, event_date FROM academic_events WHERE event_type LIKE ?", ('%' + search_type + '%',))
        result = cursor.fetchall()
        conn.close()

        if result:
            response = "📅 Upcoming Academic Events:\n"
            for event_name, event_date in result:
                response += f"✅ {event_name} on {event_date}\n"
            return response.strip()
        else:
            return "❌ No academic events found. Try asking about 'semester exams' or 'backlog exams'."

    def handle_query(self, user_id, query):
        """Process user queries for academic events."""
        logging.info(f"🎓 Handling academic query for user '{user_id}': {query}")
        return self.get_event(query)

# Run the Academic Agent (Standalone Mode)
if __name__ == "__main__":
    academic_agent = AcademicAgent()

    # Adding some sample events for testing (only adds if not already present)
    academic_agent.add_event("Semester Exams Start", "2025-06-10", "semester exams")
    academic_agent.add_event("Backlog Exams", "2025-07-15", "backlog exams")
    academic_agent.add_event("New Semester Begins", "2025-08-01", "academic calendar")

    while True:
        user_id = input("\n🔑 Enter User ID (or type 'exit' to quit): ").strip()
        if user_id.lower() == "exit":
            print("👋 Exiting Academic Agent...")
            break
        query = input("✏️ Enter academic query: ").strip()
        response = academic_agent.handle_query(user_id, query)
        print("\n📌 Response:", response)
