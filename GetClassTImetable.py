import json
import requests
import re

from bs4 import BeautifulSoup

TEACHER_PAGE_LIST_URL = "http://apps.tcfsh.tc.edu.tw/webadmin/adm/t202/108first/INDEX_TEAC.HTM"
CLASS_PAGE_LIST_URL = "http://apps.tcfsh.tc.edu.tw/webadmin/adm/t202/108first/INDEX_CLASS.HTM"
ROOT_URL = "http://apps.tcfsh.tc.edu.tw/webadmin/adm/t202/108first/";

EDITION = "27"
TITLE = "108學年度第一學期課表"

TOTAL_GRADE_NUM = 3
TOTAL_CLASS_NUM = 25

CLASS_TEACHER_NAME_ROW_COORDINATE = 75.518;
CLASS_TEACHER_NAME_COLUMN_COORDINATE = 255.419;

DOUBLE_DIGITS_TRANSFORM = {
    "1": "１",
    "2": "２",
    "3": "３",
    "4": "４",
    "5": "５",
    "6": "６",
    "7": "７",
    "8": "８",
    "9": "９",
    "0": "０"
}

SINGLE_DIGITS_TRANSFORM = {
    "１": "1",
    "２": "2",
    "３": "3",
    "４": "4",
    "５": "5",
    "６": "6",
    "７": "7",
    "８": "8",
    "９": "9",
    "０": "0"
}

DAY_OF_WEEK_TRANSFORM = {
    "1": "mon",
    "2": "tue",
    "3": "wed",
    "4": "thr",
    "5": "fri"
}


DAY_NUM = 5
COURSE_NUM = 8

CLASS_TIMETABLE_DAY_COLUMN_COORDINATE = [
    222.191,
    319.861,
    421.558,
    524.262,
    623.946
]

CLASS_TIMETABLE_FIRST_ROW_COORDINATE = [
    213.464,
    271.865,
    330.265,
    388.666,
    487.343,
    545.743,
    604.144,
    662.544
]

CLASS_TIMETABLE_SECOND_ROW_COORDINATE = [
    231.588,
    289.989,
    348.390,
    406.790,
    505.467,
    563.867,
    622.268,
    680.669
]

CLASS_TIMETABLE_THIRD_ROW_COORDINATE = [
    249.713,
    308.113,
    366.514,
    424.914,
    523.591,
    581.992,
    640.392,
    698.8
]

TEACHER_TIMETABLE_DAY_COLUMN_COORDINATE = [
    240.315,
    333.957,
    429.613,
    524.262,
    618.912
]

TEACHER_TIMETABLE_FIRST_ROW_COORDINATE = [
    193.326,
    252.733,
    312.141,
    371.548,
    464.184,
    523.591,
    582.999,
    642.406
]

TEACHER_TIMETABLE_SECOND_ROW_COORDINATE = [
    211.450,
    270.858,
    330.265,
    389.673,
    482.308,
    541.715,
    601.123,
    660.530
]

TEACHER_TIMETABLE_THIRD_ROW_COORDINATE = [
    229.575,
    288.982,
    348.390,
    407.797,
    500.432,
    559.840,
    619.247,
    678
]


def parse_to_double_digits(digit_str):
    for key in DOUBLE_DIGITS_TRANSFORM:
        digit_str = digit_str.replace(key, DOUBLE_DIGITS_TRANSFORM[key])

    return digit_str


def parse_to_single_digits(digit_str):
    for key in SINGLE_DIGITS_TRANSFORM:
        digit_str = digit_str.replace(key, SINGLE_DIGITS_TRANSFORM[key])

    return digit_str


# 抓所有老師姓名及老師課表連結
print("抓所有老師姓名及老師課表連結")

res = requests.get(TEACHER_PAGE_LIST_URL)
res.encoding = 'big5'
soup = BeautifulSoup(res.text, "lxml")

teacher_page_link_list = {}

id_count = 1
for teacher_link in soup.select("p a"):
    teacher_name = teacher_link.get_text()
    teacher_timetable_link = teacher_link.attrs.get("href")

    teacher_page_link_list[teacher_name] = {
        "id": id_count,
        "link": teacher_timetable_link
    }
    id_count += 1


output_teacher_list = []

id_count = 1
for teacher_link in soup.select("p a"):
    teacher_name = teacher_link.get_text()
    teacher_timetable_link = teacher_link.attrs.get("href")

    output_teacher_list.append({
        "id": id_count,
        "type": 1,
        "teacherName": teacher_name
    })
    id_count += 1




# 抓網站上所有班級課表連結
print("抓網站上所有班級課表連結")

res = requests.get(CLASS_PAGE_LIST_URL)
res.encoding = 'big5'
soup = BeautifulSoup(res.text, "lxml")

class_page_link_list = {}

for grade_num in range(1, TOTAL_GRADE_NUM + 1):
    for class_num in range(1, TOTAL_CLASS_NUM + 1):
        grade_and_class_num = "{grade_num}{class_num:02d}".format(
            grade_num=grade_num,
            class_num=class_num)
        double_digit_grade_and_class_num = parse_to_double_digits(grade_and_class_num)
        class_page_link = soup.find("a", string=double_digit_grade_and_class_num).attrs.get("href")

        class_page_link_list[grade_and_class_num] = {"link": class_page_link}


# 抓網站上所有班級的課表
print("抓網站上所有班級的課表")

class_timetable_list = {}

for grade_num in range(1, TOTAL_GRADE_NUM + 1):
    for class_num in range(1, TOTAL_CLASS_NUM + 1):
        grade_and_class_num = "{grade_num}{class_num:02d}".format(
            grade_num=grade_num,
            class_num=class_num)
        class_timetable_list[grade_and_class_num] = {
            "mon": [],
            "tue": [],
            "wed": [],
            "thr": [],
            "fri": []
        }

        class_timetable_page_url = "{root_url}{class_page_link}".format(
            root_url=ROOT_URL,
            class_page_link=class_page_link_list[grade_and_class_num]["link"])
        res = requests.get(class_timetable_page_url)
        res.encoding = 'big5'

        soup = BeautifulSoup(res.text, "lxml")

        class_teacher_name = soup.select_one("p[style*='Top:{top}'][style*='Left:{left}']".format(
            top=CLASS_TEACHER_NAME_ROW_COORDINATE,
            left=CLASS_TEACHER_NAME_COLUMN_COORDINATE)).get_text()
        class_timetable_list[grade_and_class_num]["class_teacher"] = class_teacher_name


        for day_count in range(0, DAY_NUM):
            for course_count in range(0, COURSE_NUM):
                course_name = ""
                course_teacher_name = ""

                first_row_str_element = soup.select_one("p[style*='Top:{top}'][style*='Left:{left}']".format(
                    top=CLASS_TIMETABLE_FIRST_ROW_COORDINATE[course_count],
                    left=CLASS_TIMETABLE_DAY_COLUMN_COORDINATE[day_count]))
                first_row_str = first_row_str_element.get_text() if first_row_str_element else ""

                second_row_str_element = soup.select_one("p[style*='Top:{top}'][style*='Left:{left}']".format(
                    top=CLASS_TIMETABLE_SECOND_ROW_COORDINATE[course_count],
                    left=CLASS_TIMETABLE_DAY_COLUMN_COORDINATE[day_count]))
                second_row_str = second_row_str_element.get_text() if second_row_str_element else ""

                third_row_str_element = soup.select_one("p[style*='Top:{top}'][style*='Left:{left}']".format(
                    top=CLASS_TIMETABLE_THIRD_ROW_COORDINATE[course_count],
                    left=CLASS_TIMETABLE_DAY_COLUMN_COORDINATE[day_count]))
                third_row_str = third_row_str_element.get_text() if third_row_str_element else ""

                if first_row_str == "" and third_row_str == "":
                    course_name = second_row_str
                elif third_row_str == "":
                    course_name = first_row_str
                    course_teacher_name = second_row_str
                else:
                    course_name = first_row_str + second_row_str
                    course_teacher_name = third_row_str

                day_course_index = "{day}-{course}".format(day=day_count + 1, course=course_count + 1)
                class_timetable_list[grade_and_class_num][day_course_index] = {
                    "course_name": course_name,
                    "course_teacher_name": course_teacher_name
                }

                if course_name:
                    class_timetable_list[grade_and_class_num][DAY_OF_WEEK_TRANSFORM[str(day_count + 1)]].append({
                            "course": course_count + 1,
                            "teacherId": teacher_page_link_list[course_teacher_name]["id"] if course_teacher_name in teacher_page_link_list else 0,
                            "teacherName": course_teacher_name,
                            "courseName": course_name
                        })


output_class_teacher_list = []
output_class_timetable_list = []
for grade_num in range(1, TOTAL_GRADE_NUM + 1):
    for class_num in range(1, TOTAL_CLASS_NUM + 1):

        grade_and_class_num = "{grade_num}{class_num:02d}".format(
            grade_num=grade_num,
            class_num=class_num)

        output_class_timetable_list.append({
            "grade": grade_num,
            "classNum": class_num,
            "classTimetable": class_timetable_list[grade_and_class_num]
        })

        output_class_teacher_list.append({
            "grade": grade_num,
            "classNum": class_num,
            "teacherId": teacher_page_link_list[class_timetable_list[grade_and_class_num]["class_teacher"]]["id"],
            "teacherName": class_timetable_list[grade_and_class_num]["class_teacher"]
        })




# 抓網站上所有老師的課表
print("抓網站上所有老師的課表")

teacher_timetable_list = {}

for key in teacher_page_link_list:
    teacher_timetable_page_url = "{root_url}{teacher_page_link}".format(
        root_url=ROOT_URL,
        teacher_page_link=teacher_page_link_list[key]["link"])
    teacher_timetable_list[key] = {
            "mon": [],
            "tue": [],
            "wed": [],
            "thr": [],
            "fri": []
        }

    res = requests.get(teacher_timetable_page_url)
    res.encoding = 'big5'
    soup = BeautifulSoup(res.text, "lxml")

    for day_count in range(0, DAY_NUM):
        for course_count in range(0, COURSE_NUM):
            grade_and_class_str = ""
            course_name = ""

            first_row_str_element = soup.select_one("p[style*='Top:{top}'][style*='Left:{left}']".format(
                top=TEACHER_TIMETABLE_FIRST_ROW_COORDINATE[course_count],
                left=TEACHER_TIMETABLE_DAY_COLUMN_COORDINATE[day_count]))
            first_row_str = first_row_str_element.get_text() if first_row_str_element else ""

            second_row_str_element = soup.select_one("p[style*='Top:{top}'][style*='Left:{left}']".format(
                top=TEACHER_TIMETABLE_SECOND_ROW_COORDINATE[course_count],
                left=TEACHER_TIMETABLE_DAY_COLUMN_COORDINATE[day_count]))
            second_row_str = second_row_str_element.get_text() if second_row_str_element else ""

            third_row_str_element = soup.select_one("p[style*='Top:{top}'][style*='Left:{left}']".format(
                top=TEACHER_TIMETABLE_THIRD_ROW_COORDINATE[course_count],
                left=TEACHER_TIMETABLE_DAY_COLUMN_COORDINATE[day_count]))
            third_row_str = third_row_str_element.get_text() if third_row_str_element else ""

            if third_row_str != "":
                grade_and_class_str = parse_to_single_digits(third_row_str)
                course_name = first_row_str + second_row_str
            elif first_row_str != "":
                grade_and_class_str = parse_to_single_digits(second_row_str)
                course_name = first_row_str
            else:
                course_name = second_row_str

            pattern = re.compile("^\d{3}$")
            if pattern.match(grade_and_class_str):
                teacher_timetable_list[key][DAY_OF_WEEK_TRANSFORM[str(day_count + 1)]].append({
                        "course": course_count + 1,
                        "grade": int(grade_and_class_str) // 100,
                        "classNum": int(grade_and_class_str) % 100,
                        "courseName": course_name
                    })
            elif course_name:
                teacher_timetable_list[key][DAY_OF_WEEK_TRANSFORM[str(day_count + 1)]].append({
                        "course": course_count + 1,
                        "grade": 0,
                        "classNum": 0,
                        "courseName": course_name
                    })

output_teacher_timetable_list = {}
for teacher_item in output_teacher_list:
    teacher_id = teacher_item["id"]
    teacher_name = teacher_item["teacherName"]

    output_teacher_timetable_list[teacher_id] = {
        "teacherId": teacher_id,
        "teacherName": teacher_name,
        "teacherTimetable": teacher_timetable_list[teacher_name]
    }


output_data = {
    "status": "success",
    "data": {
        "classTimetableEdition": EDITION,
        "classTimetableTitle": TITLE,
        "teacherList": output_teacher_list,
        "teacherTimetable": output_teacher_timetable_list,
        "classTimetable": output_class_timetable_list,
        "classTeacher": output_class_teacher_list
    }
}

f = open("alldata.json", "w")
f.write(json.dumps(output_data))
f.close()

output_class_timetable_edition = {
    "status": "success",
    "data": {
        "classTimetableEdition": EDITION
    }
}

f = open("classTimetableEdition.json", "w")
f.write(json.dumps(output_class_timetable_edition))
f.close()
