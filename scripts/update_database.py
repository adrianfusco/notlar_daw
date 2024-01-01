from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from datetime import datetime
import sys


def create_session(database_url):
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()


def upgrade_table(database_url, table_name, column_name, column_type):
    try:
        session = create_session(database_url)

        # Check if the column exists in the table
        query_check = text(
            "SELECT * FROM information_schema.columns "
            "WHERE table_name = :table_name AND column_name = :column_name"
        )
        result = session.execute(query_check, {'table_name': table_name, 'column_name': column_name}).fetchone()

        if not result:
            # Add the new column to the table
            query_add_column = text(
                f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_type} NULL'
            )
            session.execute(query_add_column)

            # Update existing records
            query_update_records = text(
                f'UPDATE "{table_name}" SET "{column_name}" = :value'
            )
            records = session.execute(text(f'SELECT * FROM "{table_name}"')).fetchall()

            for record in records:
                value = record.get('created_at').date() if 'created_at' in record else datetime.now().date()
                session.execute(query_update_records, {
                    'table_name': table_name,
                    'column_name': column_name, 'value': value
                })

            session.commit()
            print(f"Upgrade successful for table '{table_name}' and column '{column_name}'.")

        else:
            print(f"Column '{column_name}' already exists in table '{table_name}'.")

    except OperationalError as e:
        print(f"Error: {e}")
    finally:
        session.close()


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python update_database.py <database_url> <table_name> <column_name> <column_type>")
    else:
        database_url = sys.argv[1]
        table_name = sys.argv[2]
        column_name = sys.argv[3]
        column_type = sys.argv[4]
        upgrade_table(database_url, table_name, column_name, column_type)
