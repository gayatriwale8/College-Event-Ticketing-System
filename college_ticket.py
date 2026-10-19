import mysql.connector

# Connect Python to MySQL
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="pass@123",
    database="CollegeEventDB"
)

if con.is_connected():
    print("MySQL Connected Successfully!")

cursor = con.cursor()


def show_events():
    cursor.execute("SELECT * FROM Events")
    events = cursor.fetchall()

    print("\n===== COLLEGE EVENTS =====")

    for event in events:
        print("Event ID:", event[0])
        print("Event Name:", event[1])
        print("Date:", event[2])
        print("Venue:", event[3])
        print("Ticket Price: Rs.", event[4])
        print("Available Capacity:", event[5])
        print("------------------------")


def register_student():
    name = input("Enter student name: ")
    department = input("Enter department: ")
    email = input("Enter email: ")

    query = """
    INSERT INTO Students (student_name, department, email)
    VALUES (%s, %s, %s)
    """

    try:
        cursor.execute(query, (name, department, email))
        con.commit()
        print("Student registered successfully!")

    except mysql.connector.Error as err:
        con.rollback()
        print("Error:", err)


def book_ticket():
    show_events()

    try:
        student_id = int(input("\nEnter your Student ID: "))
        event_id = int(input("Enter Event ID: "))
        tickets = int(input("Enter number of tickets: "))

        if tickets <= 0:
            print("Ticket quantity must be greater than zero.")
            return

        cursor.execute(
            "SELECT total_tickets FROM Events WHERE event_id = %s",
            (event_id,)
        )
        event = cursor.fetchone()

        if event is None:
            print("Event not found.")
            return

        cursor.execute(
            """
            SELECT COALESCE(SUM(tickets), 0)
            FROM Bookings
            WHERE event_id = %s
            """,
            (event_id,)
        )
        booked = cursor.fetchone()[0]

        available = event[0] - booked

        if tickets > available:
            print("Sorry! Not enough tickets available.")
            return

        cursor.execute(
            "SELECT student_id FROM Students WHERE student_id = %s",
            (student_id,)
        )

        if cursor.fetchone() is None:
            print("Student not found. Please register first.")
            return

        cursor.execute(
            """
            INSERT INTO Bookings (student_id, event_id, tickets)
            VALUES (%s, %s, %s)
            """,
            (student_id, event_id, tickets)
        )

        con.commit()

        print("Ticket booked successfully!")

    except ValueError:
        print("Please enter valid numbers.")

    except mysql.connector.Error as err:
        con.rollback()
        print("Booking error:", err)


def show_bookings():
    query = """
    SELECT
        Bookings.booking_id,
        Students.student_name,
        Events.event_name,
        Bookings.tickets,
        Events.ticket_price,
        Bookings.tickets * Events.ticket_price AS total_amount
    FROM Bookings
    JOIN Students
        ON Bookings.student_id = Students.student_id
    JOIN Events
        ON Bookings.event_id = Events.event_id
    ORDER BY Bookings.booking_id
    """

    cursor.execute(query)
    bookings = cursor.fetchall()

    print("\n===== TICKET BOOKINGS =====")

    if not bookings:
        print("No bookings found.")
        return

    for booking in bookings:
        print("Booking ID:", booking[0])
        print("Student:", booking[1])
        print("Event:", booking[2])
        print("Tickets:", booking[3])
        print("Total Amount: Rs.", booking[5])
        print("------------------------")


while True:
    print("\n===== COLLEGE EVENT TICKETING SYSTEM =====")
    print("1. Show Events")
    print("2. Register Student")
    print("3. Book Tickets")
    print("4. Show Bookings")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        show_events()

    elif choice == "2":
        register_student()

    elif choice == "3":
        book_ticket()

    elif choice == "4":
        show_bookings()

    elif choice == "5":
        print("Thank you for using the system!")
        break

    else:
        print("Invalid choice. Please try again.")


cursor.close()
con.close()
print("MySQL connection closed.") 