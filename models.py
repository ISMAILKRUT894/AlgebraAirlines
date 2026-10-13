# models.py — Simple OOP classes and validation for SkyWay Airlines

import re


# Validation Functions (Using Regular Expressions) 

def is_valid_email(email):
    """
    Checks if an email address has a valid format (e.g., user@example.com).
    Uses a simple regular expression pattern.
    """
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if re.match(pattern, email.strip()):
        return True
    return False


def is_valid_phone(phone):
    """
    Checks if a phone number contains an optional '+' followed by 7 to 15 digits.
    """
    pattern = r"^\+?\d{7,15}$"
    if re.match(pattern, phone.strip()):
        return True
    return False


# Flight Class

class Flight:
    """
    Stores flight information: route, times, aircraft, seats, price, and status.
    """

    def __init__(self, flight_id, flight_number, departure_city, destination_city,
                 departure_datetime, arrival_datetime, aircraft_model,
                 total_seats, base_price, status="Scheduled"):
        self.flight_id = flight_id
        self.flight_number = flight_number
        self.departure_city = departure_city
        self.destination_city = destination_city
        self.departure_datetime = departure_datetime
        self.arrival_datetime = arrival_datetime
        self.aircraft_model = aircraft_model
        self.total_seats = total_seats
        self.base_price = base_price
        self.status = status

    def display_info(self):
        """Displays a clean summary of the flight."""
        print(f"Flight {self.flight_number} | {self.departure_city} -> {self.destination_city} | Status: {self.status} | Price: {self.base_price:,.0f} KZT")


# Passenger Class 

class Passenger:
    """
    Stores passenger personal information: name, passport, contact, and date of birth.
    """

    def __init__(self, passenger_id, first_name, last_name, passport_number,
                 email, phone, date_of_birth):
        self.passenger_id = passenger_id
        self.first_name = first_name
        self.last_name = last_name
        self.passport_number = passport_number
        self.email = email
        self.phone = phone
        self.date_of_birth = date_of_birth

    def get_full_name(self):
        """Returns the full name of the passenger."""
        return f"{self.first_name} {self.last_name}"

    def display_info(self):
        """Displays a clean summary of the passenger."""
        print(f"Passenger #{self.passenger_id}: {self.get_full_name()} | Passport: {self.passport_number} | Phone: {self.phone}")


# ---------- Ticket Base Class (OOP Inheritance) ----------

class Ticket:
    """
    Base class representing an airline ticket.
    Subclasses override calculate_price() to apply specific pricing rules.
    """

    def __init__(self, ticket_id, flight_id, passenger_id, seat_number,
                 ticket_type, ticket_price, booking_datetime, ticket_status="Booked"):
        self.ticket_id = ticket_id
        self.flight_id = flight_id
        self.passenger_id = passenger_id
        self.seat_number = seat_number
        self.ticket_type = ticket_type
        self.ticket_price = ticket_price
        self.booking_datetime = booking_datetime
        self.ticket_status = ticket_status

    def calculate_price(self, base_price):
        """Base implementation: returns the standard base flight price."""
        return base_price


# Economy Ticket Subclass 

class EconomyTicket(Ticket):
    """
    Economy class ticket.
    Overrides calculate_price(): standard price (multiplier 1.0).
    """

    def calculate_price(self, base_price):
        return round(base_price * 1.0, 2)


# Business Ticket Subclass 

class BusinessTicket(Ticket):
    """
    Business class ticket.
    Overrides calculate_price(): 80% premium (multiplier 1.8).
    """

    def calculate_price(self, base_price):
        return round(base_price * 1.8, 2)
