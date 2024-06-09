from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Numeric, String, Integer, Text, ForeignKey, DateTime

Base = declarative_base()

class Student(Base):
    __tablename__= "students"
    id = Column(Integer(), primary_key=True)
    name = Column(String(20))
    group_id = Column(Integer(), ForeignKey('groups.id'))
    grades = relationship('Grade', back_populates='student')
    groups = relationship('Group', back_populates='students')


class Grade(Base):
    __tablename__ = 'grades'
    id = Column(Integer(), primary_key=True)
    student_id = Column(Integer(), ForeignKey('students.id'))
    grade = Column(Numeric())
    date = Column(DateTime())
    subject_id = Column(Integer(), ForeignKey('subjects.id'))
    
    students = relationship('Student', back_populates='grades')
    subjects = relationship('Subject', back_populates='grades')

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer(), primary_key=True)
    group_name = Column(String())
    students = relationship('Student', back_populates='group')


class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer(), primary_key=True)
    subject__name = Column(String())
    teacher_id = Column(Integer(), ForeignKey('teachers.id'))
    teachers = relationship('Teacher', back_populates='subject')
    grades = relationship('Grade', back_populates='subject')

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer(), primary_key=True)
    teacher__name = Column(String())
    subjects = relationship('Subject', back_populates='teacher')


#engine = create_engine("sqlite:///test.db")
engine = create_engine("postgresql+psycopg2://marina_admin:mar123@localhost:5433/homework_6")

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()


