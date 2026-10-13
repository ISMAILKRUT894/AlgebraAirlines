# database.py — SQLite database setup and sample data generation

import sqlite3
import random
from datetime import datetime, timedelta
from models import EconomyTicket, BusinessTicket

DB_NAME = "skyway.db"


def get_connection():
    """
    Returns a connection to the SQLite database.
    Enables foreign keys and returns rows that can be accessed by column name.
    """ 
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """
    Creates the 3 main tables (Flights, Passengers, Tickets) if they do not exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Flights table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Flights (
        flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_number TEXT UNIQUE NOT NULL,
        departure_city TEXT NOT NULL,
        destination_city TEXT NOT NULL,
        departure_datetime TEXT NOT NULL,
        arrival_datetime TEXT NOT NULL,
        aircraft_model TEXT NOT NULL,
        total_seats INTEGER NOT NULL,
        base_price REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Scheduled'
    );
    """)

    # 2. Passengers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Passengers (
        passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        passport_number TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        date_of_birth TEXT NOT NULL
    );
    """)

    # 3. Tickets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_id INTEGER NOT NULL,
        passenger_id INTEGER NOT NULL,
        seat_number TEXT NOT NULL,
        ticket_type TEXT NOT NULL,
        ticket_price REAL NOT NULL,
        booking_datetime TEXT NOT NULL,
        ticket_status TEXT NOT NULL DEFAULT 'Booked',
        FOREIGN KEY (flight_id) REFERENCES Flights (flight_id),
        FOREIGN KEY (passenger_id) REFERENCES Passengers (passenger_id),
        UNIQUE (flight_id, seat_number)
    );
    """)

    conn.commit()
    conn.close()


def seed_data():
    """
    Generates initial sample data only if the database is currently empty:
    - 20 Flights
    - 50 Passengers
    - 40 Tickets
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM Flights")
    flight_count = cursor.fetchone()[0]
    if flight_count > 0:
        conn.close()
        return  # Data already exists, do not duplicate

    print("Initialising database with initial sample data...")

    # Sample data pools
    cities = ["Almaty", "Astana", "Shymkent", "Aktau", "Atyrau", "Istanbul", "Dubai", "Tashkent", "Tbilisi", "Frankfurt"]
    aircrafts = ["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A321", "Embraer 190"]
    statuses = ["Scheduled", "Scheduled", "Scheduled", "Delayed", "Cancelled"]

    first_names = [
        "Aibek", "Dinara", "Nursultan", "Aigerim", "Bolat", "Zarina", "Yerlan", "Madina",
        "Askar", "Gulnara", "Ali", "Fatima", "Omar", "Leila", "Karim", "Elena", "David",
        "Timur", "Aliya", "Sanzhar", "Daulet", "Dana", "Kairat", "Assel", "Rustam"
    ]
    last_names = [
        "Seitkali", "Bekova", "Nurmagambetov", "Akhmetova", "Bektanov", "Yessenov",
        "Tulegenova", "Sarsenov", "Khasanov", "Khan", "Petrov", "Ivanova", "Smirnov",
        "Ospanov", "Kuznetsov", "Kim", "Lee", "Aliyev", "Ibragimov", "Zhumabayev"
    ]

    # --- Insert 20 Flights ---
    base_date = datetime.now()
    for i in range(1, 21):
        flight_number = f"KC{100 + i}"
        sample_cities = random.sample(cities, 2)
        dep_city = sample_cities[0]
        dest_city = sample_cities[1]

        dep_time = base_date + timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
        arr_time = dep_time + timedelta(hours=random.randint(2, 6))

        dep_str = dep_time.strftime("%Y-%m-%d %H:%M")
        arr_str = arr_time.strftime("%Y-%m-%d %H:%M")

        aircraft = random.choice(aircrafts)
        total_seats = random.choice([100, 120, 150, 180])
        base_price = random.choice([30000.0, 45000.0, 60000.0, 85000.0, 120000.0])
        status = random.choice(statuses)

        cursor.execute("""
        INSERT INTO Flights (flight_number, departure_city, destination_city,
                             departure_datetime, arrival_datetime, aircraft_model,
                             total_seats, base_price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (flight_number, dep_city, dest_city, dep_str, arr_str, aircraft, total_seats, base_price, status))

    # --- Insert 50 Passengers ---
    for i in range(1, 51):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        passport = f"N{1000000 + i}"
        email = f"{fname.lower()}.{lname.lower()}{i}@example.com"
        phone = f"+7701{random.randint(1000000, 9999999)}"
        birth_year = random.randint(1975, 2004)
        birth_date = f"{birth_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"

        cursor.execute("""
        INSERT INTO Passengers (first_name, last_name, passport_number, email, phone, date_of_birth)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (fname, lname, passport, email, phone, birth_date))

    # Commit flights and passengers to get their IDs
    conn.commit()

    # --- Insert 40 Tickets ---
    cursor.execute("SELECT flight_id, base_price, total_seats FROM Flights")
    flight_rows = cursor.fetchall()

    cursor.execute("SELECT passenger_id FROM Passengers")
    passenger_rows = cursor.fetchall()
    passenger_ids = [row["passenger_id"] for row in passenger_rows]

    tickets_created = 0
    assigned_seats = {}  # {flight_id: set of seats}

    while tickets_created < 40:
        flight = random.choice(flight_rows)
        flight_id = flight["flight_id"]
        base_price = flight["base_price"]

        if flight_id not in assigned_seats:
            assigned_seats[flight_id] = set()

        # Find available seat like 1A, 2B, etc.
        row_num = random.randint(1, 20)
        col_letter = random.choice(["A", "B", "C", "D"])
        seat_num = f"{row_num}{col_letter}"

        if seat_num in assigned_seats[flight_id]:
            continue  # Seat already taken on this flight

        assigned_seats[flight_id].add(seat_num)
        passenger_id = random.choice(passenger_ids)

        # Ticket type and price calculation using OOP subclasses
        if random.random() < 0.3:
            ticket_type = "Business"
            ticket_obj = BusinessTicket(0, flight_id, passenger_id, seat_num, ticket_type, 0, "")
        else:
            ticket_type = "Economy"
            ticket_obj = EconomyTicket(0, flight_id, passenger_id, seat_num, ticket_type, 0, "")

        final_price = ticket_obj.calculate_price(base_price)

        booking_dt = (base_date - timedelta(days=random.randint(0, 10))).strftime("%Y-%m-%d %H:%M")
        ticket_status = "Cancelled" if random.random() < 0.1 else "Booked"

        cursor.execute("""
        INSERT INTO Tickets (flight_id, passenger_id, seat_number, ticket_type,
                             ticket_price, booking_datetime, ticket_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (flight_id, passenger_id, seat_num, ticket_type, final_price, booking_dt, ticket_status))

        tickets_created += 1

    conn.commit()
    conn.close()
    print("Database initialised successfully with sample data!")


def init_database():
    """
    Initialises the database: creates tables and generates seed data if empty.
    """
    create_tables()
    seed_data()
