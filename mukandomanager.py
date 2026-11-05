
# Import os to check whether a file exists
import os


# Name of the file that stores our mukando records
FILE_NAME = "mukando_records.json"


# Create a Member class to represent each mukando member
class Member:

    # Initialise a new member with their name
    def __init__(self, name):
        self.name = name

        # Dictionary to store the amount paid in each month
        # Example: {"October 2026": 20}
        self.payments = {}

    # Record a member's payment for a particular month
    def record_payment(self, month, amount):

        # Reject payments that are zero or negative
        if amount <= 0:
            raise ValueError("Payment must be greater than zero.")

        # Prevent the same member from paying twice for one month
        if month in self.payments:
            raise ValueError("This member has already paid for this month.")

        # Save the payment in the dictionary
        self.payments[month] = amount

    # Convert the member's information into a dictionary
    # Dictionaries can easily be saved in a JSON file
    def to_dict(self):
        return {
            "name": self.name,
            "payments": self.payments
        }


# Create a Group class to manage the entire mukando group
class Group:

    # Set the monthly contribution when the group is created
    def __init__(self, monthly_contribution=20):

        # Make sure the contribution is a positive amount
        if monthly_contribution <= 0:
            raise ValueError("Contribution must be positive.")

        # Store the monthly contribution amount
        self.monthly_contribution = monthly_contribution

        # List containing all registered Member objects
        self.members = []

        # List containing all recorded payouts
        self.payouts = []

    # Register a new member in the group
    def register_member(self, name):

        # Remove unnecessary spaces from the beginning and end
        name = name.strip()

        # Do not allow an empty member name
        if not name:
            raise ValueError("Member name cannot be empty.")

        # Check whether the member has already been registered
        for member in self.members:
            if member.name.lower() == name.lower():
                raise ValueError("This member is already registered.")

        # Create a Member object and add it to the list
        self.members.append(Member(name))

        # Confirm successful registration
        print(name, "has been registered successfully.")

    # Record a monthly payment for a particular member
    def record_payment(self, name, month, amount):

        # Find the member using their name
        member = self.find_member(name)

        # Stop if the member is not registered
        if member is None:
            raise ValueError("Member not found.")

        # Check that the payment equals the required contribution
        if amount != self.monthly_contribution:
            raise ValueError(
                f"Payment must be ${self.monthly_contribution:.2f}."
            )

        # Call the Member class method to store the payment
        member.record_payment(month, amount)

        # Display a success message
        print("Payment recorded successfully.")

    # Search for a member using their name
    def find_member(self, name):

        # Go through every registered member
        for member in self.members:

            # Compare names without considering capital letters
            if member.name.lower() == name.strip().lower():
                return member

        # Return None if the member cannot be found
        return None

    # Decide who receives the savings pool and record the payout
    def record_payout(self, month):

        # The group must have at least one member
        if not self.members:
            raise ValueError("Register members first.")

        # Prevent more than one payout being recorded for a month
        if any(p["month"] == month for p in self.payouts):
            raise ValueError("A payout is already recorded for this month.")

        # Check that every member has paid the full contribution
        for member in self.members:
            if member.payments.get(month, 0) != self.monthly_contribution:
                raise ValueError(
                    f"{member.name} has not completed payment for {month}."
                )

        # Work out the next recipient based on the number of payouts
        # The first registered member receives the first payout
        next_index = len(self.payouts) % len(self.members)
        recipient = self.members[next_index]

        # Calculate the pool using payments made in this month
        pool = sum(
            member.payments.get(month, 0)
            for member in self.members
        )

        # Check that the group has enough available savings
        if pool > self.total_savings():
            raise ValueError("Insufficient savings for this payout.")

        # Store the payout details in the payouts list
        self.payouts.append({
            "month": month,
            "recipient": recipient.name,
            "amount": pool
        })

        # Display the recipient and the amount received
        print(f"Payout recorded for {recipient.name}: ${pool:.2f}")

    # Calculate the money remaining after payouts
    def total_savings(self):

        # Add all payments made by all members
        total_paid = sum(
            sum(member.payments.values())
            for member in self.members
        )

        # Add all the money distributed through payouts
        total_paid_out = sum(
            payout["amount"] for payout in self.payouts
        )

        # Return total contributions minus total payouts
        return total_paid - total_paid_out

    # Display member payments and the group's financial status
    def show_status(self):

        # Check whether the group has any members
        if not self.members:
            print("No members registered yet.")
            return

        print("\n--- MUKANDO PAYMENT STATUS ---")

        # Display the payment records for each member
        for member in self.members:
            print(f"\nMember: {member.name}")

            # Show a message if no payments have been recorded
            if not member.payments:
                print("  No payments recorded.")

            # Otherwise, display each month and its payment
            else:
                for month, amount in member.payments.items():
                    print(f"  {month}: ${amount:.2f}")

        # Create a sorted list of months in which payments were made
        months = sorted({
            month
            for member in self.members
            for month in member.payments
        })

        print("\n--- MEMBERS BEHIND ON PAYMENTS ---")

        # Track whether any outstanding payments are found
        behind_found = False

        # Check every member for each recorded month
        for month in months:
            for member in self.members:

                # A missing payment is treated as zero
                if member.payments.get(month, 0) < self.monthly_contribution:
                    print(f"{member.name} is behind for {month}.")
                    behind_found = True

        # Display a message if nobody is behind
        if not behind_found:
            print("No outstanding payments for recorded months.")

        # Display the current savings balance
        print(f"\nTotal savings: ${self.total_savings():.2f}")

    # Display the history of payouts made by the group
    def show_payouts(self):
        print("\n--- PAYOUT HISTORY ---")

        # Check whether any payouts have been recorded
        if not self.payouts:
            print("No payouts recorded.")
            return

        # Display each payout's month, recipient and amount
        for payout in self.payouts:
            print(
                f"{payout['month']}: "
                f"{payout['recipient']} received "
                f"${payout['amount']:.2f}"
            )

    # Save the group's information to a JSON file
    def save_records(self):

        # Organise all the information into one dictionary
        data = {
            "monthly_contribution": self.monthly_contribution,

            # Convert each Member object into a dictionary
            "members": [m.to_dict() for m in self.members],

            # Include the payout history
            "payouts": self.payouts
        }

        # Open the file in write mode and save the data
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        print("Records saved successfully.")

    # Load existing records when the program starts
    @classmethod
    def load_records(cls):

        # Check whether a previous records file exists
        if not os.path.exists(FILE_NAME):
            print("No previous records found. Starting a new group.")
            return cls()

        try:
            # Open the existing file and read its JSON data
            with open(FILE_NAME, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Recreate the group using the saved contribution
            group = cls(float(data["monthly_contribution"]))

            # Recreate every Member object from the saved data
            for item in data["members"]:
                member = Member(item["name"])

                # Restore payment amounts from the dictionary
                member.payments = {
                    month: float(amount)
                    for month, amount in item["payments"].items()
                }

                # Add the restored member to the group
                group.members.append(member)

            # Restore the saved payout history
            group.payouts = data.get("payouts", [])

            print("Previous records loaded successfully.")

            # Return the group containing the saved records
            return group

        # Handle common problems when opening or reading the file
        except (OSError, json.JSONDecodeError, KeyError,
                TypeError, ValueError) as error:

            print("Could not load records:", error)
            print("Starting a new group.")

            # Create a new group if the records cannot be loaded
            return cls()


# Main function: controls the program's menu
def main():

    # Load previous records or create a new group
    group = Group.load_records()

    # Keep displaying the menu until the user exits
    while True:
        print("\n===== MUKANDO MANAGER =====")
        print("1. Register member")
        print("2. Record monthly payment")
        print("3. Record payout")
        print("4. View payment status and savings")
        print("5. View payout history")
        print("6. Save records")
        print("7. Change monthly contribution")
        print("8. Exit")

        # Ask the user to select an option
        choice = input("Choose an option (1-8): ").strip()

        try:
            # Option 1: register a member
            if choice == "1":
                name = input("Enter member name: ")
                group.register_member(name)

            # Option 2: record a monthly payment
            elif choice == "2":
                name = input("Enter member name: ")
                month = input(
                    "Enter month (e.g. October 2026): "
                ).strip()

                # Convert the typed amount from text into a number
                amount = float(input("Enter payment amount: $"))

                # Record the payment using the Group method
                group.record_payment(name, month, amount)

            # Option 3: record a payout
            elif choice == "3":
                month = input("Enter payout month: ").strip()
                group.record_payout(month)

            # Option 4: show payments and savings
            elif choice == "4":
                group.show_status()

            # Option 5: display payout history
            elif choice == "5":
                group.show_payouts()

            # Option 6: save the records manually
            elif choice == "6":
                group.save_records()

            # Option 7: change the monthly contribution
            elif choice == "7":
                amount = float(
                    input("Enter new monthly contribution: $")
                )

                # Reject zero or negative contributions
                if amount <= 0:
                    raise ValueError("Contribution must be positive.")

                # Prevent changing the contribution after payouts
                if group.payouts:
                    print(
                        "Contribution cannot be changed after payouts "
                        "have been recorded."
                    )

                # Update the contribution if allowed
                else:
                    group.monthly_contribution = amount
                    print("Monthly contribution updated.")

            # Option 8: save the records and exit
            elif choice == "8":
                group.save_records()
                print("Mukando Manager closed.")
                break

            # Handle a menu choice outside the allowed range
            else:
                print("Invalid choice. Please select 1-8.")

        # Display errors such as invalid amounts or payment details
        except ValueError as error:
            print("Error:", error)

        # Display errors related to reading or writing files
        except OSError as error:
            print("File error:", error)


# Run main() only when this file is executed directly
if __name__ == "__main__":
    main()
