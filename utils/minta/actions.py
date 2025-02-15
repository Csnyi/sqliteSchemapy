# views/actions.py

def actions(db_file, db, controller, view, valid, deleter):
    '''db = Database(db_file)
    controller = TablesController(db)
    view = CLIView()
    valid = Validator(db)
    deleter = GenerateDeleter(db)'''

    # The more functions...
    # For example:
    while True:
        view.display_menu()
        choice = input("Option: ")

        if choice == "tij":
            try:
                controller.table_inner()
            except Exception as e:
                print(e)
        
        elif choice == "tl":
            try:
                for table in valid.table_info:
                    print(table)
            except Exception as error:
                print(f"\n{str(error)}")
        
        elif choice == "accol":
            try:
                controller.get_list("accounts")
            except Exception as error:
                print(f"\n{str(error)}")
        
        elif choice == "userl":
            try:
                controller.get_list("users")
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "addrl":
            try:
                controller.get_list("address")
            except Exception as error:
                print(f"\n{str(error)}")
        
        elif choice == "add":
            try:
                table = input("Table name: ")
                message = controller.add_data(table)
                print(message)
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "update_required":
            try:
                table = input("Table name: ")
                message = controller.add_data(table, True)
                print(message)
            except Exception as error:
                print(f"\n{str(error)}")
        
        elif choice == "update":
            try:
                table = input("Table name: ")
                cols = input("Cols: ").split(", ")
                state = input("Satement: ")
                params = input("Params: ").split(", ")
                controller.update(table, cols, state, params)
                print(f"Update {cols} where {state} to {params}")
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "del":
            try:
                table = input("Table: ")
                id = input("Id: ")
                controller.delete(table, id)
                print(f"The {table} {id} has been deleted!")
            except Exception as e:
                print(e)
                if "not found" in str(e):
                    main(db_file)
                choice = input("Delete related data? (Y/n): ")
                if choice == "n":
                    print("It was not deleted.")
                else:
                    try:
                        message = controller.delete_data(table, id)
                        print(message)
                    except Exception as e:
                        print(e)
  
        elif choice == "ct":
            try:
                table = input("Table name: ")
                statement = input("Statement: ")
                db.create_table(table, statement)
                print("Done!")
            except Exception as e:
                print(e)

        elif choice == "empty":
            try:
                table = input("Table name: ")
                controller.empty_table(table)
                print(f"{table} emptied!")
            except Exception as e:
                print(e)
        
        elif choice == "bd":
            try:
                file_path = f"{db_file}.sql" 
                db.backup(file_path)
                print(f"Save to {file_path}.")
            except Exception as e:
                print(e)
        
        elif choice == "rd":
            try:
                file_path = f"{db_file}.sql"
                controller.empty_table("accounts")
                controller.empty_table("address")
                controller.empty_table("users")
                controller.restore(file_path)
                print(f"{file_path} restore done!")
            except Exception as e:
                print(e)
        
        elif choice == "fka":
            print(valid.get_foreign_key_list_all())
            
        elif choice == "sql":
            try:
                sql = db.get_sql()
                table = input("Table name: ")
                if table not in sql:
                    raise Exception("Table not found!")
                print(sql[table])
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "cls":
            view.cls()

        elif choice == "q":
            db.close()
            view.cls()
            print("Goodby!")
            break 

        #----------------- off the menu

        elif choice == "gil":
            try:
                index_list = db.get_indexes()
                if index_list:
                    for index in index_list:
                        print(*index)
                else:
                    print("The index list is empty!")
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "cui":
            try:
                index_name = input("Index name: ")
                table = input("Table: ")
                column = input("Column: ")
                db.create_unique_index(index_name, table, column)
                print(f"Unique index ({table}.{column}) hes been created!")
            except Exception as error:
                print(f"\n{str(error)}")

        elif choice == "di":
            try:
                index_name = input("Index name: ")
                db.drop_index(index_name)
                print(f"{index_name} index dropped!")
            except Exception as error:
                print(f"\n{str(error)}")
        
        elif choice == "chfk":
            try:
                table = input("table: ")
                cfk = controller.check_foreign_key(table)
                if cfk == None:
                    print(f"{table} doesn't have a foreign key!")
                else:
                    print(cfk)
            except Exception as error:
                print(f"\n{str(error)}")
        
        elif choice == "ha":
            table = input("table: ")
            ha = db.has_autoincrement(table)
            print(ha)

        elif choice == "dt":
            try:
                table = input("Table name: ")
                db.drop_table(table)
                print(f"{table} dropped!")
            except Exception as e:
                print(e)
                
        elif choice == "query":
            try:
                query = input("Query: ")
                rows = db.fetchall(query)
                for row in rows:
                    print(*row)
            except Exception as e:
                print(e)
