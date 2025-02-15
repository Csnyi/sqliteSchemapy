# migrate -> controllers/tables/tables_controller.py

def tables_controller_migrate(app_root_len, table_info, os, models_tables, tables_controller):
    path = models_tables.replace('/', '.')[app_root_len:]
    from_model = '\n'.join(f"from {path}.{table} import {table.capitalize()}" for table in table_info)

    temp_filename = tables_controller + ".tmp"
    
    with open(temp_filename, "w", encoding="utf-8") as new_file, open(tables_controller, "r", encoding="utf-8") as old_file:
        new_file.write(f"#{tables_controller}\n{from_model}\n")
        for line in old_file:
            new_file.write(line)
    
    os.replace(temp_filename, tables_controller)


