#controllers/bank_controller.py
import datetime
from models.tables.accounts import Accounts
from models.tables.users import Users

class BankController:
    def __init__(self, db):
        self.db = db

    def list_accounts(self):
        users = Users.fetch_all(self.db)
        accounts = Accounts.fetch_all(self.db)      
        for user in users:
            existing_acc = [*(acc for acc in accounts if acc.user_id == user.id)]
            if existing_acc:
                result = [(f'Number: {acc.account_number}, Balance: {acc.balance}, IR: {acc.interest_rate} Created at: {acc.timestamp}') for acc in existing_acc]
            else:
                result = 'No account'
            print(f'User: {user.name}, Account: {result}')
    
    def list_users(self):
        users = Users.fetch_all(self.db)
        print(f'ID:\tName:')
        print(*(f'{user.id}\t{user.name}'for user in users), sep='\n')
    
    def create_user(self, user_name):
        all_users = Users.fetch_all(self.db) 
        existing_user = next((user for user in all_users if user.name == user_name), None)
        if existing_user:
            raise Exception(f"{user_name} already exists!")
        timestamp = datetime.datetime.now()
        user = Users(name=user_name, timestamp=timestamp)
        user.save(self.db)
        self.create_account(user_name)
        print(f"{user_name} has been added!")
 
    def delete_user(self, user_name):
        user = next((user for user in Users.fetch_all(self.db) if user.name == user_name), None)
        if user == None:
            raise ValueError('User not found!')
        fuser = Users.fetch_one_by_id(self.db, user.id)
        accounts = Accounts.fetch_all(self.db)
        faccounts = [(acc) for acc in accounts if acc.user_id == fuser.id]
        fuser.delete(self.db)
        for acc in faccounts:
            acc.delete(self.db)
        print(f'Deleted: {fuser.name}')
    
    def user_info(self, user_name):
        users = Users.fetch_all(self.db)
        user = next((user for user in users if user.name == user_name), None)
        if user == None:
            raise Exception('User not found!')
        all_accounts = Accounts.fetch_all(self.db)
        accounts = [*(acc for acc in all_accounts if acc.user_id == user.id)]
        if accounts:
            result = [(f'Number: {acc.account_number}, Balance: {acc.balance}, IR: {acc.interest_rate}') for acc in accounts]
        else:
            result = 'No account'
        print(f'User: {user.name}, Account: {result}')
    
    def create_account(self, user_name):
        all_users = Users.fetch_all(self.db) 
        all_account = Accounts.fetch_all(self.db)
        user = next((user for user in all_users if user.name == user_name), None)
        if user == None:
            raise Exception(f'User not found!')
        account_number = int(input("Account number: "))
        existing_acc = next((acc for acc in all_account if acc.account_number == account_number), None)
        if existing_acc:
            raise Exception(f"{account_number} already exists!")
        timestamp = datetime.datetime.now()
        deposit = float(input('Deposit: '))
        interest_rate = float(input('Interest Rate: '))
        account = Accounts(account_number=account_number, balance=deposit, interest_rate=interest_rate, user_id=user.id, timestamp=timestamp)
        account.save(self.db)
        print(f"Account {account_number} has been added to {user_name}!")
 
    def deposit(self, account_number):
        acc = next((acc for acc in Accounts.fetch_all(self.db) if acc.account_number == account_number), None)
        if acc == None:
            raise Exception('Account not found!')
        deposit = float(input('Deposit: '))
        if deposit <= 0:
            raise Exception('The deposit must be positive! ')
        new_balance = acc.balance + deposit
        account = Accounts(id=acc.id, account_number=account_number, balance=new_balance, interest_rate=acc.interest_rate, user_id=acc.user_id, timestamp=acc.timestamp)
        account.save(self.db)
        print(f'{deposit} added account {account_number}. New balance: {account.balance}')
    
    def withdraw(self, account_number):
        acc = next((acc for acc in Accounts.fetch_all(self.db) if acc.account_number == account_number), None)
        if acc == None:
            raise Exception('Account not found!')
        withdraw = float(input('Withdraw: '))
        if withdraw <= 0:
            raise Exception('The withdraw must be positive! ')
        if acc.balance < withdraw:
            raise Exception('There is not enough balance in the account!')
        new_balance = acc.balance - withdraw
        account = Accounts(id=acc.id, account_number=account_number, balance=new_balance, interest_rate=acc.interest_rate, user_id=acc.user_id, timestamp=acc.timestamp)
        account.save(self.db)
        print(f'Account {account_number} withdrawals: {withdraw}. New balance: {account.balance}')
    
    def transfer(self, from_acc, to_acc):
        acc1 = next((acc for acc in Accounts.fetch_all(self.db) if acc.account_number == from_acc), None)
        if acc1 == None:
            raise Exception(f'{from_acc} account not found! ')
        acc2 = next((acc for acc in Accounts.fetch_all(self.db) if acc.account_number == to_acc), None)
        if acc2 == None:
            raise Exception(f'{to_acc} account not found! ')
        transfer = float(input('Transfer: '))
        if transfer <= 0:
            raise Exeption('Transfer must be positive!')
        if acc1.balance < transfer:
            raise Exception(f'There is not enough balance in the account {from_acc}!')
        new_balance1 = acc1.balance - transfer
        account1 = Accounts(id=acc1.id, account_number=acc1.account_number, balance=new_balance1, interest_rate=acc1.interest_rate, user_id=acc1.user_id, timestamp=acc1.timestamp)
        account1.save(self.db)
        new_balance2 = acc2.balance + transfer
        account2 = Accounts(id=acc2.id, account_number=acc2.account_number, balance=new_balance2, interest_rate=acc2.interest_rate, user_id=acc2.user_id, timestamp=acc2.timestamp)
        account2.save(self.db)
        print(f'Transfered from {from_acc} to {to_acc}: {transfer}')
    
    def delete_account(self, account_number):
        acc = next((acc for acc in Accounts.fetch_all(self.db) if acc.account_number == account_number), None)
        if acc == None:
            raise Exception('Account not found!')
        acc.delete(self.db)
        print(f'Deleted: {account_number}')
        
    def account_info(self, account_number):
        acc = next((acc for acc in Accounts.fetch_all(self.db) if acc.account_number == account_number), None)
        if acc == None:
            raise Exception('Account not found!')
        user = Users.fetch_one_by_id(self.db, acc.user_id)
        print(f'User: {user.name}, Balance: {acc.balance}, Interest Rate: {acc. interest_rate}')
    
    def apply_interest_rate(self, account_number):
        acc = next((acc for acc in Accounts.fetch_all(self.db) if acc.account_number == account_number), None)
        if acc == None:
            raise Exception('Account not found!')
        new_balance = acc.balance + (acc.balance * acc.interest_rate)
        account = Accounts(id=acc.id, account_number=account_number, balance=new_balance, interest_rate=acc.interest_rate, user_id=acc.user_id, timestamp=acc.timestamp)
        account.save(self.db)
        print(f'Apply interest rate account {account_number}. New balance: {account.balance}')
   