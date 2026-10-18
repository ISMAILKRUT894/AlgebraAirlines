# main.py — SkyWay Airlines Management System
# Main entry point with interactive console menu and all user operations.

from database import get_connection, init_database
from datetime import datetime
from models import (
    Flight, Passenger, Ticket,
    EconomyTicket, BusinessTicket,
    is_valid_email, is_valid_phone
)


#  Flight Operations 

def add_flight():
    # Adds a new flight record into the database
    print("\n--- Add New Flight ---")
    flight_number = input("Enter flight number (e.g. KC105): ").strip().upper()
    if not flight_number:
        print("Flight number cannot be empty.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # Check for duplicate flight number
    cursor.execute("SELECT flight_id FROM Flights WHERE flight_number = ?", (flight_number,))
    if cursor.fetchone():
        print(f"Error: Flight number '{flight_number}' already exists.")
        conn.close()
        return

    departure_city = input("Enter departure city: ").strip().title()
    destination_city = input("Enter destination city: ").strip().title()
    if departure_city == destination_city:
        print("Departure and destination cities cannot be the same.")
        conn.close()
        return

    departure_datetime = input("Enter departure date and time (YYYY-MM-DD HH:MM): ").strip()
    arrival_datetime = input("Enter arrival date and time (YYYY-MM-DD HH:MM): ").strip()
    aircraft_model = input("Enter aircraft model (e.g. Airbus A320): ").strip()

    try:
        total_seats = int(input("Enter total seats (e.g. 150): ").strip())
        base_price = float(input("Enter base ticket price in KZT (e.g. 45000): ").strip())
    except ValueError:
        print("Invalid number for seats or price.")
        conn.close()
        return

    cursor.execute("""
    INSERT INTO Flights (flight_number, departure_city, destination_city,
                         departure_datetime, arrival_datetime, aircraft_model,
                         total_seats, base_price, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Scheduled')
    """, (flight_number, departure_city, destination_city, departure_datetime,
          arrival_datetime, aircraft_model, total_seats, base_price))

    conn.commit()
    conn.close()
    print(f"Flight {flight_number} added successfully!")


def show_flights():
    #Displays all flights in a clean list
    print("\n--- All Flights ---")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Flights ORDER BY departure_datetime")
    flights = cursor.fetchall()
    conn.close()

    if not flights:
        print("No flights found.")
        return

    print(f"{'ID':<4} {'Flight No':<10} {'From':<12} {'To':<12} {'Departure':<17} {'Seats':<7} {'Price (KZT)':<12} {'Status':<10}")
    print("-" * 90)
    for f in flights:
        print(f"{f['flight_id']:<4} {f['flight_number']:<10} {f['departure_city']:<12} {f['destination_city']:<12} {f['departure_datetime']:<17} {f['total_seats']:<7} {f['base_price']:<12,.0f} {f['status']:<10}")


# Passenger Operations 

def add_passenger():
    """Adds a new passenger with regex validation for email and phone."""
    print("\n--- Add New Passenger ---")
    first_name = input("Enter first name: ").strip().title()
    last_name = input("Enter last name: ").strip().title()
    if not first_name or not last_name:
        print("First and last names cannot be empty.")
        return

    passport_number = input("Enter passport number (e.g. N1234567): ").strip().upper()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT passenger_id FROM Passengers WHERE passport_number = ?", (passport_number,))
    if cursor.fetchone():
        print(f"Error: Passport number '{passport_number}' is already registered.")
        conn.close()
        return

    # Validate email using regex
    email = input("Enter email address: ").strip()
    if not is_valid_email(email):
        print("Invalid email format (e.g. name@domain.com).")
        conn.close()
        return

    # Validate phone using regex
    phone = input("Enter phone number (e.g. +77011234567): ").strip()
    if not is_valid_phone(phone):
        print("Invalid phone format (must have 7 to 15 digits).")
        conn.close()
        return

    date_of_birth = input("Enter date of birth (YYYY-MM-DD): ").strip()

    cursor.execute("""
    INSERT INTO Passengers (first_name, last_name, passport_number, email, phone, date_of_birth)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, passport_number, email, phone, date_of_birth))

    conn.commit()
    conn.close()
    print(f"Passenger {first_name} {last_name} registered successfully!")


def show_passengers():
    # Displays all passengers
    print("\n--- All Passengers ---")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Passengers ORDER BY passenger_id")
    passengers = cursor.fetchall()
    conn.close()

    if not passengers:
        print("No passengers found.")
        return

    print(f"{'ID':<5} {'Name':<24} {'Passport':<12} {'Phone':<16} {'Email':<28} {'DOB':<10}")
    print("-" * 100)
    for p in passengers:
        full_name = f"{p['first_name']} {p['last_name']}"
        print(f"{p['passenger_id']:<5} {full_name:<24} {p['passport_number']:<12} {p['phone']:<16} {p['email']:<28} {p['date_of_birth']:<10}")


# Ticket Operations 

def book_ticket():
    # Books a ticket for an existing passenger on an available flight
    # Uses EconomyTicket or BusinessTicket class to calculate the price
    
    print("\n--- Book a Ticket ---")
    conn = get_connection()
    cursor = conn.cursor()

    try:
        flight_id = int(input("Enter Flight ID: ").strip())
    except ValueError:
        print("Flight ID must be a number.")
        conn.close()
        return

    # Verify flight exists
    cursor.execute("SELECT * FROM Flights WHERE flight_id = ?", (flight_id,))
    flight = cursor.fetchone()
    if not flight:
        print(f"Flight ID {flight_id} not found.")
        conn.close()
        return

    if flight["status"] == "Cancelled":
        print("Cannot book ticket: This flight has been cancelled.")
        conn.close()
        return

    # Check available seats
    cursor.execute("SELECT COUNT(*) FROM Tickets WHERE flight_id = ? AND ticket_status = 'Booked'", (flight_id,))
    booked_count = cursor.fetchone()[0]
    if booked_count >= flight["total_seats"]:
        print("This flight is fully booked!")
        conn.close()
        return

    try:
        passenger_id = int(input("Enter Passenger ID: ").strip())
    except ValueError:
        print("Passenger ID must be a number.")
        conn.close()
        return

    # Verify passenger exists
    cursor.execute("SELECT * FROM Passengers WHERE passenger_id = ?", (passenger_id,))
    passenger = cursor.fetchone()
    if not passenger:
        print(f"Passenger ID {passenger_id} not found.")
        conn.close()
        return

    # Prevent duplicate active booking for same passenger on same flight
    cursor.execute("""
    SELECT ticket_id FROM Tickets
    WHERE flight_id = ? AND passenger_id = ? AND ticket_status = 'Booked'
    """, (flight_id, passenger_id))
    if cursor.fetchone():
        print("This passenger already has an active booked ticket on this flight.")
        conn.close()
        return

    seat_number = input("Enter seat number (e.g. 12A): ").strip().upper()
    if not seat_number:
        print("Seat number cannot be empty.")
        conn.close()
        return

    # Check if seat is taken on this flight
    cursor.execute("""
    SELECT ticket_id FROM Tickets
    WHERE flight_id = ? AND seat_number = ? AND ticket_status = 'Booked'
    """, (flight_id, seat_number))
    if cursor.fetchone():
        print(f"Seat {seat_number} is already booked on this flight.")
        conn.close()
        return

    print("Ticket Types:")
    print("1. Economy")
    print("2. Business (+80% price)")
    type_choice = input("Select ticket type (1 or 2): ").strip()

    base_price = flight["base_price"]

    # Simple OOP inheritance and polymorphism: calculate price via subclass method
    if type_choice == "2":
        ticket_type = "Business"
        ticket_obj = BusinessTicket(0, flight_id, passenger_id, seat_number, ticket_type, 0, "")
    else:
        ticket_type = "Economy"
        ticket_obj = EconomyTicket(0, flight_id, passenger_id, seat_number, ticket_type, 0, "")

    final_price = ticket_obj.calculate_price(base_price)
    booking_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute("""
    INSERT INTO Tickets (flight_id, passenger_id, seat_number, ticket_type,
                         ticket_price, booking_datetime, ticket_status)
    VALUES (?, ?, ?, ?, ?, ?, 'Booked')
    """, (flight_id, passenger_id, seat_number, ticket_type, final_price, booking_time))

    conn.commit()
    conn.close()
    print(f"\nTicket booked successfully!")
    print(f"Passenger: {passenger['first_name']} {passenger['last_name']}")
    print(f"Flight: {flight['flight_number']} | Seat: {seat_number} | Class: {ticket_type}")
    print(f"Total Price: {final_price:,.0f} KZT")


def show_tickets():
    """Displays all tickets with flight and passenger details using SQL JOIN."""
    print("\n--- All Tickets ---")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT t.ticket_id, f.flight_number, p.first_name, p.last_name,
           t.seat_number, t.ticket_type, t.ticket_price, t.ticket_status, t.booking_datetime
    FROM Tickets t
    JOIN Flights f ON t.flight_id = f.flight_id
    JOIN Passengers p ON t.passenger_id = p.passenger_id
    ORDER BY t.ticket_id
    """)
    tickets = cursor.fetchall()
    conn.close()

    if not tickets:
        print("No tickets found.")
        return

    print(f"{'ID':<5} {'Flight':<9} {'Passenger':<22} {'Seat':<6} {'Type':<10} {'Price (KZT)':<12} {'Status':<10} {'Booked On':<16}")
    print("-" * 98)
    for t in tickets:
        p_name = f"{t['first_name']} {t['last_name']}"
        print(f"{t['ticket_id']:<5} {t['flight_number']:<9} {p_name:<22} {t['seat_number']:<6} {t['ticket_type']:<10} {t['ticket_price']:<12,.0f} {t['ticket_status']:<10} {t['booking_datetime']:<16}")


def cancel_ticket():
    # Cancels a ticket by updating its status to 'Cancelled' (preserving record history)
    print("\n--- Cancel Ticket ---")
    try:
        ticket_id = int(input("Enter Ticket ID to cancel: ").strip())
    except ValueError:
        print("Ticket ID must be a number.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tickets WHERE ticket_id = ?", (ticket_id,))
    ticket = cursor.fetchone()

    if not ticket:
        print(f"Ticket #{ticket_id} not found.")
        conn.close()
        return

    if ticket["ticket_status"] == "Cancelled":
        print(f"Ticket #{ticket_id} is already cancelled.")
        conn.close()
        return

    cursor.execute("UPDATE Tickets SET ticket_status = 'Cancelled' WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    print(f"Ticket #{ticket_id} has been successfully cancelled.")


# Search Operation 

def search_records():
    # Allows searching flights, passengers, or tickets
    print("\n--- Search Records ---")
    print("1. Search Flights by City")
    print("2. Search Passengers by Name")
    print("3. Search Tickets by Flight Number")
    choice = input("Select search option (1-3): ").strip()

    conn = get_connection()
    cursor = conn.cursor()

    if choice == "1":
        city = input("Enter city name: ").strip()
        cursor.execute("""
        SELECT * FROM Flights
        WHERE departure_city LIKE ? OR destination_city LIKE ?
        """, (f"%{city}%", f"%{city}%"))
        results = cursor.fetchall()
        print(f"\nFound {len(results)} flight(s):")
        for f in results:
            print(f"Flight {f['flight_number']}: {f['departure_city']} -> {f['destination_city']} ({f['departure_datetime']}) - Status: {f['status']}")

    elif choice == "2":
        name = input("Enter passenger name: ").strip()
        cursor.execute("""
        SELECT * FROM Passengers
        WHERE first_name LIKE ? OR last_name LIKE ?
        """, (f"%{name}%", f"%{name}%"))
        results = cursor.fetchall()
        print(f"\nFound {len(results)} passenger(s):")
        for p in results:
            print(f"ID #{p['passenger_id']}: {p['first_name']} {p['last_name']} | Passport: {p['passport_number']} | Phone: {p['phone']}")

    elif choice == "3":
        flight_num = input("Enter flight number: ").strip()
        cursor.execute("""
        SELECT t.ticket_id, f.flight_number, p.first_name, p.last_name, t.seat_number, t.ticket_status
        FROM Tickets t
        JOIN Flights f ON t.flight_id = f.flight_id
        JOIN Passengers p ON t.passenger_id = p.passenger_id
        WHERE f.flight_number LIKE ?
        """, (f"%{flight_num}%",))
        results = cursor.fetchall()
        print(f"\nFound {len(results)} ticket(s):")
        for t in results:
            print(f"Ticket #{t['ticket_id']} on {t['flight_number']}: {t['first_name']} {t['last_name']} (Seat: {t['seat_number']}) - Status: {t['ticket_status']}")
    else:
        print("Invalid search choice.")

    conn.close()


# Update Record Operation 

def update_record():
    # Updates flight status or passenger contact details
    print("\n--- Update Record ---")
    print("1. Update Flight Status")
    print("2. Update Passenger Contact Info")
    choice = input("Select option (1 or 2): ").strip()

    conn = get_connection()
    cursor = conn.cursor()

    if choice == "1":
        try:
            flight_id = int(input("Enter Flight ID: ").strip())
        except ValueError:
            print("Flight ID must be a number.")
            conn.close()
            return

        cursor.execute("SELECT flight_number, status FROM Flights WHERE flight_id = ?", (flight_id,))
        flight = cursor.fetchone()
        if not flight:
            print(f"Flight ID {flight_id} not found.")
            conn.close()
            return

        print(f"Current status of Flight {flight['flight_number']} is '{flight['status']}'.")
        print("Status options: Scheduled, Delayed, Cancelled, Completed")
        new_status = input("Enter new status: ").strip().capitalize()
        if new_status in ["Scheduled", "Delayed", "Cancelled", "Completed"]:
            cursor.execute("UPDATE Flights SET status = ? WHERE flight_id = ?", (new_status, flight_id))
            conn.commit()
            print("Flight status updated successfully!")
        else:
            print("Invalid status option.")

    elif choice == "2":
        try:
            passenger_id = int(input("Enter Passenger ID: ").strip())
        except ValueError:
            print("Passenger ID must be a number.")
            conn.close()
            return

        cursor.execute("SELECT first_name, last_name, email, phone FROM Passengers WHERE passenger_id = ?", (passenger_id,))
        passenger = cursor.fetchone()
        if not passenger:
            print(f"Passenger ID {passenger_id} not found.")
            conn.close()
            return

        print(f"Updating info for {passenger['first_name']} {passenger['last_name']}:")
        new_email = input(f"New email (current: {passenger['email']}): ").strip()
        new_phone = input(f"New phone (current: {passenger['phone']}): ").strip()

        if new_email and not is_valid_email(new_email):
            print("Invalid email format.")
            conn.close()
            return

        if new_phone and not is_valid_phone(new_phone):
            print("Invalid phone format.")
            conn.close()
            return

        email_to_save = new_email if new_email else passenger["email"]
        phone_to_save = new_phone if new_phone else passenger["phone"]

        cursor.execute("""
        UPDATE Passengers SET email = ?, phone = ? WHERE passenger_id = ?
        """, (email_to_save, phone_to_save, passenger_id))
        conn.commit()
        print("Passenger contact info updated successfully!")

    else:
        print("Invalid choice.")

    conn.close()


# Delete Record Operation 

def delete_record():
    # Deletes a flight or passenger record only if there are no active (Booked) tickets
    
    print("\n--- Delete Record ---")
    print("1. Delete Flight")
    print("2. Delete Passenger")
    choice = input("Select option (1 or 2): ").strip()

    conn = get_connection()
    cursor = conn.cursor()

    if choice == "1":
        try:
            flight_id = int(input("Enter Flight ID to delete: ").strip())
        except ValueError:
            print("Flight ID must be a number.")
            conn.close()
            return

        # Check for active tickets
        cursor.execute("SELECT COUNT(*) FROM Tickets WHERE flight_id = ? AND ticket_status = 'Booked'", (flight_id,))
        active_tickets = cursor.fetchone()[0]
        if active_tickets > 0:
            print(f"Cannot delete flight: there are {active_tickets} active booked ticket(s) for it.")
            conn.close()
            return

        confirm = input(f"Are you sure you want to delete Flight #{flight_id}? (yes/no): ").strip().lower()
        if confirm == "yes":
            cursor.execute("DELETE FROM Tickets WHERE flight_id = ?", (flight_id,))
            cursor.execute("DELETE FROM Flights WHERE flight_id = ?", (flight_id,))
            conn.commit()
            print(f"Flight #{flight_id} deleted successfully.")
        else:
            print("Deletion cancelled.")

    elif choice == "2":
        try:
            passenger_id = int(input("Enter Passenger ID to delete: ").strip())
        except ValueError:
            print("Passenger ID must be a number.")
            conn.close()
            return

        # Check for active tickets
        cursor.execute("SELECT COUNT(*) FROM Tickets WHERE passenger_id = ? AND ticket_status = 'Booked'", (passenger_id,))
        active_tickets = cursor.fetchone()[0]
        if active_tickets > 0:
            print(f"Cannot delete passenger: they have {active_tickets} active booked ticket(s).")
            conn.close()
            return

        confirm = input(f"Are you sure you want to delete Passenger #{passenger_id}? (yes/no): ").strip().lower()
        if confirm == "yes":
            cursor.execute("DELETE FROM Tickets WHERE passenger_id = ?", (passenger_id,))
            cursor.execute("DELETE FROM Passengers WHERE passenger_id = ?", (passenger_id,))
            conn.commit()
            print(f"Passenger #{passenger_id} deleted successfully.")
        else:
            print("Deletion cancelled.")

    else:
        print("Invalid choice.")

    conn.close()


# Statistics Operation 

def show_statistics():
    """
    Calculates and displays system statistics based on actual database records:
    - Total ticket revenue (active Booked tickets)
    - Seat occupancy rate (occupied seats / total seats * 100)
    - Total counts of flights, passengers, and tickets
    """

    print("\n--- SkyWay Airlines Statistics ---")
    conn = get_connection()
    cursor = conn.cursor()

    # Total revenue from active (Booked) tickets
    cursor.execute("SELECT SUM(ticket_price) FROM Tickets WHERE ticket_status = 'Booked'")
    revenue_result = cursor.fetchone()[0]
    total_revenue = revenue_result if revenue_result is not None else 0.0

    # Total counts
    cursor.execute("SELECT COUNT(*) FROM Flights")
    total_flights = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Passengers")
    total_passengers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Tickets WHERE ticket_status = 'Booked'")
    booked_tickets = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Tickets WHERE ticket_status = 'Cancelled'")
    cancelled_tickets = cursor.fetchone()[0]

    # Total seats across all flights for occupancy rate calculation
    cursor.execute("SELECT SUM(total_seats) FROM Flights")
    seats_result = cursor.fetchone()[0]
    total_seats = seats_result if seats_result is not None else 0

    # Seat occupancy rate calculation (avoid division by zero)
    if total_seats > 0:
        occupancy_rate = (booked_tickets / total_seats) * 100
    else:
        occupancy_rate = 0.0

    conn.close()

    print(f"Total Flights          : {total_flights}")
    print(f"Total Passengers       : {total_passengers}")
    print(f"Active Booked Tickets  : {booked_tickets}")
    print(f"Cancelled Tickets      : {cancelled_tickets}")
    print(f"Total System Seats     : {total_seats}")
    print(f"Seat Occupancy Rate    : {occupancy_rate:.2f}%")
    print(f"Total Ticket Revenue   : {total_revenue:,.2f} KZT")


# ---------- Export Report Operation ----------

def export_report():
    #Exports a comprehensive summary report to a local text file 'results.txt'
    print("\n--- Exporting Report to results.txt ---")
    conn = get_connection()
    cursor = conn.cursor()

    # Calculate statistics
    cursor.execute("SELECT COUNT(*) FROM Flights")
    total_flights = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Passengers")
    total_passengers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Tickets WHERE ticket_status = 'Booked'")
    booked_tickets = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Tickets WHERE ticket_status = 'Cancelled'")
    cancelled_tickets = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(ticket_price) FROM Tickets WHERE ticket_status = 'Booked'")
    revenue_res = cursor.fetchone()[0]
    total_revenue = revenue_res if revenue_res is not None else 0.0

    cursor.execute("SELECT SUM(total_seats) FROM Flights")
    seats_res = cursor.fetchone()[0]
    total_seats = seats_res if seats_res is not None else 0
    occupancy_rate = (booked_tickets / total_seats * 100) if total_seats > 0 else 0.0

    # Fetch top flights
    cursor.execute("SELECT flight_number, departure_city, destination_city, departure_datetime, status FROM Flights ORDER BY departure_datetime LIMIT 10")
    flight_sample = cursor.fetchall()

    conn.close()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("results.txt", "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("        SKYWAY AIRLINES — MANAGEMENT REPORT\n")
        f.write(f"        Generated on: {now_str}\n")
        f.write("=" * 60 + "\n\n")

        f.write("1. SYSTEM OVERVIEW & KEY METRICS\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total Registered Flights   : {total_flights}\n")
        f.write(f"Total Registered Passengers: {total_passengers}\n")
        f.write(f"Active Booked Tickets      : {booked_tickets}\n")
        f.write(f"Cancelled Tickets          : {cancelled_tickets}\n")
        f.write(f"Total Aircraft Seats       : {total_seats}\n")
        f.write(f"Seat Occupancy Rate        : {occupancy_rate:.2f}%\n")
        f.write(f"Total Active Revenue       : {total_revenue:,.2f} KZT\n\n")

        f.write("2. UPCOMING FLIGHT SCHEDULE (SAMPLE)\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'Flight':<10} {'Route':<25} {'Departure':<18} {'Status':<10}\n")
        f.write("-" * 60 + "\n")
        for fl in flight_sample:
            route = f"{fl['departure_city']} -> {fl['destination_city']}"
            f.write(f"{fl['flight_number']:<10} {route:<25} {fl['departure_datetime']:<18} {fl['status']:<10}\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("End of Report\n")

    print("Report successfully saved to results.txt!")


# Main Menu Loop 

def main():
    # Initialises the database and runs the main console loop
    init_database()

    while True:
        print("\n" + "=" * 40)
        print("       SKYWAY AIRLINES SYSTEM")
        print("=" * 40)
        print("1.  Add Flight")
        print("2.  Add Passenger")
        print("3.  Book Ticket")
        print("4.  Show Flights")
        print("5.  Show Passengers")
        print("6.  Show Tickets")
        print("7.  Search")
        print("8.  Update Record")
        print("9.  Cancel Ticket")
        print("10. Delete Record")
        print("11. Show Statistics")
        print("12. Export Report")
        print("0.  Exit")
        print("=" * 40)

        choice = input("Select an option (0-12): ").strip()

        if choice == "1":
            add_flight()
        elif choice == "2":
            add_passenger()
        elif choice == "3":
            book_ticket()
        elif choice == "4":
            show_flights()
        elif choice == "5":
            show_passengers()
        elif choice == "6":
            show_tickets()
        elif choice == "7":
            search_records()
        elif choice == "8":
            update_record()
        elif choice == "9":
            cancel_ticket()
        elif choice == "10":
            delete_record()
        elif choice == "11":
            show_statistics()
        elif choice == "12":
            export_report()
        elif choice == "0":
            print("\nThank you for using SkyWay Airlines. Goodbye!")
            break
        else:
            print("Invalid option. Please enter a number between 0 and 12.")


if __name__ == "__main__":
    main()
