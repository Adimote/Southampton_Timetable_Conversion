University of Southampton Timetable converter
============================================

# This Project is no longer needed!

There is an ical feed available at:

https://timetable.soton.ac.uk/Feed/Get !

What follows below is here for posterity, as the ical feed should service all your needs.

(or if you want some code which generates a valid iCal file)

Regardless, this is now no longer supported because it is no longer needed.

## Description (for Posterity)

This is a python script that converts a University of Southampton new (as of 2015/16) calendar to an icalendar standard format (.ics)

this icalendar format can then be used to import into many calendars such as Google Calendar.

## Installation

1. [Download Python 2 or 3](https://www.python.org/downloads/) if you haven't already.

2. Create a virtual environment to install the dependencies with `pyvenv venv` or `virtualenv venv`. Activate with `source venv/bin/activate`. (Optional)

3. Install `python-lxml` or run `pip install -r requirements.txt`.

4. Run the script and follow the steps `python timetable_converter.py`.
