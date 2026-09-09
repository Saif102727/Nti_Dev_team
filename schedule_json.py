import pandas as pd
import random

students_data = []

for i in range(1, 51):
    students_data.append({
        "Student_ID": i,
        "Study_Preference": "Flexible (Home/Uni)",
        "Target_Gaps": 2,
        "Lecture_Group": "A" if i <= 25 else "B" 
    })

for i in range(51, 76):
    students_data.append({
        "Student_ID": i,
        "Study_Preference": "Home",
        "Target_Gaps": random.choice([0, 0, 0, 1]), # الأولوية لـ 0
        "Lecture_Group": "A" 
    })

for i in range(76, 101):
    students_data.append({
        "Student_ID": i,
        "Study_Preference": "University",
        "Target_Gaps": 4,
        "Lecture_Group": "B"
    })

df_students = pd.DataFrame(students_data)

print("Lecture Group Distribution:")
print(df_students['Lecture_Group'].value_counts())

df_students.to_json("students_dummy_data.json", orient="records", indent=4)

print("\nSample Data Generated:")
print(df_students.head())
print(df_students.tail())