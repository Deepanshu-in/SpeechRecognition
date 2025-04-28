import json
from datetime import datetime

class Bus:
    """
    Bus class to manage seat bookings and cancellations.
    """
    def __init__(self, bus_id, route_popularity):
        self.bus_id = bus_id
        self.seats = [None] * 40  # 40 seats, indexed 0 to 39
        self.waiting_list = []
        self.route_popularity = route_popularity

    def check_seat_availability(self):
        """
        Returns a list of available seats.
        """
        return [i + 1 for i, seat in enumerate(self.seats) if seat is None]

    def book_seat(self, passenger):
        """
        Books a seat for a passenger if available, else adds to waiting list.
        """
        available_seats = self.check_seat_availability()
        if available_seats:
            seat_number = available_seats[0]  # Assign first available seat
            self.seats[seat_number - 1] = passenger
            return {"status": "booked", "seat_number": seat_number}
        elif len(self.waiting_list) < 5:
            self.waiting_list.append(passenger)
            return {"status": "waiting_list", "position": len(self.waiting_list)}
        else:
            return {"status": "full"}

    def cancel_seat(self, seat_number):
        """
        Cancels a seat and allocates it to the first in waiting list if any.
        """
        if 1 <= seat_number <= 40 and self.seats[seat_number - 1] is not None:
            self.seats[seat_number - 1] = None
            if self.waiting_list:
                next_passenger = self.waiting_list.pop(0)
                self.seats[seat_number - 1] = next_passenger
                return {"status": "cancelled", "reallocated_to": next_passenger}
            return {"status": "cancelled"}
        else:
            raise ValueError("Invalid seat number or seat already empty.")

class Passenger:
    """
    Passenger class to store passenger details and calculate fare.
    """
    def __init__(self, name, age, is_student, is_regular, booking_time):
        self.name = name
        self.age = age
        self.is_student = is_student
        self.is_regular = is_regular
        self.booking_time = booking_time

    def calculate_fare(self, distance, route_popularity):
        """
        Calculates fare based on distance, age, booking time, and route popularity.
        """
        base_fare = distance * 2  # Example base fare calculation
        if self.age >= 60:
            base_fare *= 0.9  # 10% discount for senior citizens
        if self.is_student:
            base_fare *= 0.9  # 10% discount for students
        if self.is_regular:
            base_fare *= 0.95  # 5% discount for regular passengers

        # Peak hours surcharge
        peak_hours = (8 <= self.booking_time.hour < 10) or (17 <= self.booking_time.hour < 20)
        if peak_hours:
            base_fare *= 1.15  # 15% extra charge

        # Route popularity adjustment
        if route_popularity == "high":
            base_fare *= 1.2
        elif route_popularity == "medium":
            base_fare *= 1.1

        return base_fare

def main():
    # Example usage
    bus = Bus(bus_id=1, route_popularity="medium")
    passenger = Passenger(name="Ravi", age=65, is_student=False, is_regular=True, booking_time=datetime.now())

    # Book a seat
    booking_result = bus.book_seat(passenger)
    print(json.dumps(booking_result, indent=4))

    # Calculate fare
    fare = passenger.calculate_fare(distance=100, route_popularity=bus.route_popularity)
    print(f"Calculated Fare: {fare}")

    # Cancel a seat
    try:
        cancellation_result = bus.cancel_seat(seat_number=1)
        print(json.dumps(cancellation_result, indent=4))
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
    