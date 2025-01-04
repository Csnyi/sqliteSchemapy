import argparse
import configparser
from models.database.database_example import Database
from models.tables_info_example import Info
from controllers.controller_example import BankController
from views.cli_view_example import CLIView

def main(db_file):
    db = Database(db_file)
    view = CLIView()
    info = Info()
    bank = BankController(db)
 
    while True:
        view.display_menu()
        choice = input("Choose an option: ")

        if choice == 'lsa':
            try:
                bank.list_accounts()
            except Exception as error:
                print(f"Unexpected {error=}, {type(error)=}")
            
        elif choice == 'lsu':
            try:
                bank.list_users()
            except Exception as error:
                print(f"Unexpected {error=}, {type(error)=}")

        elif choice == 'cu':
            try:
                user_name = input("Add User: ")
                bank.create_user(user_name)
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == 'du':
            try:
                user_name = input("Delete User: ")
                bank.delete_user(user_name)
            except ValueError as e:
                print(f'\n{str(e)}')
                
        elif choice == 'ui':
            try:
                user_name = input("User name: ")
                bank.user_info(user_name)
            except Exception as error:
                print(f"\n {str(error)}")
        
        elif choice == 'ca':
            try:
                user_name = input("User name: ")
                bank.create_account(user_name)
            except Exception as error:
                print(f"\n {str(error)}")
            
        elif choice == 'd':
            try:
                account_number = int(input('Account number: '))
                bank.deposit(account_number)
            except Exception as error:
                print(f"\n {str(error)}")
        
        elif choice == 'w':
            try:
                account_number = int(input('Account number: '))
                bank.withdraw(account_number)
            except Exception as error:
                print(f"\n {str(error)}")
        
        elif choice == 't':
            try:
                from_acc = int(input('From Account: '))
                to_acc = int(input('To Account: '))
                bank.transfer(from_acc, to_acc)
            except Exception as error:
                print(f"\n {str(error)}")
        
        elif choice == 'da':
            try:
                account_number = int(input("Account number: "))
                bank.delete_account(account_number)
            except Exception as error:
                print(f"\n {str(error)}")
            
        elif choice == 'ai':
            try:
                account_number = int(input("Account number: "))
                bank.account_info(account_number)
            except Exception as error:
                print(f"\n {str(error)}")
        
        elif choice == 'ir':
            try:
                account_number = int(input("Account number: "))
                bank.apply_interest_rate(account_number)
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
