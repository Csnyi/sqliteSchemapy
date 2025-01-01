# views/cli_view.py
import os
import platform

class CLIView:
    @staticmethod
    def display_menu():
        print(f'''
    Options:
        lsa:\tAccounts List
        lsu:\tUsers List
        tinf:\tTables columns Info
        au:\tAdd User
        du:\tDelete User
        ui:\tUser Info
        ca:\tCreate Account
        d:\tDeposit
        w:\tWithdraw
        t:\tTransfer
        da:\tDelete Account
        ai:\tAccount Info
        ir:\tApply Interest Rate
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