import sqlite3


# -----------------------------------
# Database connection
# -----------------------------------

def connect_db():
    connection = sqlite3.connect("expenses.db")
    return connection


# -----------------------------------
# Create database tables
# -----------------------------------

def create_tables():

    connection = connect_db()
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            payer TEXT NOT NULL,
            split_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Expense splits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_splits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            amount_owed REAL NOT NULL,
            FOREIGN KEY (expense_id) REFERENCES expenses(id)
        )
    """)

    # Payments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payer TEXT NOT NULL,
            receiver TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# -----------------------------------
# Add user
# -----------------------------------

def add_user(name):

    connection = connect_db()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO users (name)
            VALUES (?)
        """, (name,))

        connection.commit()

    except sqlite3.IntegrityError:
        # User already exists
        pass

    connection.close()


# -----------------------------------
# Get all users
# -----------------------------------

def get_users():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM users
        ORDER BY id
    """)

    users = cursor.fetchall()

    connection.close()

    # Convert [('a',), ('b',)] to ['a', 'b']
    return [user[0] for user in users]


# -----------------------------------
# Save expense
# -----------------------------------

def save_expense(
    description,
    amount,
    payer,
    split_type,
    splits
):

    connection = connect_db()
    cursor = connection.cursor()

    # Insert expense
    cursor.execute("""
        INSERT INTO expenses
        (description, amount, payer, split_type)
        VALUES (?, ?, ?, ?)
    """, (
        description,
        amount,
        payer,
        split_type
    ))

    expense_id = cursor.lastrowid

    # Insert individual splits
    for user_name, amount_owed in splits:

        cursor.execute("""
            INSERT INTO expense_splits
            (expense_id, user_name, amount_owed)
            VALUES (?, ?, ?)
        """, (
            expense_id,
            user_name,
            amount_owed
        ))

    connection.commit()
    connection.close()

    return expense_id


# -----------------------------------
# Get all expenses
# -----------------------------------

def get_all_expenses():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            description,
            amount,
            payer,
            split_type,
            created_at
        FROM expenses
        ORDER BY id
    """)

    expenses = cursor.fetchall()

    connection.close()

    return expenses


# -----------------------------------
# Get expense splits
# -----------------------------------

def get_expense_splits(expense_id):

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            user_name,
            amount_owed
        FROM expense_splits
        WHERE expense_id = ?
    """, (expense_id,))

    splits = cursor.fetchall()

    connection.close()

    return splits


# -----------------------------------
# Get all expense splits
# Used to rebuild balance matrix
# -----------------------------------

def get_all_expense_splits():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            e.payer,
            s.user_name,
            s.amount_owed
        FROM expenses e
        JOIN expense_splits s
        ON e.id = s.expense_id
        ORDER BY e.id
    """)

    splits = cursor.fetchall()

    connection.close()

    return splits


# -----------------------------------
# Get expenses for a specific user
# -----------------------------------

def get_user_expenses(user_name):

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            e.description,
            e.amount,
            e.payer,
            e.split_type,
            s.amount_owed,
            e.created_at
        FROM expenses e
        JOIN expense_splits s
        ON e.id = s.expense_id
        WHERE s.user_name = ?
        ORDER BY e.id
    """, (user_name,))

    expenses = cursor.fetchall()

    connection.close()

    return expenses


# -----------------------------------
# Save payment
# -----------------------------------

def save_payment(payer, receiver, amount):

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO payments
        (payer, receiver, amount)
        VALUES (?, ?, ?)
    """, (
        payer,
        receiver,
        amount
    ))

    connection.commit()
    connection.close()


# -----------------------------------
# Get all payments
# -----------------------------------

def get_all_payments():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            payer,
            receiver,
            amount,
            created_at
        FROM payments
        ORDER BY id
    """)

    payments = cursor.fetchall()

    connection.close()

    return payments