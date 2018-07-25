sql_types = {'integer': sqlalchemy.types.INTEGER,
             'string': sqlalchemy.types.TEXT,
             'bool': sqlalchemy.types.BOOLEAN}

sql_column_types = {key: sql_types[value[1]] for key, value in json_data.items()}

# importing data
csv_to_postgresql('data/file.csv', 'data/census_column_dtypes.json', 'postgres', 'postgres', 'public', 'table', dbname='database')
