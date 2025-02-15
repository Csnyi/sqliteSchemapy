# migration/cli_view_migrate.py

def cli_view_migrate(textwrap, table_info, cli_view):

    display_menu = textwrap.dedent(f'''\
        print(f\'\'\'
        {"":>16}Options:
    ''')
    for table_name in table_info:
        class_name = table_name.capitalize()
        option = table_name[:4]
        display_menu += f'''\
            {"":>8}{option}l:\\t{class_name} List\n'''

    display_menu += f'''\
        {"":>12}add:\\tAdd Row
        {"":>12}del:\\tDelete Row
        {"":>12}up:\\tUpdate Columns
        {"":>12}empty:\\tEmpty Table
        {"":>12}cls:\\tClear Screen
        {"":>12}q:\\tQuit
        {"":>8}\'\'\')'''

    with open(cli_view, 'w') as f:
        content = textwrap.dedent(f'''\
            # {cli_view}
            import os
            import platform

            class CLIView:
                @staticmethod
                def display_menu():
                    {display_menu}

                @staticmethod
                def cls():
                    if platform.system() == "Windows":
                        os.system("cls")
                    else:
                        os.system("clear")
        ''')
        f.write(content)
