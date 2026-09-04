import numpy as np
from prettytable import PrettyTable

from database import (
    create_tables,
    add_user,
    get_users,
    save_expense,
    get_all_expenses,
    get_user_expenses,
    get_all_expense_splits,
    save_payment,
    get_all_payments
)


# =========================================================
# GLOBAL VARIABLES
# =========================================================

friends = []

expense_matrix = np.zeros((0, 0))


# =========================================================
# INITIALIZE USERS
# =========================================================

def initialize_users():

    global friends
    global expense_matrix

    existing_users = get_users()

    print("\n========== EXPENSE SHARING APP ==========")

    if existing_users:

        print("\nExisting users:")

        for i, user in enumerate(existing_users, start=1):
            print(f"{i}. {user}")

        print("\n1. Continue with these users")
        print("2. Add new users")

        while True:

            choice = input("\nEnter choice: ").strip()

            if choice == "1":

                friends = existing_users
                break

            elif choice == "2":

                new_users = input(
                    "\nEnter new users separated by comma: "
                ).split(",")

                new_users = [
                    user.strip()
                    for user in new_users
                    if user.strip()
                ]

                for user in new_users:
                    add_user(user)

                friends = get_users()
                break

            else:
                print("Please enter 1 or 2.")

    else:

        print("\nNo existing users found.")

        while True:

            users_input = input(
                "Enter friends separated by comma: "
            ).split(",")

            users_input = [
                user.strip()
                for user in users_input
                if user.strip()
            ]

            # Remove duplicates
            users_input = list(
                dict.fromkeys(users_input)
            )

            if not users_input:

                print("Please enter at least one user.")
                continue

            for user in users_input:
                add_user(user)

            friends = get_users()
            break

    # Create matrix based on users
    expense_matrix = np.zeros(
        (len(friends), len(friends))
    )


# =========================================================
# LOAD PREVIOUS EXPENSES
# =========================================================

def load_previous_expenses():

    global expense_matrix

    expense_matrix = np.zeros(
        (len(friends), len(friends))
    )

    splits = get_all_expense_splits()

    for payer, beneficiary, amount_owed in splits:

        if payer not in friends:
            continue

        if beneficiary not in friends:
            continue

        payer_index = friends.index(payer)

        beneficiary_index = friends.index(
            beneficiary
        )

        expense_matrix[
            payer_index
        ][
            beneficiary_index
        ] += amount_owed


# =========================================================
# ADD EXPENSE
# =========================================================

def add_expense():

    global expense_matrix

    print("\n========== ADD EXPENSE ==========")

    # -----------------------------------
    # Description
    # -----------------------------------

    description = input(
        "Enter expense description: "
    ).strip()

    if not description:

        print("Description cannot be empty.")
        return

    # -----------------------------------
    # Select payer
    # -----------------------------------

    print("\nFriends:")

    for friend in friends:
        print("-", friend)

    while True:

        payer = input(
            "\nWho paid? "
        ).strip()

        if payer in friends:
            break

        print("Invalid friend name.")

    # -----------------------------------
    # Amount
    # -----------------------------------

    while True:

        try:

            amount = float(
                input("Enter amount: ₹")
            )

            if amount <= 0:

                print(
                    "Amount must be greater than zero."
                )

                continue

            break

        except ValueError:

            print(
                "Please enter a valid amount."
            )

    # -----------------------------------
    # Beneficiaries
    # -----------------------------------

    while True:

        beneficiaries_input = input(
            "\nEnter beneficiaries separated by comma: "
        )

        beneficiaries = [
            person.strip()
            for person in beneficiaries_input.split(",")
            if person.strip()
        ]

        # Remove duplicates
        beneficiaries = list(
            dict.fromkeys(beneficiaries)
        )

        if not beneficiaries:

            print(
                "Please enter at least one beneficiary."
            )

            continue

        invalid_names = [
            person
            for person in beneficiaries
            if person not in friends
        ]

        if invalid_names:

            print(
                "Invalid names:",
                ", ".join(invalid_names)
            )

            continue

        break

    # -----------------------------------
    # Split type
    # -----------------------------------

    print("\nSelect Split Type")

    print("1. Equal Split")
    print("2. Custom Split")

    while True:

        choice = input(
            "Enter choice: "
        ).strip()

        if choice in ["1", "2"]:
            break

        print("Please enter 1 or 2.")

    splits = {}

    # =====================================================
    # EQUAL SPLIT
    # =====================================================

    if choice == "1":

        total_paise = round(
            amount * 100
        )

        number_of_people = len(
            beneficiaries
        )

        base_share = (
            total_paise // number_of_people
        )

        remainder = (
            total_paise % number_of_people
        )

        for i, person in enumerate(
            beneficiaries
        ):

            share_paise = base_share

            if i < remainder:
                share_paise += 1

            splits[person] = (
                share_paise / 100
            )

        print(
            "\n========== EQUAL SPLIT =========="
        )

        for person, share in splits.items():

            print(
                f"{person}: ₹{share:.2f}"
            )

    # =====================================================
    # CUSTOM SPLIT
    # =====================================================

    else:

        print(
            "\n========== CUSTOM SPLIT =========="
        )

        while True:

            splits = {}

            total_custom = 0

            for person in beneficiaries:

                while True:

                    try:

                        share = float(
                            input(
                                f"Enter amount for "
                                f"{person}: ₹"
                            )
                        )

                        if share < 0:

                            print(
                                "Amount cannot be negative."
                            )

                            continue

                        splits[person] = share

                        total_custom += share

                        break

                    except ValueError:

                        print(
                            "Please enter a valid amount."
                        )

            if round(
                total_custom,
                2
            ) == round(
                amount,
                2
            ):

                break

            print("\n❌ Invalid split!")

            print(
                f"Expense amount: ₹{amount:.2f}"
            )

            print(
                f"Split total: ₹{total_custom:.2f}"
            )

            print(
                "The split amounts must equal "
                "the expense amount."
            )

            print(
                "\nPlease enter the amounts again."
            )

    # -----------------------------------
    # Display split total
    # -----------------------------------

    split_total = sum(
        splits.values()
    )

    print(
        f"\nTotal split: ₹{split_total:.2f}"
    )

    # -----------------------------------
    # Save expense
    # -----------------------------------

    split_list = list(
        splits.items()
    )

    split_type = (
        "Equal"
        if choice == "1"
        else "Custom"
    )

    save_expense(
        description,
        amount,
        payer,
        split_type,
        split_list
    )

    # -----------------------------------
    # Update matrix immediately
    # -----------------------------------

    payer_index = friends.index(
        payer
    )

    for person, share in splits.items():

        person_index = friends.index(
            person
        )

        expense_matrix[
            payer_index
        ][
            person_index
        ] += share

    print(
        "\n✅ Expense added successfully!"
    )


# =========================================================
# VIEW ALL EXPENSES
# =========================================================

def view_all_expenses():

    print("\n========== ALL EXPENSES ==========")

    expenses = get_all_expenses()

    if not expenses:

        print("No expenses found.")
        return

    table = PrettyTable()

    table.field_names = [
        "ID",
        "Description",
        "Amount",
        "Payer",
        "Split",
        "Date"
    ]

    for expense in expenses:

        expense_id = expense[0]
        description = expense[1]
        amount = expense[2]
        payer = expense[3]
        split_type = expense[4]
        created_at = expense[5]

        table.add_row([
            expense_id,
            description,
            f"₹{amount:.2f}",
            payer,
            split_type,
            created_at
        ])

    print(table)


# =========================================================
# USER TRANSACTION HISTORY
# =========================================================

def view_user_history():

    print("\n========== USER HISTORY ==========")

    print("\nAvailable users:")

    for user in friends:
        print("-", user)

    user_name = input(
        "\nEnter user name: "
    ).strip()

    if user_name not in friends:

        print("Invalid user.")
        return

    expenses = get_user_expenses(
        user_name
    )

    payments = get_all_payments()

    if not expenses and not payments:

        print(
            f"No transactions found for {user_name}."
        )

        return

    print(
        f"\nTransaction History - {user_name}"
    )

    table = PrettyTable()

    table.field_names = [
        "Type",
        "Description",
        "Paid By",
        "Amount",
        "Your Share",
        "Status",
        "Date"
    ]

    # -----------------------------------
    # Expenses
    # -----------------------------------

    for expense in expenses:

        description = expense[0]
        total = expense[1]
        payer = expense[2]
        split_type = expense[3]
        your_share = expense[4]
        created_at = expense[5]

        if payer == user_name:

            status = (
                f"Receive "
                f"₹{total - your_share:.2f}"
            )

        else:

            status = (
                f"Owe "
                f"₹{your_share:.2f}"
            )

        table.add_row([
            "Expense",
            description,
            payer,
            f"₹{total:.2f}",
            f"₹{your_share:.2f}",
            status,
            created_at
        ])

    # -----------------------------------
    # Payments
    # -----------------------------------

    for payment in payments:

        payer = payment[0]
        receiver = payment[1]
        amount = payment[2]
        created_at = payment[3]

        if payer == user_name:

            table.add_row([
                "Payment",
                "Payment Made",
                payer,
                f"₹{amount:.2f}",
                "-",
                f"Paid to {receiver}",
                created_at
            ])

        elif receiver == user_name:

            table.add_row([
                "Payment",
                "Payment Received",
                payer,
                f"₹{amount:.2f}",
                "-",
                f"Received from {payer}",
                created_at
            ])

    print(table)


# =========================================================
# CALCULATE BALANCES
# =========================================================

def calculate_settlements():

    total_paid = np.sum(
        expense_matrix,
        axis=1
    )

    total_owed = np.sum(
        expense_matrix,
        axis=0
    )

    net_balance = (
        total_paid - total_owed
    )

    # -----------------------------------
    # Apply recorded payments
    # -----------------------------------

    payments = get_all_payments()

    for payer, receiver, amount, created_at in payments:

        if payer not in friends:
            continue

        if receiver not in friends:
            continue

        payer_index = friends.index(
            payer
        )

        receiver_index = friends.index(
            receiver
        )

        # Payer's debt decreases
        net_balance[payer_index] += amount

        # Receiver's credit decreases
        net_balance[receiver_index] -= amount

    return net_balance


# =========================================================
# DISPLAY BALANCE SUMMARY
# =========================================================

def display_settlements():

    settlements = calculate_settlements()

    print("\n========== BALANCE SUMMARY ==========")

    table = PrettyTable()

    table.field_names = [
        "Friend",
        "Balance"
    ]

    for i, friend in enumerate(friends):

        balance = settlements[i]

        # Avoid displaying tiny floating-point values
        if abs(balance) < 0.005:

            table.add_row([
                friend,
                "Settled"
            ])

        elif balance > 0:

            table.add_row([
                friend,
                f"Should receive ₹{balance:.2f}"
            ])

        else:

            table.add_row([
                friend,
                f"Owes ₹{-balance:.2f}"
            ])

    print(table)


# =========================================================
# SUGGEST PAYMENTS
# =========================================================

def suggest_payments():

    settlements = calculate_settlements()

    creditors = [
        [
            friends[i],
            float(amount)
        ]

        for i, amount in enumerate(
            settlements
        )

        if amount > 0.005
    ]

    debtors = [
        [
            friends[i],
            float(-amount)
        ]

        for i, amount in enumerate(
            settlements
        )

        if amount < -0.005
    ]

    transactions = []

    # -----------------------------------
    # Match debtors and creditors
    # -----------------------------------

    while debtors and creditors:

        debtor, debt_amount = debtors[0]

        creditor, credit_amount = creditors[0]

        payment = min(
            debt_amount,
            credit_amount
        )

        transactions.append(
            (
                debtor,
                creditor,
                payment
            )
        )

        debt_amount -= payment

        credit_amount -= payment

        if debt_amount <= 0.005:

            debtors.pop(0)

        else:

            debtors[0][1] = debt_amount

        if credit_amount <= 0.005:

            creditors.pop(0)

        else:

            creditors[0][1] = credit_amount

    # -----------------------------------
    # Display
    # -----------------------------------

    print(
        "\n========== SUGGESTED PAYMENTS =========="
    )

    if transactions:

        for debtor, creditor, amount in transactions:

            print(
                f"{debtor} should pay "
                f"₹{amount:.2f} to {creditor}"
            )

    else:

        print(
            "Everyone is settled."
        )


# =========================================================
# RECORD PAYMENT
# =========================================================

def record_payment():

    print("\n========== RECORD PAYMENT ==========")

    print("\nAvailable users:")

    for friend in friends:
        print("-", friend)

    # -----------------------------------
    # Payer
    # -----------------------------------

    payer = input(
        "\nWho is paying? "
    ).strip()

    if payer not in friends:

        print("Invalid payer.")
        return

    # -----------------------------------
    # Receiver
    # -----------------------------------

    receiver = input(
        "Who are you paying? "
    ).strip()

    if receiver not in friends:

        print("Invalid receiver.")
        return

    if payer == receiver:

        print(
            "Payer and receiver cannot be the same."
        )

        return

    # -----------------------------------
    # Amount
    # -----------------------------------

    while True:

        try:

            amount = float(
                input(
                    "Enter payment amount: ₹"
                )
            )

            if amount <= 0:

                print(
                    "Amount must be greater than zero."
                )

                continue

            break

        except ValueError:

            print(
                "Please enter a valid amount."
            )

    # -----------------------------------
    # Save payment
    # -----------------------------------

    save_payment(
        payer,
        receiver,
        amount
    )

    print(
        "\n✅ Payment recorded successfully!"
    )


# =========================================================
# PAYMENT HISTORY
# =========================================================

def view_payment_history():

    print(
        "\n========== PAYMENT HISTORY =========="
    )

    payments = get_all_payments()

    if not payments:

        print("No payments recorded.")
        return

    table = PrettyTable()

    table.field_names = [
        "Payer",
        "Receiver",
        "Amount",
        "Date"
    ]

    for payment in payments:

        payer = payment[0]
        receiver = payment[1]
        amount = payment[2]
        created_at = payment[3]

        table.add_row([
            payer,
            receiver,
            f"₹{amount:.2f}",
            created_at
        ])

    print(table)


# =========================================================
# MAIN MENU
# =========================================================

def menu():

    while True:

        print("\n")
        print("=" * 38)
        print(
            "       EXPENSE SHARING APPLICATION"
        )
        print("=" * 38)

        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. View User Transaction History")
        print("4. View Balance Summary")
        print("5. Suggest Settlements")
        print("6. Record Payment")
        print("7. View Payment History")
        print("8. Exit")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        # -----------------------------------
        # Add Expense
        # -----------------------------------

        if choice == "1":

            add_expense()

        # -----------------------------------
        # View Expenses
        # -----------------------------------

        elif choice == "2":

            view_all_expenses()

        # -----------------------------------
        # User History
        # -----------------------------------

        elif choice == "3":

            view_user_history()

        # -----------------------------------
        # Balance
        # -----------------------------------

        elif choice == "4":

            display_settlements()

        # -----------------------------------
        # Suggestions
        # -----------------------------------

        elif choice == "5":

            suggest_payments()

        # -----------------------------------
        # Record Payment
        # -----------------------------------

        elif choice == "6":

            record_payment()

        # -----------------------------------
        # Payment History
        # -----------------------------------

        elif choice == "7":

            view_payment_history()

        # -----------------------------------
        # Exit
        # -----------------------------------

        elif choice == "8":

            print(
                "\nThank you for using "
                "Expense Sharing Application!"
            )

            break

        else:

            print(
                "Invalid choice. "
                "Please select 1-8."
            )


# =========================================================
# PROGRAM START
# =========================================================

if __name__ == "__main__":

    # Create database tables
    create_tables()

    # Load users
    initialize_users()

    # Load old expenses into matrix
    load_previous_expenses()

    # Start application
    menu()