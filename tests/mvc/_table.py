from cli_controller import Controller

def main(db):
    controller = Controller(db)
    
    options = f'''
    Options: 
        dblist\t - List table names
        list\t - List table rows
        add\t - Add data
        upd\t - Update data
        updcust\t - Update customize data
        del\t - Delete data
        cols\t - Show table columns
       req_cols\t - Show required columns
        add_col\t - Add column to table with default constant
        ex\t - Execute custom query
        q\t - Quit
    '''

    while True:
        print(options)
        choice = input("Option: ").strip().lower()

        if choice == "dblist":
            controller.list_table()

        elif choice in {"list", "add", "upd", "updcust", "del", "cols", "req_cols", "add_col"}:
            table = controller.choice_table()

            if table:
                
                if choice == "list":
                    controller.list_table_rows(table)
                    
                elif choice == "add":
                    controller.add_row(table)
                    
                elif choice == "upd":
                    controller.update_by_id(table)
                
                elif choice == "updcust":
                    controller.update_customize(table)
                    
                elif choice == "del":
                    try:
                        controller.delete_row(table)
                    except Exception as e:
                        print(e)
                
                elif choice == "cols":
                    print(f"{table.table_name} columns: {table.columns}")
    
                elif choice == "req_cols":
                    print(f"{table.table_name} required columns: {table.required_columns}")
    
                elif choice == "add_col":
                     controller.add_column(table)
            
            else:
                continue
    
        elif choice == "ex":
            controller.execute_query()

        elif choice == "q":
            controller.quit()
            break

        else:
            print(f"Invalid option: {choice}")

if __name__ == "__main__":
    main("../../db/bank.db")

