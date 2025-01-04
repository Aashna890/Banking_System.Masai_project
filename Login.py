import sqlite3
import streamlit as aTm
import re
def setup_db():
    cus=sqlite3.connect('atm_system.db')
    cur=cus.cursor()
    cur.execute('''
    create table if not exists customer(
    cust_id integer primary key autoincrement,
    username text not null unique,
    password text not null,
    balance real default 0,
    acc_id int not null
    )
    ''')
    cus.commit()
    cus.close()

class Customer:
    def __init__(self,cust_id,username,balance=0.0):
        self.cust_id = cust_id
        self.username = username
        self.balance = balance

    def deposit(self,amount):
            if amount>0:
                self.balance+=amount
                self._update_balance()
                return f"₹{amount:.2f} Deposited sucessfully!"
            else:
                return "Invalid amount entered"
    def withdraw(self,amount):
            if 0<amount <=self.balance:
                self.balance -=amount
                self._update_balance()
                return f"₹{amount:.2f} withdrawn successfully!"
            else:
                return "Invalid amount insufficient balance."
    def _update_balance(self):
            cus =sqlite3.connect('atm_system.db')
            cur =cus.cursor()
            cur.execute("update customer set balance =? where cust_id=?",(self.balance,self.cust_id))
            cus.commit()
            cus.close()
class ATM:
    def __init__(self):
        setup_db()
    def register_customer(self,username,password):

        if len(password)<8 or len(password)>100 or not re.search(r'[A-Za-z]', password) or \
                not re.search(r'\d', password) or not re.search(r'[!@#$%^&*(),.?:{}|<>]', password):
            return ("Password must contain:"
                    "Length: At least 8 characters, but can be up to 100 characters.\n"
                    "Characters: Must include a combination of letters, numbers, and symbols. \n"
                    "Format: Cannot start or end with a blank space. \n"
                    'Avoid: Avoid common passwords like "password123". \n'
                    "Accents: Cannot include accented characters or symbols. \n"
                    )
        try:
            cus=sqlite3.connect('atm_system.db')
            cur=cus.cursor()
            cur.execute("insert into customer (username,password) values (?,?)",
                        (username,password))
            cus.commit()

            return "Registration Successful!"
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                return "Username or account already exists. Try a different one."
            else:
                return "An error occurred. Please try again."
        finally:
            cus.close()
    def login(self,username,password):
        cus=sqlite3.connect('atm_system.db')
        cur=cus.cursor()
        cur.execute("select * from customer "
                    "where username=? and password=?",(username,password))
        result=cur.fetchone()
        cus.close()
        if result:
            return Customer(cust_id=result[0],username=result[1],balance=result[3])
        else:
            return None
    def reset_pass(self,username,new_pass):
        cus=sqlite3.connect('atm_system.db')
        cur=cus.cursor()
        cur.execute("select * from customer where username = ?",(username,))
        if cur.fetchone() is None:
            cus.close()
            return "Username not found."
        cur.execute("update customer set password=? where username=?",(new_pass,username))
        cus.commit()
        cus.close()
        return "Password reset successful!"

def main():
    atm=ATM()
    aTm.title("ABC Banking System")
    aTm.subheader("Welcome to ABC Banking System!")
    if "logged_in" not in aTm.session_state:
        aTm.session_state.logged_in = False
        aTm.session_state.customer = None
    if not aTm.session_state.logged_in:
        option = aTm.selectbox("Choose an option", ["Login", "Register"])

        if option =="Register":
            aTm.subheader("Create a new Account")
            username = aTm.text_input("Username",key="reg_username")
            password = aTm.text_input("Password",type="password",key="reg_password")
            acc_id=aTm.text_input("Account number",key="reg_acc_id")

            if aTm.button("Register"):
                result=atm.register_customer(username, password)
                if "successful" in result.lower():
                    aTm.success(result)
                    aTm.button("Back to home")
                else:
                    aTm.error(result)
        elif option=="Login":
            aTm.subheader("Login to your Account")
            username=aTm.text_input("Username",key="login_username")
            password=aTm.text_input("Password",type="password",key="login_password")

            if aTm.button("Login"):
                customer=atm.login(username, password)
                if customer:
                    aTm.session_state.logged_in=True
                    aTm.session_state.customer=customer
                    aTm.success("Login Successful!")
                else:
                     aTm.error("Invalid username or password.")
            if aTm.button("Forgot Password"):
                new_pass = aTm.text_input("Enter New Password",type="password",key="new_pass")
                confirm_pass = aTm.text_input("Confirm New Password",type="password",key="confirm_pass")
                if aTm.button("Submit New Password"):
                   if new_pass and confirm_pass:
                     if new_pass==confirm_pass:
                        result=atm.reset_pass(username, new_pass)
                        aTm.success(result)
                     else:
                        aTm.error("Passwords do not match. Please try again.")

    else:
        aTm.subheader(f"Welcome, {aTm.session_state.customer.username}")
        customer=aTm.session_state.customer
        aTm.write("### Deposit Money")
        deposit_amount=aTm.number_input("Enter amount to deposit:", min_value=0.0, format="%.2f")
        if aTm.button("Deposit"):
            result=customer.deposit(deposit_amount)
            if "Sucessfully" in result:
                aTm.success(result)
            else:
                aTm.error(result)
        aTm.write("### Withdraw Money")
        withdraw_amount=aTm.number_input("Enter amount to withdraw:", 0.0, format="%.2f")
        if aTm.button("Withdraw"):
            result=customer.withdraw(withdraw_amount)
            if "successfully" in result:
                aTm.success(result)
            else:
                aTm.error(result)
        aTm.write("### Show balance")
        if aTm.button("Balance"):
           aTm.success(f"Current Balance: ₹{customer.balance:.2f}")


        if aTm.button("Logout"):
            aTm.session_state.logged_in=False
            aTm.session_state.customer=None
            aTm.info("You have been logged out.")
if __name__ == "__main__":
    main()