from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from typing import List

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email_id = Column(Integer, ForeignKey('emails.id'))
    email = relationship("Email", back_populates="users")
    depressive_disorder_answers = relationship("DepressiveDisorderAnswer", order_by="DepressiveDisorderAnswer.id", back_populates="user")
    bipolar_disorder_answers = relationship("BipolarDisorderAnswer", order_by="BipolarDisorderAnswer.id", back_populates="user")
    anxiety_disorder_answers = relationship("AnxietyDisorderAnswer", order_by="AnxietyDisorderAnswer.id", back_populates="user")

class DepressiveDisorderAnswer(Base):
    __tablename__ = 'depressive_disorder_answers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="depressive_disorder_answers")
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)

class BipolarDisorderAnswer(Base):
    __tablename__ = 'bipolar_disorder_answers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="bipolar_disorder_answers")
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)

class AnxietyDisorderAnswer(Base):
    __tablename__ = 'anxiety_disorder_answers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="anxiety_disorder_answers")
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)

Email.users = relationship("User", order_by=User.id, back_populates="email")
User.depressive_disorder_answers = relationship("DepressiveDisorderAnswer", order_by=DepressiveDisorderAnswer.id, back_populates="user")
User.bipolar_disorder_answers = relationship("BipolarDisorderAnswer", order_by=BipolarDisorderAnswer.id, back_populates="user")
User.anxiety_disorder_answers = relationship("AnxietyDisorderAnswer", order_by=AnxietyDisorderAnswer.id, back_populates="user")

engine = create_engine('sqlite:///quiz.db', echo=False)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

def calculate_quiz_score(answers: List[str], target_answer: str) -> int:
    # A basic scoring system: +1 for each target answer
    return sum(answer.lower() == target_answer for answer in answers)

def register_user():
    while True:
        email = input("Enter your email: ")
        existing_email = session.query(Email).filter_by(email=email).first()

        if existing_email:
            print("Email already registered. Please enter a different email.")
        else:
            user_name = input("Enter your name: ")
            new_email = Email(email=email)
            user = User(name=user_name, email=new_email)
            session.add(new_email)
            session.add(user)
            session.commit()
            print("User registered successfully!")
            return user

def take_quiz(user):
    if user:
        depressive_disorder_answers = []
        bipolar_disorder_answers = []
        anxiety_disorder_answers = []

        depressive_disorder_questions = [
            "Have you experienced a persistent feeling of sadness or emptiness for most of the day, nearly every day?",
            "Have you lost interest or pleasure in activities that you once enjoyed?",
            "Do you have significant changes in appetite or weight (significant weight loss or gain)?",
            "Have you noticed changes in your sleep patterns, such as difficulty falling asleep, staying asleep, or sleeping too much?",
            "Do you feel fatigued or have a lack of energy, even after getting enough rest"
        ]

        bipolar_disorder_questions = [
            "Have you experienced periods where your mood was extremely elevated, characterized by heightened energy levels, increased self-esteem, and a decreased need for sleep?",
            "Have you gone through extended periods of deep sadness or hopelessness, where even routine tasks feel overwhelming?",
            "Have you noticed sudden and unexplained shifts in your mood from extreme highs to extreme lows?",
            "Do you often find yourself with a surplus of energy and an increased drive to accomplish goals during certain periods?",
            "Have you noticed changes in your sleep patterns, such as a decreased need for sleep during manic episodes or difficulty sleeping during depressive episodes?"
        ]

        anxiety_disorder_questions = [
            "Do you frequently experience excessive worry or fear about various aspects of your life, such as work, relationships, or health?",
            "Do you often experience physical symptoms of anxiety, such as muscle tension, trembling, sweating, or a racing heart?",
            "Do you find it challenging to engage in social situations due to fear of judgment, embarrassment, or criticism?",
            "Have you ever experienced sudden and intense episodes of fear or discomfort, accompanied by physical symptoms like chest pain, dizziness, or a sense of impending doom?",
            "Has anxiety significantly interfered with your ability to perform everyday tasks, meet responsibilities, or maintain relationships?"
        ]

        # Depressive Disorder Questions
        for question in depressive_disorder_questions:
            answer = input(f"{question} (yes/no): ").lower()
            depressive_disorder_answers.append(answer)
            quiz_answer = DepressiveDisorderAnswer(user=user, question=question, answer=answer)
            session.add(quiz_answer)

        # Check if the user should be prompted with additional questions for Bipolar Disorder
        if calculate_quiz_score(depressive_disorder_answers, 'no') < 3:
            print("\nThank you for completing our mental health quiz.\nBased on your answers, it's recommended to seek help for Depressive Disorder symptoms.\nConsider reaching out to a mental health expert near you.\nIn Kenya, the Mental Health Hotline is available at [+254 739 935 333 or +254 756 454 585].\nRemember, seeking help is a sign of strength.\nTake care.")
        else:
            # Additional questions for Bipolar Disorder
            print("\nYou answered more than 3 depressive disorder questions with 'no'. \nPlease answer the next set of questions.")
            for question in bipolar_disorder_questions:
                answer = input(f"{question} (yes/no): ").lower()
                bipolar_disorder_answers.append(answer)
                additional_quiz_answer = BipolarDisorderAnswer(user=user, question=question, answer=answer)
                session.add(additional_quiz_answer)

            session.commit()

            # Check if the user should be prompted with additional questions for Anxiety Disorder
            if calculate_quiz_score(bipolar_disorder_answers, 'no') < 3:
                print("\nThank you for completing our mental health quiz.\nBased on your answers, it's recommended to seek help for Bipolar disorder symptoms.\nConsider reaching out to a mental health expert near you.\nIn Kenya, the Mental Health Hotline is available at [+254 739 935 333 or +254 756 454 585].\nRemember, seeking help is a sign of strength.\nTake care.")
            else:
                # Additional questions for Anxiety Disorder
                print("\nYou answered more than 3 bipolar disorder questions with 'no'. \nPlease answer the next set of questions.")
                for question in anxiety_disorder_questions:
                    answer = input(f"{question} (yes/no): ").lower()
                    anxiety_disorder_answers.append(answer)
                    additional_quiz_answer = AnxietyDisorderAnswer(user=user, question=question, answer=answer)
                    session.add(additional_quiz_answer)

                session.commit()

                if calculate_quiz_score(anxiety_disorder_answers, 'no') < 3:
                    print("\nThank you for completing our mental health quiz.\nBased on your answers, it's recommended to seek help for Anxiety disorder symptoms.\nConsider reaching out to a mental health expert near you.\nIn Kenya, the Mental Health Hotline is available at [+254 739 935 333 or +254 756 454 585].\nRemember, seeking help is a sign of strength.\nTake care.")

                # Check if all three sets of questions have more than 3 'no' responses
                if (calculate_quiz_score(depressive_disorder_answers, 'no') > 3
                        and calculate_quiz_score(bipolar_disorder_answers, 'no') > 3
                        and calculate_quiz_score(anxiety_disorder_answers, 'no') > 3):
                    print("\nThank you for completing our mental health quiz."
                          "\nEven if the questions you answered don't indicate signs of depression, anxiety, or bipolar disorder,\nit's essential to prioritize your mental health."
                          "\nIf you ever feel the need to talk to a professional, consider reaching out to a mental health expert near you."
                          "\nIn Kenya, the Mental Health Hotline is available at [+254 739 935 333 or +254 756 454 585]."
                          "\nRemember, seeking help is a sign of strength.\nTake care.")
                else:
                    print("Quiz completed successfully!")

    else:
        print("User not found. Please register before taking the quiz.")

if __name__ == "__main__":
    while True:
        print("\n1. Register\n2. Take Quiz\n3. Exit")
        choice = input("Choose an option (1/2/3): ")

        if choice == '1':
            user = register_user()
        elif choice == '2':
            take_quiz(user)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")
