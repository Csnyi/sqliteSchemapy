# views/cli_view.py example
import os
import platform

class CLIView:
    @staticmethod
    def display_menu():
        print(f'''
    Options:
        tij:\tTables Join Valid List
        accol:\tAccounts List
        userl:\tUsers List
        addrl:\tAddress List
        add:\tAdd Table Required
        update:\tUpdate Table Column
        del:\tDelete by table and id
        ct:\tCreate Table
        empty:\tEmpty Table
        bd:\tBackup Database
        rd:\tRestore Database
        fka:\tForeign key
        sql:\tSql by table
        cls:\tClear Screen
        q:\tQuit
    ''')

    @staticmethod
    def get_user_input(prompt):
        return input(prompt)

    @staticmethod
    def display_message(message):
        print(message)

    @staticmethod
    def cls():
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
