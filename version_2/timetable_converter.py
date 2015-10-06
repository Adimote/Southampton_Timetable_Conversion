#!/usr/bin/env python
from lxml import etree
import icalendar
import unicodedata
from datetime import datetime, timedelta

url = "https://timetable.soton.ac.uk/Home/Semester/"
print("Please input the following into your browser," +
      "then save te output to the same directory as this python script")
print(url)

MONDAY_OF_FIRST_WEEK = "2015/09/28"  # YYYY/MM/DD
# convert it to datetime
monday_of_first_week = datetime.strptime(MONDAY_OF_FIRST_WEEK, "%Y/%m/%d")
print monday_of_first_week


def get_weeks_from_string(week_string):

    weeks = []
    # Last column is the weeks they are on.
    # Example: "1-11, 15"
    week_specs = week_string.split(",")
    for week_spec in week_specs:
        # If it's a range of weeks
        if "-" in week_spec:
            # i.e. 1-10
            ind_weeks = week_spec.split("-")
            start_week_int = int(ind_weeks[0])
            end_week_int = int(ind_weeks[1])
            for i in range(start_week_int, end_week_int+1):
                weeks.append(i)
        else:
            try:
                individual_week = int(week_spec)
            except ValueError:
                raise Exception("Suspected Malformed timetable")
            weeks.append(individual_week)
    return weeks


def scrape_page(page_string):
    page = etree.HTML(page_string)
    table = page.xpath("//*[@id=\"calendarTable\"]/table/tbody")[0]
    lectures = []
    for row in table:
        lecture = {}
        lecture["code"] = row[0][0].text
        lecture["name"] = row[1].text
        lecture["type"] = unicodedata.normalize('NFKD', row[2].text).encode(
            'ascii',
            'ignore')
        lecture["day"] = row[3].text
        lecture["start_time"] = row[4].text
        lecture["end_time"] = row[5].text
        lecture["weeks"] = row[6].text
        lectures.append(lecture)
        print lecture["weeks"]
        print get_weeks_from_string(lecture["weeks"])
        print lecture
    # print (etree.tostring(table, pretty_print=True))


def get_date_from_day_and_week(string, weeks):
    global monday_of_first_week
    # Day -> Int Dictionary
    day_offsets = {
        "Mon": 0,
        "Tue": 1,
        "Wed": 2,
        "Thu": 3,
        "Fri": 4,
        "Sat": 5,
        "Sun": 6,
    }
    time_deltas = []
    for week in weeks:
        if week in day_offsets:
            day_offset = day_offsets[week]
        else:
            raise "Badly formatted weekday!"
        total_offset = week*7 + day_offset
        time_deltas.append(timedelta(days=total_offset))
    return [monday_of_first_week+delta for delta in time_deltas]
    # TODO: check the above works

    # TODO: implement get_date_from_day_and_week into the scrape_page script
    # TODO: maybe make monday_of_first_week non-global
    # TODO: implement the below with the icalendar module
def export_as_ical(lectures):
    pass

def main():
    with open("My Timetable.html") as f:
        scrape_page(f.read())


if __name__ == "__main__":
    main()