from datetime import datetime


class ATM:
    def __init__(self):
        self.accounts = {
            "1001": {"name": "Sai","pin": "1234","balance": 25000.00,"transactions": []},
            "1002": {"name": "Rahul","pin": "5678","balance": 15000.00,"transactions": []},
            "1003": {"name": "Priya","pin": "2468","balance": 30000.00,"transactions": []}
        }

        # ATM cash available
        self.atm_cash = {500: 20,200: 30,100: 50}

        self.max_attempts = 3

   
    def add_transaction(self, account, transaction_type, amount):
        time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        account["transactions"].append({
            "time": time,
            "type": transaction_type,
            "amount": amount,
            "balance": account["balance"]
        })

    def display_header(self):
        print("\n" + "=" * 50)
        print("PYTHON ATM SYSTEM")
        print("=" * 50)

    def login(self):
        self.display_header()

        account_number = input("Enter Account Number: ").strip()

        if account_number not in self.accounts:
            print("Account not found.")
            return None

        account = self.accounts[account_number]

        for attempt in range(self.max_attempts):
            pin = input("Enter 4-digit PIN: ").strip()

            if pin == account["pin"]:
                print(f"\nLogin successful!")
                print(f"Welcome, {account['name']}!")
                return account_number

            remaining = self.max_attempts - attempt - 1

            if remaining > 0:
                print(f" Incorrect PIN. {remaining} attempt(s) remaining.")

        print("\nToo many incorrect attempts.")
        print("Your account has been temporarily locked.")
        return None

    

    def balance_enquiry(self, account):
        print("\n----- BALANCE ENQUIRY -----")
        print(f"Available Balance : ₹{account['balance']:.2f}")

    

    def deposit(self, account):
        print("\n----- CASH DEPOSIT -----")

        try:
            amount = float(input("Enter amount to deposit: ₹"))

            if amount <= 0:
                print(" Enter a valid amount.")
                return

            account["balance"] += amount

            self.add_transaction(
                account,
                "Cash Deposit",
                amount
            )

            print(f" ₹{amount:.2f} deposited successfully.")
            print(f"New Balance: ₹{account['balance']:.2f}")

        except ValueError:
            print(" Invalid amount.")

   

    def calculate_notes(self, amount):
        notes = {}

        for denomination in sorted(self.atm_cash.keys(), reverse=True):
            available_notes = self.atm_cash[denomination]

            required_notes = min(
                amount // denomination,
                available_notes
            )

            if required_notes > 0:
                notes[denomination] = int(required_notes)
                amount -= int(required_notes) * denomination

        if amount != 0:
            return None

        return notes

    def withdraw(self, account):
        print("\n----- CASH WITHDRAWAL -----")
        print("Available denominations: ₹500, ₹200, ₹100")

        try:
            amount = int(input("Enter withdrawal amount: ₹"))

            if amount <= 0:
                print(" Invalid amount.")
                return

            if amount > account["balance"]:
                print(" Insufficient account balance.")
                return

            notes = self.calculate_notes(amount)

            if notes is None:
                print(" ATM cannot dispense this exact amount.")
                print("Please enter an amount compatible with available notes.")
                return

            
            total_atm_cash = sum(
                denomination * count
                for denomination, count in self.atm_cash.items()
            )

            if amount > total_atm_cash:
                print(" ATM does not have enough cash.")
                return

            # Deduct notes from ATM
            for denomination, count in notes.items():
                self.atm_cash[denomination] -= count

            account["balance"] -= amount

            self.add_transaction(
                account,
                "Cash Withdrawal",
                amount
            )

            print("\n Please collect your cash.")

            print("\nNotes dispensed:")
            for denomination, count in notes.items():
                print(f"₹{denomination} × {count}")

            print(f"\nRemaining Balance: ₹{account['balance']:.2f}")

        except ValueError:
            print(" Please enter a valid amount.")


    def transfer(self, sender_number):
        print("\n----- FUND TRANSFER -----")

        receiver_number = input(
            "Enter receiver account number: "
        ).strip()

        if receiver_number not in self.accounts:
            print("Receiver account does not exist.")
            return

        if receiver_number == sender_number:
            print("You cannot transfer money to yourself.")
            return

        sender = self.accounts[sender_number]
        receiver = self.accounts[receiver_number]

        try:
            amount = float(input("Enter transfer amount: ₹"))

            if amount <= 0:
                print("Invalid amount.")
                return

            if amount > sender["balance"]:
                print(" Insufficient balance.")
                return

            sender["balance"] -= amount
            receiver["balance"] += amount

            self.add_transaction(
                sender,
                f"Transfer to {receiver_number}",
                amount
            )

            self.add_transaction(
                receiver,
                f"Transfer from {sender_number}",
                amount
            )

            print("\n Transfer successful!")
            print(f"Transferred: ₹{amount:.2f}")
            print(f"Receiver: {receiver['name']}")
            print(f"Your Balance: ₹{sender['balance']:.2f}")

        except ValueError:
            print(" Invalid amount.")

    # --------------------------------------------------
    # Transaction History
    # --------------------------------------------------

    def transaction_history(self, account):
        print("\n----- TRANSACTION HISTORY -----")

        transactions = account["transactions"]

        if not transactions:
            print("No transactions available.")
            return

        for transaction in transactions[-10:]:
            print(
                f"{transaction['time']} | "
                f"{transaction['type']} | "
                f"₹{transaction['amount']:.2f} | "
                f"Balance: ₹{transaction['balance']:.2f}"
            )

    # --------------------------------------------------
    # Mini Statement
    # --------------------------------------------------

    def mini_statement(self, account):
        print("\n" + "-" * 55)
        print("                    MINI STATEMENT")
        print("-" * 55)

        print(f"Account Holder : {account['name']}")
        print(f"Current Balance: ₹{account['balance']:.2f}")

        print("-" * 55)

        if not account["transactions"]:
            print("No transactions.")
            return

        print("Last 5 Transactions:")

        for transaction in account["transactions"][-5:]:
            print(
                f"{transaction['type']:<25} "
                f"₹{transaction['amount']:>8.2f}"
            )

        print("-" * 55)

    # --------------------------------------------------
    # Change PIN
    # --------------------------------------------------

    def change_pin(self, account):
        print("\n----- CHANGE PIN -----")

        old_pin = input("Enter current PIN: ").strip()

        if old_pin != account["pin"]:
            print(" Incorrect current PIN.")
            return

        new_pin = input("Enter new 4-digit PIN: ").strip()

        if len(new_pin) != 4 or not new_pin.isdigit():
            print(" PIN must contain exactly 4 digits.")
            return

        confirm_pin = input("Confirm new PIN: ").strip()

        if new_pin != confirm_pin:
            print(" PINs do not match.")
            return

        account["pin"] = new_pin

        print(" PIN changed successfully.")

   
    def atm_cash_status(self):
        print("\n----- ATM CASH STATUS -----")

        total = 0

        for denomination, count in self.atm_cash.items():
            value = denomination * count
            total += value

            print(
                f"₹{denomination} Notes : "
                f"{count} "
                f"(₹{value})"
            )

        print("-" * 30)
        print(f"Total ATM Cash: ₹{total}")


    def menu(self, account_number):

        account = self.accounts[account_number]

        while True:

            self.display_header()

            print(f"Account Holder: {account['name']}")
            print(f"Account Number: {account_number}")

            print("\n1. Balance Enquiry")
            print("2. Cash Withdrawal")
            print("3. Cash Deposit")
            print("4. Fund Transfer")
            print("5. Transaction History")
            print("6. Mini Statement")
            print("7. Change PIN")
            print("8. ATM Cash Status")
            print("9. Logout")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.balance_enquiry(account)

            elif choice == "2":
                self.withdraw(account)

            elif choice == "3":
                self.deposit(account)

            elif choice == "4":
                self.transfer(account_number)

            elif choice == "5":
                self.transaction_history(account)

            elif choice == "6":
                self.mini_statement(account)

            elif choice == "7":
                self.change_pin(account)

            elif choice == "8":
                self.atm_cash_status()

            elif choice == "9":
                print("\n Successfully logged out.")
                break

            else:
                print(" Invalid choice.")

            input("\nPress Enter to continue...")

    

    def run(self):

        while True:

            account_number = self.login()

            if account_number:
                self.menu(account_number)

            again = input(
                "\nDo you want to use the ATM again? (Y/N): "
            ).strip().upper()

            if again != "Y":
                print("\nThank you for using Python ATM.")
                print("Have a nice day! ")
                break




if __name__ == "__main__":
    atm = ATM()
    atm.run()