# views/cli_view.py example
import os
import platform

class CLIView:
    @staticmethod
    def display_menu():
        print(f'''
    Options:
        accol:\tAccounts List
        aacco:\tAdd Account
        userl:\tUsers List
        auser:\tAdd User
        empty:\tEmpty Table
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
