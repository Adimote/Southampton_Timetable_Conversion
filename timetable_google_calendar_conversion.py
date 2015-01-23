import csv
import sys
from datetime import datetime, timedelta
"""
Gathers information from the 'Save to CSV' function of the southampton timetable 
managment and saves it as a new CSV file, which is compatiable with google calendar.

It's important to save the new timetable in a way that is easy to switch out, as the new calendar isn't saved as recurring lessons. So you'll need to swap 'em out.
"""
print("CSV Timetable to Google Calendar converter")
print("Version 2.15")
print("Author: Andrew Barrett-Sprot")
print("----------------------------")
print("How To Use:")
print("-----------")
print("1: Download the Timetable of your semester from")
print("https://www.adminservices.soton.ac.uk/adminweb/jsp/timetables/timetablesController.jsp")
print("and save the CSV in the same location as this python script")
print("2: Find the start date of your year (Not Semester!)")
print("3: Run this script and follow the instructions")
print("4: Choose the name of the output file")
print("5: Go to your google calendar and import the output file")
print("(Settings->Calendars->Import)")
print("...and you're done!")
print("")
print("------------")
print("")

# First Day of year, NEEDS TO BE A MONDAY
first_daystring_of_year = "2014/09/22"
print("Step 1:")
day = raw_input("Enter the first day of the year in the form YYYY/MM/DD (NEEDS TO BE A MONDAY) (default:"+first_daystring_of_year+")")
if day:
    first_daystring_of_year = day
try:
    first_day_of_year = datetime.strptime(first_daystring_of_year,"%Y/%m/%d")
except ValueError:
    sys.exit("Error: Invalid First Day of year")

# Input Filename
print("Step 2:")
filename = ""
if len(sys.argv) > 1:
    filename = sys.argv[1]
    print("Set input file to " + filename)
if not filename:
    # Ask for a filename
    filename = raw_input("Enter the name of the CSV file from Southampton: ")

# Output Filename
print("Step 3:")
output_filename = ""
if len(sys.argv) > 2:
    output_filename = sys.argv[2]
    print("Set output file to " + output_filename)
if not output_filename:
    # Ask for a output_filename
    default = "output.csv"
    output_filename = raw_input("Enter the name of Output file (default "+ default +"): ")
    if not output_filename:
        output_filename = default

# The conversion object, because I didn't want to split it into multiple files.
class Timetable_converter(object):

    # Day -> Int Dictionary
    day_offset = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }

    def __enter__(self):
        self.csv_file = open(self.file_name)
        # Open the write file as a new file
        self.out_file = open(self.out_file_name, 'w+')
        self.writer = csv.writer(self.out_file)
        self.reader = csv.reader(self.csv_file)
        return self

    def __exit__(self, type, value, traceback):
        self.csv_file.close()
        self.out_file.close()

    def read_file(self):
        for row in self.reader:
            if row:
                # Last column is the weeks they are on.
                # Example: "1-11, 15"
                weeks = row[-1].split(",")
                # Everything but the day and the weeks available
                for week_spec in weeks:
                    # If it's a range of weeks
                    if "-" in week_spec:
                        # i.e. 1-10
                        ind_weeks = week_spec.split("-")
                        start_week_int = int(ind_weeks[0])
                        end_week_int = int(ind_weeks[1])
                        for i in range(start_week_int, end_week_int+1):
                            self.add_lesson(row, i)
                    else:
                        try:
                            individual_week = int(week_spec)
                        except ValueError:
                            raise Exception("Suspected Malformed timetable")
                        self.add_lesson(row, individual_week)

    def __init__(self, file_name, out_file_name, first_day_of_term):
        self.csv_file = None
        self.out_file = None
        self.file_name = file_name
        self.out_file_name = out_file_name
        self.first_day_of_term = first_day_of_term

        self.written_yet = False

    def add_lesson(self, all_data, week_number):
        #"Thursday"
        day = all_data[0]
        #"12:00"
        start_time = all_data[1]
        #"14:00"
        end_time = all_data[2]
        #"COMP1202 Lab/01"
        subject = all_data[3]
        #"Millard D E Dr, Prince R F, Weal, M" + " Weeks: " + "1-11, 15"
        description = all_data[4] + " Weeks: " + all_data[6]
        #"44 / 1061"
        where = all_data[5]

        # Date of calendar entry
        start_date = self.first_day_of_term + timedelta(days=Timetable_converter.day_offset[day]) + timedelta(weeks=week_number-1)
        
        # Format the start date into Standard datetime
        start_date_str = start_date.strftime("%Y/%m/%d")

        # If it hasn't written anything yet, write the header to the file
        if not self.written_yet:
            self.written_yet = True
            self.writer.writerow([
                "Subject",
                "Start Date",
                "End Date",
                "Start Time",
                "End Time",
                "Description",
                "Location",
                "All Day Event"
            ])

        to_write = [subject,
                    start_date_str,
                    start_date_str,
                    start_time,
                    end_time,
                    description,
                    where,
                    "FALSE"]
        self.writer.writerow(to_write)

with Timetable_converter(filename, output_filename, first_day_of_year) as t:
    t.read_file()