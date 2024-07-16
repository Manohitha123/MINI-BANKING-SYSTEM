import sqlite3
import os


# BankAccount Class
class BankAccount:
    def __init__(self, conn):
        self.conn = conn
        self.cur = conn.cursor()

    def create_database(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS BankTable (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL,
                            mobile_num TEXT NOT NULL,
                            balance REAL DEFAULT 0
                        )""")
        self.conn.commit()

    def sign_up(self, name, password, mobile_num):
        try:
            self.cur.execute("""INSERT INTO BankTable (name, password, mobile_num)
                               VALUES (?, ?, ?)""", (name, password, mobile_num))
            self.conn.commit()
            print("Account created successfully")

            # Save user data to file
            self.save_user_data(name, password, mobile_num)
        except sqlite3.IntegrityError:
            print("User already exists with that name.")
        except Exception as e:
            print(e)

    def sign_in(self, name, password):
        try:
            self.cur.execute("""SELECT * FROM BankTable WHERE name = ? AND password = ?""", (name, password))
            data = self.cur.fetchone()
            if data:
                print("Login Successful :) ")
                return BankUser(self.conn, data)
            else:
                print("Login Failed  :( ")
                return None
        except Exception as e:
            print(e)
            return None

    def close(self):
        self.cur.close()
        self.conn.close()

    def save_user_data(self, name, password, mobile_num):
        try:
            filename = f"{name}.txt"
            with open(filename, 'w') as file:
                file.write(f"Name: {name}\n")
                file.write(f"Password: {password}\n")
                file.write(f"Mobile Number: {mobile_num}\n")
        except Exception as e:
            print(f"Error saving user data for {name}: {e}")


# BankUser Class
class BankUser:
    def __init__(self, conn, data):
        self.conn = conn
        self.cur = conn.cursor()
        self.id = data[0]
        self.name = data[1]
        self.password = data[2]
        self.mobile_num = data[3]
        self.balance = data[4]

    def view_profile(self):
        try:
            print("      Your Profile")
            print(f" ID           : {self.id}")
            print(f" Name         : {self.name}")
            print(f" Mobile Number: {self.mobile_num}")
            print(f" Balance      : Rs. {self.balance}")
        except Exception as e:
            print(e)

    def check_balance(self):
        try:
            print(f"Current Balance: Rs. {self.balance}")
        except Exception as e:
            print(e)

    def withdraw(self, amount):
        try:
            if amount > 0:
                if amount <= self.balance:
                    self.cur.execute("""UPDATE BankTable SET balance = balance - ? WHERE name = ?""",
                                     (amount, self.name))
                    self.conn.commit()
                    self.balance -= amount
                    print(f"Withdrawal of Rs. {amount} successful.")
                else:
                    print("Insufficient Balance.")
            else:
                print("Please enter a valid amount.")
        except Exception as e:
            print(e)

    def deposit(self, amount):
        try:
            if amount > 0:
                self.cur.execute("""UPDATE BankTable SET balance = balance + ? WHERE name = ?""",
                                 (amount, self.name))
                self.conn.commit()
                self.balance += amount
                print(f"Deposit of Rs. {amount} successful.")
            else:
                print("Please enter a valid amount.")
        except Exception as e:
            print(e)

    def transfer_money(self, receiver_name, amount):
        try:
            self.cur.execute("""SELECT * FROM BankTable WHERE name = ?""", (receiver_name,))
            receiver_data = self.cur.fetchone()
            if receiver_data:
                if amount > 0:
                    if amount <= self.balance:
                        self.cur.execute("""UPDATE BankTable SET balance = balance - ? WHERE name = ?""",
                                         (amount, self.name))
                        self.cur.execute("""UPDATE BankTable SET balance = balance + ? WHERE name = ?""",
                                         (amount, receiver_name))
                        self.conn.commit()
                        self.balance -= amount
                        print(f"Transfer of Rs. {amount} to '{receiver_name}' successful.")
                    else:
                        print("Insufficient Balance.")
                else:
                    print("Please enter a valid amount.")
            else:
                print(f"Receiver '{receiver_name}' not found.")
        except Exception as e:
            print(e)

    def delete_account(self):
        try:
            self.cur.execute("""DELETE FROM BankTable WHERE name = ?""", (self.name,))
            self.conn.commit()
            print("Your Account has been deleted successfully.")

            # Delete user data file
            filename = f"{self.name}.txt"
            if os.path.exists(filename):
                os.remove(filename)
                print(f"User data file {filename} deleted.")
            else:
                print(f"User data file {filename} not found.")
        except Exception as e:
            print(e)

    def close(self):
        self.cur.close()


# Main Function
def main():
    try:
        conn = sqlite3.connect("BankDatabase.db")
        bank = BankAccount(conn)
        bank.create_database()

        while True:
            print("")
            print("_____________________________________________________")
            print("*********   Welcome   *****************")
            print("------------------------------------------------------")
            print("")
            print("1-- Sign Up")
            print("2-- Sign in")
            print("3-- Exit")

            try:
                choice = int(input("Enter the Option: "))
                if choice == 1:
                    name = input("Enter your name: ")
                    password = input("Enter your password: ")
                    mobile_num = input("Enter your mobile number: ")
                    bank.sign_up(name, password, mobile_num)
                elif choice == 2:
                    name = input("Enter the name: ")
                    password = input("Enter the password: ")
                    user = bank.sign_in(name, password)
                    if user:
                        user_operations(user)
                elif choice == 3:
                    print("Exiting the application.")
                    break
                else:
                    print("Enter a valid option.")
            except ValueError:
                print("Enter a numeric option.")
            except Exception as e:
                print(e)
    finally:
        conn.close()


# User Operations
def user_operations(user):
    while True:
        try:
            print("")
            print("_____________________________________________________")
            print("*********Welcome to the user operations page**********")
            print("------------------------------------------------------")
            print("")
            print("1--  View Profile     ==>")
            print("2--  Check Balance    ==>")
            print("3--  Withdraw Amount  ==>")
            print("4--  Deposit Amount   ==>")
            print("5--  Transfer Money   ==>")
            print("6--  Delete Account   ==>")
            print("7--  Logout           ==>")

            choice = int(input("Enter your option: "))
            if choice == 1:
                user.view_profile()
            elif choice == 2:
                user.check_balance()
            elif choice == 3:
                amount = float(input("Enter the amount to withdraw: Rs. "))
                user.withdraw(amount)
            elif choice == 4:
                amount = float(input("Enter the amount to deposit: Rs. "))
                user.deposit(amount)
            elif choice == 5:
                receiver_name = input("Enter the receiver's name: ")
                amount = float(input("Enter the amount to transfer: Rs. "))
                user.transfer_money(receiver_name, amount)
            elif choice == 6:
                user.delete_account()
                break
            elif choice == 7:
                print("Thank you, You have been logged out of this account!!!")
                break
            else:
                print("Invalid input")
        except ValueError:
            print("Please input a valid option.")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
