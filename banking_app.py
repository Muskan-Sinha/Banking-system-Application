import mysql.connector
import re
import random

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0022"
    )

def create_database():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS banking_system")
    conn.commit()
    conn.close()

def connect_db_with_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0022",
        database="banking_system"
    )

def create_tables():
    conn = connect_db_with_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            account_number VARCHAR(10) UNIQUE NOT NULL,
            dob DATE NOT NULL,
            city VARCHAR(100),
            password VARCHAR(255) NOT NULL,
            balance DECIMAL(10, 2) NOT NULL,
            contact_number VARCHAR(15) UNIQUE NOT NULL,
            email_id VARCHAR(255) UNIQUE NOT NULL,
            address TEXT,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            account_number VARCHAR(10),
            transaction_type VARCHAR(50),
            amount DECIMAL(10, 2),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def validate_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)

def validate_contact(contact):
    return re.match(r'^\d{10}$', contact)

def validate_password(password):
    return len(password) >= 8 and any(c.isdigit() for c in password) and any(c.isalpha() for c in password)

def add_user():
    conn = connect_db_with_db()
    cursor = conn.cursor()

    name = input("Enter Name: ")
    dob = input("Enter Date of Birth (YYYY-MM-DD): ")
    city = input("Enter City: ")
    password = input("Enter Password: ")
    while not validate_password(password):
        print("Password must be at least 8 characters long and contain both letters and numbers.")
        password = input("Enter Password: ")

    balance = float(input("Enter Initial Balance (minimum 2000): "))
    while balance < 2000:
        print("Initial balance must be at least 2000.")
        balance = float(input("Enter Initial Balance (minimum 2000): "))

    contact_number = input("Enter Contact Number: ")
    while not validate_contact(contact_number):
        print("Invalid contact number. It must be 10 digits.")
        contact_number = input("Enter Contact Number: ")

    email_id = input("Enter Email ID: ")
    while not validate_email(email_id):
        print("Invalid email format.")
        email_id = input("Enter Email ID: ")

    address = input("Enter Address: ")
    account_number = str(random.randint(1000000000, 9999999999))

    try:
        cursor.execute("""
            INSERT INTO users (name, account_number, dob, city, password, balance, contact_number, email_id, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, account_number, dob, city, password, balance, contact_number, email_id, address))
        conn.commit()
        print(f"User added successfully! Account Number: {account_number}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()

def show_users():
    conn = connect_db_with_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

def login():
    conn = connect_db_with_db()
    cursor = conn.cursor()

    account_number = input("Enter Account Number: ")
    password = input("Enter Password: ")

    cursor.execute("SELECT * FROM users WHERE account_number = %s AND password = %s AND is_active = TRUE", (account_number, password))
    user = cursor.fetchone()

    if user:
        print("\nLogin Successful!")
        while True:
            print("\n1. Show Balance")
            print("2. Show Transactions")
            print("3. Credit Amount")
            print("4. Debit Amount")
            print("5. Transfer Amount")
            print("6. Activate/Deactivate Account")
            print("7. Change Password")
            print("8. Update Profile")
            print("9. Logout")
            choice = input("Enter your choice: ")

            if choice == '1':
                print(f"Your Balance: {user[6]}")

            elif choice == '2':
                cursor.execute("SELECT * FROM transactions WHERE account_number = %s", (account_number,))
                transactions = cursor.fetchall()
                for t in transactions:
                    print(t)

            elif choice == '3':
                amount = float(input("Enter amount to credit: "))
                cursor.execute("UPDATE users SET balance = balance + %s WHERE account_number = %s", (amount, account_number))
                cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, 'Credit', %s)", (account_number, amount))
                conn.commit()
                print("Amount credited successfully!")

            elif choice == '4':
                amount = float(input("Enter amount to debit: "))
                if user[6] >= amount:
                    cursor.execute("UPDATE users SET balance = balance - %s WHERE account_number = %s", (amount, account_number))
                    cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, 'Debit', %s)", (account_number, amount))
                    conn.commit()
                    print("Amount debited successfully!")
                else:
                    print("Insufficient balance!")

            elif choice == '5':
                target_account = input("Enter target account number: ")
                amount = float(input("Enter amount to transfer: "))
                if user[6] >= amount:
                    cursor.execute("UPDATE users SET balance = balance - %s WHERE account_number = %s", (amount, account_number))
                    cursor.execute("UPDATE users SET balance = balance + %s WHERE account_number = %s", (amount, target_account))
                    cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, 'Transfer Out', %s)", (account_number, amount))
                    cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, 'Transfer In', %s)", (target_account, amount))
                    conn.commit()
                    print("Amount transferred successfully!")
                else:
                    print("Insufficient balance!")

            elif choice == '6':
                new_status = not user[9]
                cursor.execute("UPDATE users SET is_active = %s WHERE account_number = %s", (new_status, account_number))
                conn.commit()
                print("Account status updated successfully!")

            elif choice == '7':
                new_password = input("Enter new password: ")
                while not validate_password(new_password):
                    print("Password must be at least 8 characters long and contain both letters and numbers.")
                    new_password = input("Enter new password: ")
                cursor.execute("UPDATE users SET password = %s WHERE account_number = %s", (new_password, account_number))
                conn.commit()
                print("Password changed successfully!")

            elif choice == '8':
                print("Update Profile")
                new_city = input("Enter new city: ")
                new_contact = input("Enter new contact number: ")
                while not validate_contact(new_contact):
                    print("Invalid contact number. It must be 10 digits.")
                    new_contact = input("Enter new contact number: ")
                new_email = input("Enter new email: ")
                while not validate_email(new_email):
                    print("Invalid email format.")
                    new_email = input("Enter new email: ")
                new_address = input("Enter new address: ")
                cursor.execute("UPDATE users SET city = %s, contact_number = %s, email_id = %s, address = %s WHERE account_number = %s", (new_city, new_contact, new_email, new_address, account_number))
                conn.commit()
                print("Profile updated successfully!")

            elif choice == '9':
                print("Logged out successfully!")
                break

            else:
                print("Invalid choice. Please try again.")
    else:
        print("Invalid account number or password, or the account is inactive.")
    conn.close()

def main():
    create_database()
    create_tables()
    while True:
        print("\nBANKING SYSTEM")
        print("1. Add User")
        print("2. Show Users")
        print("3. Login")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_user()
        elif choice == '2':
            show_users()
        elif choice == '3':
            login()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
