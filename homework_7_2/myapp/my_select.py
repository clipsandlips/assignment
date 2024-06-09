from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from models import Student, Grade, Group, Subject #type: ignore

# Connect to the database
engine = create_engine("postgresql+psycopg2://marina_admin:mar123@localhost:5433/homework_7")
Session = sessionmaker(bind=engine)
session = Session()

# Define the queries
query1 = session.query(
    Group.group_name.label('group_name'),
    Student.name.label('student_name'),
    Subject.subject_name.label('subject_name'),
    Grade.grade
).join(Grade, Student.id == Grade.student_id) \
 .join(Subject, Grade.subject_id == Subject.id) \
 .join(Group, Student.group_id == Group.id) \
 .order_by(Group.group_name, Subject.subject_name, Student.name)

query2 = session.query(
    Student.name.label('student_name'),
    Group.group_name.label('group_name')
).join(Group, Student.group_id == Group.id) \
 .order_by(Group.group_name, Student.name)

# Execute the queries and print the results
print("Query 1 Results:")
for result in query1.all():
    print(result)

print("\nQuery 2 Results:")
for result in query2.all():
    print(result)

# Close the session
session.close()
