# migrate -> models/tables/tablename.py

def model_file_migrate(textwrap, table, columns, models_tables):

    class_name = table.capitalize()
    model_file = f'{models_tables}/{table}.py'
    attributes = tuple(col['name'] for col in columns)
    init_args = ', '.join([f"{arg}=None" for arg in attributes])
    init_body = '\n                    '.join(f"self.{arg} = {arg}" for arg in attributes)
    attrs = ", ".join([f"{attr}={{self.{attr}!r}}" for attr in attributes])

    with open(model_file, 'w') as f:
        content = textwrap.dedent(f'''\
            #{model_file}
            from models.tables.table import Table
            
            class {class_name}(Table):
                def __init__(self, {init_args}, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.table = "{table}"
                    {init_body}
                    
                def __repr__(self):
                    return f"< {class_name}: ({attrs}) >"

        ''')
        f.write(content)
