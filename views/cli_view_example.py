# views/cli_view.py
import os
import platform

class CLIView:
    @staticmethod
    def display_menu():
        print(f'''
    Options:
        accounts-list:\tAccounts List
        users-list:\tUsers List
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