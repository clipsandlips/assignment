from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker
from models import Base, Student, Grade, Group, Subject, Teacher
import random
from datetime import datetime

# Initialize the Faker generator
fake = Faker()

# Connect to the database
engine = create_engine("postgresql+psycopg2://marina_admin:mar123@localhost:5433/homework_7")
Session = sessionmaker(bind=engine)
session = Session()

# Create the tables in the database
Base.metadata.create_all(engine)

# Generate data
def create_groups(num_groups):
    groups = []
    for _ in range(num_groups):
        group = Group(group_name=fake.word())
        session.add(group)
        groups.append(group)
    session.commit()
    return groups

def create_teachers(num_teachers):
    teachers = []
    for _ in range(num_teachers):
        teacher = Teacher(teacher_name=fake.name())
        session.add(teacher)
        teachers.append(teacher)
    session.commit()
    return teachers

def create_subjects(num_subjects, teachers):
    subjects = []
    for _ in range(num_subjects):
        subject = Subject(subject_name=fake.word(), teacher_id=random.choice(teachers).id)
        session.add(subject)
        subjects.append(subject)
    session.commit()
    return subjects

def create_students(num_students, groups):
    students = []
    for _ in range(num_students):
        student = Student(name=fake.name(), group_id=random.choice(groups).id)
        session.add(student)
        students.append(student)
    session.commit()
    return students

def create_grades(num_grades, students, subjects):
    for _ in range(num_grades):
        grade = Grade(
            student_id=random.choice(students).id,
            grade=round(random.uniform(1, 10), 2),
            date=fake.date_time_this_year(),
            subject_id=random.choice(subjects).id
        )
        session.add(grade)
    session.commit()

# Create the entities
groups = create_groups(3)
teachers = create_teachers(5)
subjects = create_subjects(5, teachers)
students = create_students(random.randint(30, 50), groups)
create_grades(20, students, subjects)

print("Database seeded successfully!")

# Close the session
session.close()
