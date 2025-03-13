import datetime
import sqlite3
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class LeaveAgent:
    def __init__(self):
        self.db = "leave_requests.db"
        self.create_database()

    def create_database(self):
        """Creates the leave request database if it does not exist."""
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS leave_requests (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                employee_id TEXT,
                                leave_type TEXT,
                                start_date TEXT,
                                end_date TEXT,
                                status TEXT
                            )''')
            conn.commit()
            conn.close()
            logging.info("✅ Database verified: 'leave_requests' table is ready.")
        except sqlite3.Error as e:
            logging.error(f"❌ Database error: {e}")

    def check_leave_balance(self, employee_id, leave_type):
        """Fetch leave balance from HRMS (for now, using a static dictionary)."""
        leave_balances = {
            "casual": 10,
            "sick": 5,
            "vacation": 15
        }
        return leave_balances.get(leave_type.lower(), 0)

    def check_conflict(self, employee_id, start_date, end_date):
        """Check if an employee has overlapping leave requests."""
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM leave_requests WHERE employee_id=? 
                              AND status='Approved' 
                              AND ((start_date BETWEEN ? AND ?) 
                              OR (end_date BETWEEN ? AND ?) 
                              OR (? BETWEEN start_date AND end_date))''',
                           (employee_id, start_date, end_date, start_date, end_date, start_date))
            conflicts = cursor.fetchall()
            conn.close()
            return len(conflicts) > 0
        except sqlite3.Error as e:
            logging.error(f"❌ Database error while checking conflicts: {e}")
            return True  # Assume conflict in case of an error

    def apply_leave_policies(self, employee_id, leave_type, start_date, end_date):
        """Apply leave rules before approving the request."""
        leave_days = (end_date - start_date).days + 1
        available_balance = self.check_leave_balance(employee_id, leave_type)

        if leave_days > available_balance:
            return "❌ Leave request denied: Not enough balance."

        if self.check_conflict(employee_id, start_date, end_date):
            return "❌ Leave request denied: Overlapping leave found."

        return "✅ Leave approved."

    def store_leave_request(self, employee_id, leave_type, start_date, end_date, status):
        """Save the leave request in the database."""
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, status)
                              VALUES (?, ?, ?, ?, ?)''', 
                           (employee_id, leave_type, start_date, end_date, status))
            conn.commit()
            conn.close()
            logging.info(f"📌 Leave request stored: {employee_id}, {leave_type}, {start_date} to {end_date}, {status}")
        except sqlite3.Error as e:
            logging.error(f"❌ Database error while storing leave request: {e}")

    def revoke_leave(self, employee_id, leave_type, start_date, end_date):
        """Revoke an approved leave request."""
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''UPDATE leave_requests 
                              SET status='Revoked' 
                              WHERE employee_id=? AND leave_type=? 
                              AND start_date=? AND end_date=? AND status='Approved' ''',
                           (employee_id, leave_type, start_date, end_date))
            conn.commit()
            rows_updated = cursor.rowcount
            conn.close()

            if rows_updated > 0:
                return "✅ Leave revoked successfully."
            return "❌ No approved leave found for revocation."
        except sqlite3.Error as e:
            logging.error(f"❌ Database error while revoking leave: {e}")
            return "❌ Error processing leave revocation."

    def extract_leave_details(self, query):
        """Extract leave type and duration or specific dates using regex."""
        leave_types = ["casual", "sick", "vacation"]
        leave_type = next((lt for lt in leave_types if lt in query.lower()), None)

        if not leave_type:
            return None, None, None

        # Check for number of days
        days_match = re.search(r'(\d+)\s*(day|days)', query)
        if days_match:
            leave_days = int(days_match.group(1))
            start_date = datetime.date.today()
            end_date = start_date + datetime.timedelta(days=leave_days - 1)
            return leave_type, start_date, end_date

        # Check for specific start and end dates (YYYY-MM-DD format)
        date_match = re.findall(r'(\d{4}-\d{2}-\d{2})', query)
        if len(date_match) == 2:
            start_date = datetime.datetime.strptime(date_match[0], "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(date_match[1], "%Y-%m-%d").date()
            if end_date < start_date:
                return None, None, None  # Invalid date range
            return leave_type, start_date, end_date

        return None, None, None

    def handle_query(self, user_id, query):
        """Process leave queries."""
        query = query.lower()

        if "revoke leave" in query:
            leave_type, start_date, end_date = self.extract_leave_details(query)
            if not leave_type or not start_date or not end_date:
                return "❌ Please specify leave type and valid duration for revocation."
            return self.revoke_leave(user_id, leave_type, start_date, end_date)

        leave_type, start_date, end_date = self.extract_leave_details(query)
        if not leave_type or not start_date or not end_date:
            return "❌ Please specify leave type (Casual, Sick, Vacation) and a valid duration."

        # Apply leave policies
        result = self.apply_leave_policies(user_id, leave_type, start_date, end_date)

        # Store request in the database if approved
        status = "Approved" if "approved" in result else "Rejected"
        self.store_leave_request(user_id, leave_type, start_date, end_date, status)

        return result


# Run the Leave Agent (Standalone Mode)
if __name__ == "__main__":
    leave_agent = LeaveAgent()
    while True:
        user_id = input("\n🔑 Enter Employee ID (or type 'exit' to quit): ").strip()
        if user_id.lower() == "exit":
            print("👋 Exiting Leave Agent...")
            break

        query = input("✏️ Enter leave request: ").strip()
        response = leave_agent.handle_query(user_id, query)

        print("\n📌 Response:", response)
