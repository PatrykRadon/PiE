import pandas as pd
import numpy as np


class Gradebook:
    def __init__(self, school_name, group_id, student_list=None):
        self.school_name = school_name
        self.group_id = group_id
        self.gradebook = pd.DataFrame(data=student_list,
                                          columns=pd.MultiIndex.from_tuples([('First Name', ''), ('Second Name', '')]))
        self.gradebook.index.rename('Album Index', inplace=True)
        self.gradebook.sort_values('Second Name', inplace=True)
        self.attendance = pd.DataFrame(data=student_list, columns=['First Name', 'Last Name'])

    def add_students(self, students):
        students = np.array(students).reshape(-1, 2)
        self.gradebook = self.gradebook.append(
            pd.DataFrame(students, columns=pd.MultiIndex.from_tuples([('First Name', ''), ('Second Name', '')])),
            ignore_index=True)
        self.gradebook.sort_values('Second Name', inplace=True)
        self.attendance = self.attendance.append(pd.DataFrame(students, columns=['First Name', 'Last Name']),
                                                 ignore_index=True)

    def add_grade_cat(self, grade_cat, class_name, grades=np.nan):
        self.gradebook[class_name, grade_cat] = grades

    def set_students_grade(self, students, grade_cat, class_name, grades):
        grades = np.array(grades).reshape(-1, 1)
        students = np.array(students).reshape(-1, 1)
        for student_id, grade in zip(students, grades):
            self.gradebook.loc[student_id, (class_name, grade_cat)] = grade

    def student_class_average(self, student_id, class_name):
        return self.gradebook.loc[student_id, class_name].mean()

    def student_average_overall(self, student_id):
        return self.gradebook.loc[student_id][2:].mean()

    def set_attendance(self, date, attendance_list):
        self.attendance[date] = attendance_list

    def student_attendance_overall(self, student_id):
        return self.attendance.loc[student_id][2:].sum()

if __name__ == "__main__":
    gb = Gradebook('best_school', '1a', [['jan','kowal'],['ban','bowal']])

    print(gb.gradebook)

    gb.add_students(['ban','bebok'])

    print(gb.gradebook)

    gb.add_grade_cat('kartkowka', class_name = 'maths')

    print(gb.gradebook)

    gb.set_students_grade(2, 'kartkowka', 'maths', 4.0)
    gb.set_students_grade([2, 1], 'sprawdzian', 'maths', [3.0, 2.0])

    print(gb.gradebook)


    print(gb.student_average_overall(2))
    print(gb.student_class_average(2,'maths'))

    gb.set_attendance('11-10-2010', [1,0,1])

    print(gb.attendance)

    print(gb.student_attendance_overall(2))
