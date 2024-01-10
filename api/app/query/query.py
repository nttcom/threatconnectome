from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create the SQLAlchemy engine
engine = create_engine('your_database_connection_string')

# Create a session factory
Session = sessionmaker(bind=engine)

# Function to execute SQL queries
def execute_query(query):
    # Create a session
    session = Session()

    try:
        # Execute the query
        result = session.execute(query)
        # Commit the changes
        session.commit()
        # Return the result
        return result
    except Exception as e:
        # Rollback the changes in case of an error
        session.rollback()
        # Raise the exception
        raise e
    finally:
        # Close the session
        session.close()
