import argparse
import configparser
import datetime
from models.database.database import Database
from models.tables_info import Info
from models.tables.accounts import Accounts
from models.tables.users import Users
from views.cli_view import CLIView

def main(db_file):
    db = Database(db_file)
    view = CLIView()
    info = Info()

    def create_user(user_name):
        all_users = Users.fetch_all(db) 
        existing_user = next((user for user in all_users if user.name == user_name), None)
        if existing_user:
            raise Exception(f"{user_name} already exists!")
        timestamp = datetime.datetime.now()
        user = Users(name=user_name, timestamp=timestamp)
        user.save(db)
        create_account(user_name)
        print(f"{user_name} has been added!")
 
    def delete_user(user_name):
        user = next((user for user in Users.fetch_all(db) if user.name == user_name), None)
        if user == None:
            raise ValueError('User not found!')
        fuser = Users.fetch_one_by_id(db, user.id)
        accounts = Accounts.fetch_all(db)
        faccounts = [(acc) for acc in accounts if acc.user_id == fuser.id]
        fuser.delete(db)
        for acc in faccounts:
            acc.delete(db)
        print(f'Deleted: {fuser.name}')
    
    def user_info(user_name):
        users = Users.fetch_all(db)
        user = next((user for user in users if user.name == user_name), None)
        if user == None:
            raise Exception('User not found!')
        all_accounts = Accounts.fetch_all(db)
        accounts = [*(acc for acc in all_accounts if acc.user_id == user.id)]
        if accounts:
            result = [(f'Number: {acc.account_number}, Balance: {acc.balance}, IR: {acc.interest_rate}') for acc in accounts]
        else:
            result = 'No account'
        print(f'User: {user.name}, Account: {result}')
    
    def create_account(user_name):
        all_users = Users.fetch_all(db) 
        all_account = Accounts.fetch_all(db) 
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
        account.save(db)
        print(f"Account {account_number} has been added to {user_name}!")
 
    def deposit(account_number):
        acc = next((acc for acc in Accounts.fetch_all(db) if acc.account_number == account_number), None)
        if acc == None:
            raise Exception('Account not found!')
        deposit = float(input('Deposit: '))
        if deposit <= 0:
            raise Exception('The deposit must be positive! ')
        new_balance = acc.balance + deposit
        account = Accounts(id=acc.id, account_number=account_number, balance=new_balance, interest_rate=acc.interest_rate, user_id=acc.user_id, timestamp=acc.timestamp)
        account.save(db)
        print(f'{deposit} added account {account_number}. New balance: {account.balance}')
    
    def withdraw(account_number):
        acc = next((acc for acc in Accounts.fetch_all(db) if acc.account_number == account_number), None)
        if acc == None:
            raise Exception('Account not found!')
        withdraw = float(input('Withdraw: '))
        if withdraw <= 0:
            raise Exception('The withdraw must be positive! ')
        if acc.balance < withdraw:
            raise Exception('There is not enough balance in the account!')
        new_balance = acc.balance - withdraw
        account = Accounts(id=acc.id, account_number=account_number, balance=new_balance, interest_rate=acc.interest_rate, user_id=acc.user_id, timestamp=acc.timestamp)
        account.save(db)
        print(f'Account {account_number} withdrawals: {withdraw}. New balance: {account.balance}')
    
    def transfer(from_acc, to_acc):
        acc1 = next((acc for acc in Accounts.fetch_all(db) if acc.account_number == from_acc), None)
        if acc1 == None:
            raise Exception(f'{from_acc} account not found! ')
        acc2 = next((acc for acc in Accounts.fetch_all(db) if acc.account_number == to_acc), None)
        if acc2 == None:
            raise Exception(f'{to_acc} account not found! ')
        transfer = float(input('Transfer: '))
        if transfer <= 0:
            raise Exeption('Transfer must be positive!')
        if acc1.balance < transfer:
            raise Exception(f'There is not enough balance in the account {from_acc}!')
        new_balance1 = acc1.balance - transfer
        account1 = Accounts(id=acc1.id, account_number=acc1.account_number, balance=new_balance1, interest_rate=acc1.interest_rate, user_id=acc1.user_id, timestamp=acc1.timestamp)
        account1.save(db)
        new_balance2 = acc2.balance + transfer
        account2 = Accounts(id=acc2.id, account_number=acc2.account_number, balance=new_balance2, interest_rate=acc2.interest_rate, user_id=acc2.user_id, timestamp=acc2.timestamp)
        account2.save(db)
        print(f'Transfered from {from_acc} to {to_acc}: {transfer}')
    
    def delete_account(account_number):
        acc = next((acc for acc in Accounts.fetch_all(db) if acc.account_number == account_number), None)
        if acc == None:
            raise Exception('Account not found!')
        acc.delete(db)
        print(f'Deleted: {account_number}')
        
    def account_info(account_number):
        acc = next((acc for acc in Accounts.fetch_all(db) if acc.account_number == account_number), None)
        if acc == None:
            raise Exception('Account not found!')
        user = Users.fetch_one_by_id(db, acc.user_id)
        print(f'User: {user.name}, Balance: {acc.balance}, Interest Rate: {acc. interest_rate}')
    
    def apply_interest_rate(account_number):
        acc = next((acc for acc in Accounts.fetch_all(db) if acc.account_number == account_number), None)
        if acc == None:
            raise Exception('Account not found!')
        new_balance = acc.balance + (acc.balance * acc.interest_rate)
        account = Accounts(id=acc.id, account_number=account_number, balance=new_balance, interest_rate=acc.interest_rate, user_id=acc.user_id, timestamp=acc.timestamp)
        account.save(db)
        print(f'Apply interest rate account {account_number}. New balance: {account.balance}')
    
    while True:
        view.display_menu()
        choice = input("Choose an option: ")

        if choice == 'lsa':
            try:
                users = Users.fetch_all(db)
                accounts = Accounts.fetch_all(db)      
                for user in users:
                    existing_acc = [*(acc for acc in accounts if acc.user_id == user.id)]
                    if existing_acc:
                        result = [(f'Number: {acc.account_number}, Balance: {acc.balance}, IR: {acc.interest_rate}') for acc in existing_acc]
                    else:
                        result = 'No account'
                    print(f'User: {user.name}, Account: {result}')
            except Exception as error:
                print(f"Unexpected {error=}, {type(error)=}")
            
        elif choice == 'lsu':
            users = Users.fetch_all(db)
            print(f'ID:\tName:')
            print(*(f'{user.id}\t{user.name}'for user in users), sep='\n')
        
        elif choice == 'tinf':
            print('Tables and they columns: ')
            [print(k, d) for k, d in info.table_colnames.items()]

        elif choice == 'au':
            try:
                user_name = input("Add User: ")
                create_user(user_name)
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == 'du':
            try:
                user_name = input("Delete User: ")
                delete_user(user_name)
            except ValueError as e:
                print(f'\n{str(e)}')
                
        elif choice == 'ui':
            try:
                user_name = input("User name: ")
                user_info(user_name)
            except Exception as error:
                print(f"\n {str(error)}")
        
        elif choice == 'ca':
            user_name = input("User name: ")
            create_account(user_name)
            
        elif choice == 'd':
            try:
                account_number = int(input('Account number: '))
                deposit(account_number)
            except Exception as error:
                print(f"\n {str(error)}")
        
        elif choice == 'w':
            try:
                account_number = int(input('Account number: '))
                withdraw(account_number)
            except Exception as error:
                print(f"\n {str(error)}")
        
        elif choice == 't':
            try:
                from_acc = int(input('From Account: '))
                to_acc = int(input('To Account: '))
                transfer(from_acc, to_acc)
            except Exception as error:
                print(f"\n {str(error)}")
        
        elif choice == 'da':
            try:
                account_number = int(input("Account number: "))
                delete_account(account_number)
            except Exception as error:
                print(f"\n {str(error)}")
            
        elif choice == 'ai':
            try:
                account_number = int(input("Account number: "))
                account_info(account_number)
            except Exception as error:
                print(f"\n {str(error)}")
        
        elif choice == 'ir':
            try:
                account_number = int(input("Account number: "))
                apply_interest_rate(account_number)
            except Exception as error:
                print(f"\n {str(error)}")

        elif choice == 'cls':
            view.cls()
         
        elif choice == 'test':
            query = f"PRAGMA table_info('accounts');"
            columns = db.fetchall(query)
            table_info = [{'name': col['name'], 'type': col['type'], 'notnull': col['notnull'], 'dflt_value': col['dflt_value'], 'pk': col['pk']} for col in columns]
            columns = [colinfo['name'] for colinfo in table_info if colinfo['pk'] != 1]
            print(len(table_info))
            print([info.table_info['users'][i]['type'] for i in range(0, len(info.table_info['users']))])
        
        elif choice == 'q':
            db.close()
            view.cls()
            print(f"\nGoodbye!")
            break

if __name__ == '__main__':
    # Argumentumok beolvasása
    parser = argparse.ArgumentParser(description="Main script.")
    parser.add_argument("--db_file", type=str, help="Az adatbázis fájl elérési útja.")
    parser.add_argument("--config", type=str, default="config_migrate.ini", help="A konfigurációs fájl elérési útja.")

    args = parser.parse_args()

    # Konfigurációs fájl beolvasása
    config = configparser.ConfigParser()
    config.read(args.config)

    # Argumentumok vagy konfigurációs fájl használata
    db_file = args.db_file or config["Paths"]["db_file"]

    main(db_file)
