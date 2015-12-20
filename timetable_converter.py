#!/usr/bin/env python3
from lxml import etree
import unicodedata
import uuid
import time
import os

from datetime import datetime, timedelta


try:
    input = raw_input  # for Python 2 compatibility
except NameError:
    pass


MONDAY_OF_FIRST_WEEK = "2015/09/28"  # YYYY/MM/DD


VERSION = 0.2

# convert it to datetime
MONDAY_OF_FIRST_WEEK_DATETIME = datetime.strptime(
        MONDAY_OF_FIRST_WEEK,
        "%Y/%m/%d"
    )

# Day -> Int Dictionary
DAY_OFFSETS = {
    "Mon": 0,
    "Tue": 1,
    "Wed": 2,
    "Thu": 3,
    "Fri": 4,
    "Sat": 5,
    "Sun": 6,
}

# Day -> ISO Dictionary
DAY_TO_ISO = {
    "Mon": "MO",
    "Tue": "TU",
    "Wed": "WE",
    "Thu": "TH",
    "Fri": "FR",
    "Sat": "SA",
    "Sun": "SU",
}

def get_term_weeks_from_string(week_string):
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
        lecture["code"] = row[0][0].text.strip()
        lecture["name"] = row[1].text.strip()
        # for some reason the lecture string has a unicode character on the end
        # We're clearing it here.
        lecture["type"] = unicodedata.normalize(
                'NFKD',
                row[2].text.strip()
            ).encode(
                'ascii',
                'ignore'
            ).decode('UTF-8')
        term_weeks = get_term_weeks_from_string(row[6].text.strip())

        # if there aren't any weeks, stop.
        if not term_weeks:
            raise Exception("Timetable entry has 0 valid weeks!")

        # get the weeks in ISO week form
        weeks = get_ISO_weeks(
                term_weeks,
                MONDAY_OF_FIRST_WEEK_DATETIME
            )


        # get the weekday name
        day_string = row[3].text.strip()
        # get the start and end times in HH:MM and convert them to datetime
        start_time_hhmm = row[4].text.strip()
        end_time_hhmm = row[5].text.strip()

        # Get a tuple of the start and end datetimes of the first lecture.
        start_and_end_datetime = get_datetime_of_lecture(
            start_time_hhmm,
            end_time_hhmm,
            day_string,
            term_weeks[0]
            )
        recursions = [start_and_end_datetime[0] + timedelta(weeks=week-term_weeks[0]) for week in term_weeks]
        lecture["day"] = day_string
        lecture["start_time"] = start_and_end_datetime[0]
        lecture["end_time"] = start_and_end_datetime[1]
        lecture["recursions"] = recursions
        lecture["weeks"] = weeks
        lecture["week_times"] = weeks
        lecture["location"] = row[7].text.strip()

        lectures.append(lecture)

    # print (etree.tostring(table, pretty_print=True))
    return lectures


def day_to_iso_day(day_string):
    return DAY_TO_ISO[day_string]


def get_ISO_weeks(term_weeks, first_day_of_term):
    week_offsets = [get_week_offset(x) for x in term_weeks]
    return [
        (first_day_of_term+x).isocalendar()[1]
        for x in week_offsets
    ]

def get_day_offset(day_string):
    if day_string in DAY_OFFSETS:
        day_offset = DAY_OFFSETS[day_string]
    else:
        raise Exception("Badly formatted weekday! {}".format(day_string))
    return timedelta(days=day_offset)


def get_week_offset(week_number):
    return timedelta(weeks=week_number-1)

def get_week_spans(weeks):
    spans = []
    minim = weeks[0]
    maxim = weeks[0]
    for w in weeks:
        if w == (maxim+1) or w == weeks[0]:
            maxim = w
        else:
            spans.append((minim, maxim))
            minim = w
            maxim = w
    spans.append((minim,maxim))
    return spans

def get_time_offset(time):
    t = datetime.strptime(time, "%H:%M")
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


def get_datetime_of_lecture(
    start_time_string,
    end_time_string,
    day_string,
    first_week_number
  ):
    """
    returns UTC datetime of the start and end times.
    """
    day_delta = get_day_offset(day_string)
    week_delta = get_week_offset(first_week_number)
    day_date = MONDAY_OF_FIRST_WEEK_DATETIME + week_delta + day_delta
    start_hour_delta = get_time_offset(start_time_string)
    end_hour_delta = get_time_offset(end_time_string)
    start_time = day_date+start_hour_delta
    end_time = day_date+end_hour_delta

    return (start_time, end_time)

# TODO: maybe make monday_of_first_week non-global
# TODO(Bonus) link rooms to opendata by adding \
#   ALTREF:http://data.southampton.ac.uk/room/<building-room>.html to the description


def export_as_ical(lectures):
    calendar_string = """BEGIN:VCALENDAR
PRODID:-//github.com.Adimote//Timetable Converter v{version}//EN
VERSION:2.0
CALSCALE:GREGORIAN
X-WR-CALNAME:timetable_University_of_Southampton
X-WR-TIMEZONE:Europe/London
BEGIN:VTIMEZONE
TZID:Europe/London
X-LIC-LOCATION:Europe/London
BEGIN:DAYLIGHT
TZOFFSETFROM:+0000
TZOFFSETTO:+0100
TZNAME:BST
DTSTART:19700329T010000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0100
TZOFFSETTO:+0000
TZNAME:GMT
DTSTART:19701025T020000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE""".format(version=VERSION)
    for lecture in lectures:
        calendar_string += """
BEGIN:VEVENT
DTSTART;TZID=Europe/London:{start_time}
DTEND;TZID=Europe/London:{end_time}{rdates}
UID:{uid}
DESCRIPTION:{name} ({type})
LOCATION: {location}
SUMMARY:{code}
TRANSP:OPAQUE
END:VEVENT
""".format(
        start_time=lecture["start_time"].strftime("%Y%m%dT%H%M%S"),
        end_time=lecture["end_time"].strftime("%Y%m%dT%H%M%S"),
        uid=uuid.uuid1(),
        name=lecture["name"],
        type=lecture["type"],
        rdates="".join(["\nRDATE:{}".format(recursion.strftime("%Y%m%dT%H%M%S"))
        for recursion in lecture["recursions"]
        ]),
        location=lecture["location"],
        code=lecture["code"],
        week_count=len(lecture["weeks"]),
        weeks=",".join([str(x) for x in lecture["weeks"]]),
        day_string=day_to_iso_day(lecture["day"])
    )
    calendar_string += """
END:VCALENDAR"""
    return calendar_string


def user_interface():

    url = "https://timetable.soton.ac.uk/Home/Semester/"
    print("This code is configured for the year starting: {}".format(MONDAY_OF_FIRST_WEEK))
    time.sleep(1)
    print("")
    a = input("...is it the right year? (yes/no) ")
    if a.strip().lower() != "yes":
        print("Go into the code and change the date to the FIRST monday of lectures!!")
        return input("(Press Enter to close)")
    print("")
    print("...good.")
    print("")
    time.sleep(0.2)
    print("Now then:")
    while True:
        print("")
        print("----")
        print("")
        print("Please load the following up in your web browser: (log in if needed)")
        print(url)
        input("(Press Enter/Return to continue)")
        print("")
        print("Press ctrl/command + S and save it as 'My Timetable.html' in the same directory as this python script")
        print("(Press Enter/Return when done)")
        input()
        if os.path.isfile("My Timetable.html"):
            break
        else:
            print("...")
            time.sleep(0.5)
            print("...I can't find the file!")
            print("")
            time.sleep(1)
            print("Lets try again")
            print("")
            time.sleep(0.5)
            print(
                "Remember to save it in the same " +
                "directory as this python script!"
                )
            time.sleep(0.5)

    with open("My Timetable.html") as f:
        lectures = scrape_page(f.read())
        with open("lecture_timetable.ics", "w") as cal_file:
            cal_file.write(export_as_ical(lectures).replace(r'\n', '\r\n'))
    print("...")
    print("")
    print("Done!")
    print("")
    print("The file 'lecture_timetable.ics' has now been created in the same directory.")
    print("To import this into google calendar you just select the file from the import option in the settings menu.")
    print("Good Luck!")
    input("(Press Enter to close)")


def test():
    with open("My Timetable.html") as f:
        lectures = scrape_page(f.read())
    print(export_as_ical(lectures))

def main():
    user_interface()

if __name__ == "__main__":
    main()
