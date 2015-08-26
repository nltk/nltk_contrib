# Code for tagging temporal expressions in text and finding resultant time
# For details of the TIMEX format, see http://timex2.mitre.org/

import re
import string
import os
import sys

# Requires eGenix.com mx Base Distribution
# http://www.egenix.com/products/python/mxBase/
try:
    from mx.DateTime import *
except ImportError:
    print """
Requires eGenix.com mx Base Distribution
http://www.egenix.com/products/python/mxBase/"""

# Predefined strings.
numbers = "(^a(?=\s)|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand)"
time = "(morning|noon|evening|mid ?night|night|now)"
day = "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
week_day = "(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
month = "(january|february|march|april|may|june|july|august|september|october|november|december)"
dmy = "(year|day|week|month|minute|hour)"
rel_day = "(today|yesterday|tomorrow|tonight|tonite)"
exp1 = "(before|after|earlier|later|ago|from|at|for)"
exp2 = "(this|next|last)"
iso = "\d+[/-]\d+[/-]\d+ \d+:\d+:\d+\.\d+"
year = "((?<=\s)\d{4}|^\d{4})"
regxp1 = "((\d+|(" + numbers + "[-\s]?)+) " + dmy + "s? " + exp1 + "( (" + time + "|(\d+|(" + numbers + "[-\s]?)+)))?)"
regxp2 = "(" + exp2 + " (" + dmy + "|" + week_day + "|" + month + "))"

regxp6 = "(" + dmy + " " + exp1 + " " + rel_day +")"
regxp7 = "(" + exp1 + " (\d+\s?|(" + numbers + "[-\s]?)+)" + "(" + dmy + "(s?))?" + ")"
regxp8 = "(in (the )?" + time + ")"
regxp9 = "(" + exp1 + " (the )?" + exp2 + " (\d+ |(" + numbers + "[-\s]?)+)" + dmy + "s?)"

reg1 = re.compile(regxp1, re.IGNORECASE)
reg2 = re.compile(regxp2, re.IGNORECASE)
reg3 = re.compile(rel_day, re.IGNORECASE)
reg4 = re.compile(iso)
reg5 = re.compile(year)

reg6 = re.compile(regxp6, re.IGNORECASE)
reg7 = re.compile(regxp7, re.IGNORECASE)
reg8 = re.compile(regxp8, re.IGNORECASE)
reg9 = re.compile(regxp9, re.IGNORECASE)

def tag(text):

    # Initialization
    timex_found = []

    # re.findall() finds all the substring matches, keep only the full
    # matching string. Captures expressions such as 'number of days' ago, etc.
    found = reg1.findall(text)
    # print found
    found = [a[0] for a in found if len(a) > 1]
    for timex in found:
        timex_found.append(timex)

    # Variations of this thursday, next year, etc
    found = reg2.findall(text)
    found = [a[0] for a in found if len(a) > 1]
    for timex in found:
        timex_found.append(timex)

    # 'day after tomorrow' kind of expressions
    found = reg6.findall(text)
    # print found
    found = [a[0] for a in found if len(a) > 1]
    for timex in found:
        timex_found.append(timex)

    # 'at seven' kind of expressions
    found = reg7.findall(text)
    # print found
    found = [a[0] for a in found if len(a) > 1]
    for timex in found:
        timex_found.append(timex)

    # 'in (the) evening' kind of expressions
    found = reg8.findall(text)
    # print found
    found = [a[0] for a in found if len(a) > 1]
    for timex in found:
        timex_found.append(timex)

    # 'for (the) last two years' kind of expressions
    found = reg9.findall(text)
    # print found
    found = [a[0] for a in found if len(a) > 1]
    for timex in found:
        timex_found.append(timex)

    # today, tomorrow, etc
    found = reg3.findall(text)
    for timex in found:
        # print timex
        timex_found.append(timex)

    # ISO
    found = reg4.findall(text)
    for timex in found:
        timex_found.append(timex)

    # Year
    found = reg5.findall(text)
    for timex in found:
        timex_found.append(timex)

    # Tag only temporal expressions which haven't been tagged.
    for timex in timex_found:
        text = re.sub(timex + '(?!</TIMEX2>)', '<TIMEX2>' + timex + '</TIMEX2>', text)

    return text

# Hash function for week days to simplify the grounding task.
# [Mon..Sun] -> [0..6]
hashweekdays = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6}

# Hash function for months to simplify the grounding task.
# [Jan..Dec] -> [1..12]
hashmonths = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12}

# Hash number in words into the corresponding integer value
def hashnum(number):
    if re.match(r'one|^a\b', number, re.IGNORECASE):
        return 1
    if re.match(r'two', number, re.IGNORECASE):
        return 2
    if re.match(r'three', number, re.IGNORECASE):
        return 3
    if re.match(r'four', number, re.IGNORECASE):
        return 4
    if re.match(r'five', number, re.IGNORECASE):
        return 5
    if re.match(r'six', number, re.IGNORECASE):
        return 6
    if re.match(r'seven', number, re.IGNORECASE):
        return 7
    if re.match(r'eight', number, re.IGNORECASE):
        return 8
    if re.match(r'nine', number, re.IGNORECASE):
        return 9
    if re.match(r'ten', number, re.IGNORECASE):
        return 10
    if re.match(r'eleven', number, re.IGNORECASE):
        return 11
    if re.match(r'twelve', number, re.IGNORECASE):
        return 12
    if re.match(r'thirteen', number, re.IGNORECASE):
        return 13
    if re.match(r'fourteen', number, re.IGNORECASE):
        return 14
    if re.match(r'fifteen', number, re.IGNORECASE):
        return 15
    if re.match(r'sixteen', number, re.IGNORECASE):
        return 16
    if re.match(r'seventeen', number, re.IGNORECASE):
        return 17
    if re.match(r'eighteen', number, re.IGNORECASE):
        return 18
    if re.match(r'nineteen', number, re.IGNORECASE):
        return 19
    if re.match(r'twenty', number, re.IGNORECASE):
        return 20
    if re.match(r'thirty', number, re.IGNORECASE):
        return 30
    if re.match(r'forty', number, re.IGNORECASE):
        return 40
    if re.match(r'fifty', number, re.IGNORECASE):
        return 50
    if re.match(r'sixty', number, re.IGNORECASE):
        return 60
    if re.match(r'seventy', number, re.IGNORECASE):
        return 70
    if re.match(r'eighty', number, re.IGNORECASE):
        return 80
    if re.match(r'ninety', number, re.IGNORECASE):
        return 90
    if re.match(r'hundred', number, re.IGNORECASE):
        return 100
    if re.match(r'thousand', number, re.IGNORECASE):
      return 1000

# Given a timex_tagged_text and a Date object set to base_date,
# returns identified_time
def identify_time(tagged_text, base_date):

    # Find all identified timex and put them into a list
    timex_regex = re.compile(r'<TIMEX2>.*?</TIMEX2>', re.DOTALL)
    timex_found = timex_regex.findall(tagged_text)
    timex_found = map(lambda timex:re.sub(r'</?TIMEX2.*?>', '', timex), \
                timex_found)

    # Calculate the new date accordingly
    time_type = None
    time_data = None

    for timex in timex_found:
        timex_val = 'UNKNOWN' # Default value

        timex_ori = timex   # Backup original timex for later substitution

	'''	
	# If numbers are given in words, hash them into corresponding numbers.
        # eg. twenty five days ago --> 25 days ago
        if re.search(numbers, timex, re.IGNORECASE):
            split_timex = re.split(r'\s(?=days?|months?|years?|weeks?)', \
                                                              timex, re.IGNORECASE)
            value = split_timex[0]
            unit = split_timex[1]
            num_list = map(lambda s:hashnum(s),re.findall(numbers + '+', \
                                          value, re.IGNORECASE))
            timex = `sum(num_list)` + ' ' + unit

        # If timex matches ISO format, remove 'time' and reorder 'date'
        if re.match(r'\d+[/-]\d+[/-]\d+ \d+:\d+:\d+\.\d+', timex):
            dmy = re.split(r'\s', timex)[0]
            dmy = re.split(r'/|-', dmy)
            timex_val = str(dmy[2]) + '-' + str(dmy[1]) + '-' + str(dmy[0])
	'''

        # Converting numbers from words to digits
        # twenty four ---> 24
        # bug to be fixed for four teen, six teen, seven teen, eighteen, nineteen
        match = re.search(r'('+numbers+'[-\s]?)+', timex)
        if match:
            i = match.start()
            j = match.end()
            value = timex[i:j]
            value = value.strip()
            num_list = map(lambda s:hashnum(s),re.findall(numbers + '+', value))
            timex = timex[:i] + `sum(num_list)` + ' ' + timex[j:]

        print timex
        # Specific dates
        if re.match(r'\d{4}', timex):
            m = re.match(r'\d{4}', timex)
            y = int(m.group(0))

            time_type = 'period'
            td1 = DateTime(y, 01, 01, 00, 00)
            td2 = DateTime(y, 12, 31, 23, 59)
            time_data = td1, td2
            # timex_val = str(timex)

        # Relative dates
        elif re.match(r'tonight|tonite|today', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            m = re.match(r'tonight|tonite|today', timex)
            if 'tonight' in m.group(0) or 'tonite' in m.group(0):
                td1 = base_date + RelativeDateTime(hour=20, minute=00)
                td2 = base_date + RelativeDateTime(hour=23, minute=59)
            elif 'today' in m.group(0):
                td1 = base_date + RelativeDateTime(hour=00, minute=00)
                td2 = base_date + RelativeDateTime(hour=23, minute=59)
            time_data = td1, td2
            # timex_val = str(base_date)

        elif re.match(r'yesterday', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            td1 = base_date + RelativeDateTime(days=-1, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(days=-1, hour=23, minute=59)
            time_data = td1, td2
        elif re.match(r'tomorrow', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            td1 = base_date + RelativeDateTime(days=+1, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(days=+1, hour=23, minute=59)
            time_data = td1, td2
 
#            timex_val = str(base_date + RelativeDateTime(days=+1))

        # Weekday in the previous week.
        elif re.match(r'last ' + week_day, timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            day = Weekday[timex.split()[1].title()]
            time_type = 'period'
            td1 = base_date + RelativeDateTime(weeks=-1, weekday=(day, 0), hour=00, minute=00)
            td2 = base_date + RelativeDateTime(weeks=-1, weekday=(day, 0), hour=23, minute=59)
            time_data = td1, td2
#            timex_val = str(base_date + RelativeDateTime(weeks=-1, weekday=(day, 0)))
#            print timex_val

        # Weekday in the current week.
        elif re.match(r'this ' + week_day, timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            day = Weekday[timex.split()[1].title()]
            time_type = 'period'
            td1 = base_date + RelativeDateTime(weekday=(day, 0), hour=00, minute=00)
            td2 = base_date + RelativeDateTime(weekday=(day, 0), hour=23, minute=59)
            time_data = td1, td2
#            timex_val = str(base_date + RelativeDateTime(weeks=0, weekday=(day,0)))
#            print(timex_val)

        # Weekday in the following week.
        elif re.match(r'next ' + week_day, timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            day = Weekday[timex.split()[1].title()]
            time_type = 'period'
            td1 = base_date + RelativeDateTime(weeks=+1, weekday=(day, 0), hour=00, minute=00)
            td2 = base_date + RelativeDateTime(weeks=+1, weekday=(day, 0), hour=23, minute=59)
            time_data = td1, td2
#           timex_val = str(base_date + RelativeDateTime(weeks=+1, weekday=(day,0)))

        # Last, this, next week.
        elif re.match(r'last week', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            td1 = base_date + RelativeDateTime(weeks=-1)
            td2 = base_date
            time_data = td1, td2
#
            # year = (base_date + RelativeDateTime(weeks=-1)).year

            # iso_week returns a triple (year, week, day) hence, retrieve
            # only week value.
            # week = (base_date + RelativeDateTime(weeks=-1)).iso_week[1]
            # timex_val = str(year) + 'W' + str(week)
#            print(timex_val)
        elif re.match(r'this week', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            td1 = base_date
            td2 = base_date + RelativeDateTime(weeks=+1)
            time_data = td1, td2
#            year = (base_date + RelativeDateTime(weeks=0)).year
#            week = (base_date + RelativeDateTime(weeks=0)).iso_week[1]
#            timex_val = str(year) + 'W' + str(week)
        elif re.match(r'next week', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            td1 = base_date + RelativeDateTime(weeks=+1)
            td2 = td1+RelativeDateTime(weeks=+1)
            time_data = td1, td2
#           year = (base_date + RelativeDateTime(weeks=+1)).year
#           week = (base_date + RelativeDateTime(weeks=+1)).iso_week[1]
#           timex_val = str(year) + 'W' + str(week)


        # Month in the previous year.
        elif re.match(r'last ' + month, timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            mon = Month[timex.split()[1].title()]
            time_type = 'period'
            td1 = base_date + RelativeDateTime(years=-1, month=mon, day=1, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(years=-1, month=mon, day=-1, hour=23, minute=59)
            time_data = td1, td2

#            timex_val = str(base_date.year - 1) + '-' + str(mon)
#            print(timex_val)

        # Month in the current year.
        elif re.match(r'this ' + month, timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            mon = Month[timex.split()[1].title()]
            time_type = 'period'
            td1 = base_date + RelativeDateTime(month=mon, day=1, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(month=mon, day=-1, hour=23, minute=59)
            time_data = td1, td2

#            timex_val = str(base_date.year) + '-' + str(mon)
#            print(timex_val)

        # Month in the following year.
        elif re.match(r'next ' + month, timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            mon = Month[timex.split()[1].title()]
            time_type = 'period'
            td1 = base_date + RelativeDateTime(years=+1, month=mon, day=1, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(years=+1, month=mon, day=-1, hour=23, minute=59)
            time_data = td1, td2

#            timex_val = str(base_date.year + 1) + '-' + str(mon)
#            print(timex_val)

        elif re.match(r'last month', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            td1 = base_date + RelativeDateTime(months=-1, day=1, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(months=-1, day=-1, hour=23, minute=59)
            time_data = td1, td2


            # Handles the year boundary.
#            if base_date.month == 1:
#                timex_val = str(base_date.year - 1) + '-' + '12'
#            else:
#                timex_val = str(base_date.year) + '-' + str(base_date.month - 1)

        elif re.match(r'this month', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            td1 = base_date + RelativeDateTime(day=1, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(day=-1, hour=23, minute=59)
            time_data = td1, td2

#            timex_val = str(base_date.year) + '-' + str(base_date.month)
#            print(timex_val)

        elif re.match(r'next month', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            td1 = base_date + RelativeDateTime(months=+1, day=1, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(months=+1, day=-1, hour=23, minute=59)
            time_data = td1, td2


            # Handles the year boundary.
#            if base_date.month == 12:
#                timex_val = str(base_date.year + 1) + '-' + '1'
#            else:
#                timex_val = str(base_date.year) + '-' + str(base_date.month + 1)
#            print(timex_val)

        elif re.match(r'last year', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            td1 = base_date + RelativeDateTime(years=-1, month=1, day=1, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(years=-1, month=12, day=-1, hour=23, minute=59)
            time_data = td1, td2

#            timex_val = str(base_date.year - 1)
#            print(timex_val)

        elif re.match(r'this year', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            td1 = base_date + RelativeDateTime(month=1, day=1, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(month=12, day=-1, hour=23, minute=59)
            time_data = td1, td2

#            timex_val = str(base_date.year)
#            print(timex_val)

        elif re.match(r'next year', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            td1 = base_date + RelativeDateTime(years=+1, month=1, day=1, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(years=+1, month=12, day=-1, hour=23, minute=59)
            time_data = td1, td2
            
        # include cases for 'last|next minute|hour'

#            timex_val = str(base_date.year + 1)
#            print(timex_val)
        
        elif re.match(r'\d+ days? (ago|earlier|before)', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data


            # Calculate the offset by taking '\d+' part from the timex.
            offset = int(re.split(r'\s', timex)[0])
            time_type = 'period'
            td1 = base_date + RelativeDateTime(days=-offset, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(days=-offset, hour=23, minute=59)
            time_data = td1, td2


#            timex_val = str(base_date + RelativeDateTime(days=-offset))
#            print(timex_val)

        elif re.match(r'\d+ days? (later|after)', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            offset = int(re.split(r'\s', timex)[0])
            time_type = 'period'
            td1 = base_date + RelativeDateTime(days=+offset, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(days=+offset, hour=23, minute=59)
            time_data = td1, td2

#            timex_val = str(base_date + RelativeDateTime(days=+offset))
#            print(timex_val)

        elif re.match(r'\d+ weeks? (ago|earlier|before)', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            offset = int(re.split(r'\s', timex)[0])
            time_type = 'period'
            td1 = base_date + RelativeDateTime(weeks=-offset, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(weeks=-offset, hour=23, minute=59)
            time_data = td1, td2

#            year = (base_date + RelativeDateTime(weeks=-offset)).year
#            week = (base_date + RelativeDateTime(weeks=-offset)).iso_week[1]
#            timex_val = str(year) + 'W' + str(week)
#            print(timex_val)
        elif re.match(r'\d+ weeks? (later|after)', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            offset = int(re.split(r'\s', timex)[0])
            time_type = 'period'
            td1 = base_date + RelativeDateTime(weeks=+offset, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(weeks=+offset, hour=23, minute=59)
            time_data = td1, td2

#            year = (base_date + RelativeDateTime(weeks=+offset)).year
#            week = (base_date + RelativeDateTime(weeks=+offset)).iso_week[1]
#            timex_val = str(year) + 'W' + str(week)
        elif re.match(r'\d+ months? (ago|earlier|before)', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            offset = int(re.split(r'\s', timex)[0])
            time_type = 'period'
            td1 = base_date + RelativeDateTime(months=-offset, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(months=-offset, hour=23, minute=59)
            time_data = td1, td2


            # Checks if subtracting the remainder of (offset / 12) to the base month
            # crosses the year boundary.
#            if (base_date.month - offset % 12) < 1:
#                extra = 1

            # Calculate new values for the year and the month.
#            year = str(base_date.year - offset // 12 - extra)
#            month = str((base_date.month - offset % 12) % 12)

            # Fix for the special case.
#            if month == '0':
#                month = '12'
#            timex_val = year + '-' + month
#            print(timex_val)
        elif re.match(r'\d+ months? (later|after)', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

       # extra = 0
            offset = int(re.split(r'\s', timex)[0])
            time_type = 'period'
            td1 = base_date + RelativeDateTime(months=+offset, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(months=+offset, hour=23, minute=59)
            time_data = td1, td2

#            if (base_date.month + offset % 12) > 12:
#                extra = 1
#            year = str(base_date.year + offset // 12 + extra)
#            month = str((base_date.month + offset % 12) % 12)
#            if month == '0':
#                month = '12'
#            timex_val = year + '-' + month
#            print(timex_val)
        elif re.match(r'\d+ years? (ago|earlier|before)', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            offset = int(re.split(r'\s', timex)[0])
            time_type = 'period'
            td1 = base_date + RelativeDateTime(years=-offset, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(years=-offset, hour=23, minute=59)
            time_data = td1, td2

#            timex_val = str(base_date.year - offset)
#            print(timex_val)
        elif re.match(r'\d+ years? (later|after)', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            offset = int(re.split(r'\s', timex)[0])
            time_type = 'period'
            td1 = base_date + RelativeDateTime(years=+offset, hour=00, minute=00)
            td2 = base_date + RelativeDateTime(years=+offset, hour=23, minute=59)
            time_data = td1, td2

#            timex_val = str(base_date.year + offset)
#            print(timex_val)

        # 'for (the) last two years' kind of expressions
        elif re.match(r'for (the )?'+exp2+' (\d+ |(' + numbers + '[-\s]?)+)' + dmy + 's?', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            s = re.split(r'\s', timex) 
            if len(s) > 4:
                direction = s[2]
                offset = int(s[3])
                unit = s[4]
            else:
                direction = s[1]
                offset = int(s[2])
                unit = s[3]
            if 'last' in direction:
                if 'year' in unit:
                    td1 = base_date + RelativeDateTime(years=-offset, month=1, day=1, hour=00, minute=00)
                    td2 = base_date + RelativeDateTime(years=-1, month=12, day=31, hour=23, minute=59)
                if 'month' in unit:
                    td1 = base_date + RelativeDateTime(months=-offset, day=01, hour=00, minute=00)
                    td2 = base_date + RelativeDateTime(months=-1, day=-1, hour=23, minute=59)
            elif 'next' in direction:
                if 'year' in unit:
                    td1 = base_date + RelativeDateTime(years=+1, month=01, day=01, hour=00, minute=00)
                    td2 = base_date + RelativeDateTime(years=+offset, month=12, hour=23, minute=59)
                if 'month' in unit:
                    td1 = base_date + RelativeDateTime(months=+1, day=01, hour=00, minute=00)
                    td2 = base_date + RelativeDateTime(months=+offset, day=-1, hour=23, minute=59)
            time_data = td1, td2

       
        # 'day after tomorrow' kind of expressions
        elif re.match(r'day (after tomorrow|before yesterday)', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'period'
            direction = re.split(r'\s', timex)[1]
            if 'after' in direction:
                td1 = base_date + RelativeDateTime(days=+2, hour=00, minute=00)
                td2 = base_date + RelativeDateTime(days=+2, hour=23, minute=59)
            elif 'before' in direction:
                td1 = base_date + RelativeDateTime(days=-2, hour=00, minute=00)
                td2 = base_date + RelativeDateTime(days=-2, hour=23, minute=59)
            time_data = td1, td2
         
        # 'after 2 (day)s' kind of expressions
        # have to add cases for 'after|before number minute|day|week|month|year'
        elif re.match(r'(after|before) \d+( '+dmy+'s?)?', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            time_type = 'trigger'

            s = re.split(r'\s', timex)
            direction = s[0]
            origin = int(s[1])
            if len(s)>2:        # dmy exists
                unit = s[2]

            h = base_date.hour
            if h < 12:
                if 'before' in direction:
                    td1 = base_date
                    if origin > h:
                        td2 = base_date + RelativeDateTime(hour=origin, minute=0)
                    else:
                        td2 = base_date + RelativeDateTime(hour=origin+12, minute=0)
                elif 'after' in direction:
                    if origin > h:
                        td1 = base_date + RelativeDateTime(hour=origin, minute=0)
                    else:
                        td1 = base_date + RelativeDateTime(hour=origin+12, minute=0)
                    td2 = None
            else:
                h -= 12
                if 'before' in direction:
                    td1 = base_date
                    if origin > h:
                        td2 = base_date + RelativeDateTime(hour=origin+12, minute=0)
                    else:
                        td2 = base_date + RelativeDateTime(days=+1, hour=origin, minute=0)
                elif 'after' in direction:
                    if origin > h:
                        td1 = base_date + RelativeDateTime(hour=origin+12, minute=0)
                    else:
                        td1 = base_date + RelativeDateTime(days=+1, hour=origin, minute=0)
                    td2 = None
            time_data = td1, td2

        # Remove 'time' from timex_val.
        # For example, If timex_val = 2000-02-20 12:23:34.45, then
        # timex_val = 2000-02-20
#        timex_val = re.sub(r'\s.*', '', timex_val)

        # Substitute tag+timex in the text with grounded tag+timex.
#        tagged_text = re.sub('<TIMEX2>' + timex_ori + '</TIMEX2>', '<TIMEX2 val=\"'+ timex_val + '\">' + timex_ori + '</TIMEX2>', tagged_text)

        # '25 minutes later' kind of expressions
        elif re.match(r'\d+ (minutes?|hours?) (later|ago)', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            s = re.split(r'\s', timex)
            offset = int(s[0])
            unit = s[1]
            direction = s[2]
            time_type = 'stamp'
            if 'minute' in unit:
                if 'later' in s[2]:
                    td = base_date + RelativeDateTime(minutes=+offset)
                elif 'ago' in s[2]:
                    td = base_date + RelativeDateTime(minutes=-offset)
            elif 'hour' in unit:
                if 'later' in s[2]:
                    td = base_date + RelativeDateTime(hours=+offset)
                elif 'ago' in s[2]:
                    td = base_date + RelativeDateTime(hours=-offset)
            time_data = td

        # '2 hours from now' kind of expressions
        elif re.match(r'\d+ (minutes?|hours?) from now', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            s = re.split(r'\s', timex)
            offset = int(s[0])
            unit = s[1]
            time_type = 'stamp'
            if 'minute' in unit:
                td = base_date + RelativeDateTime(minutes=+offset)
            elif 'hour' in unit:
                td = base_date + RelativeDateTime(hours=+offset)
            time_data = td

        # '20 minutes after 8' kind of expression
        elif re.match(r'\d+ (minutes?|hours?) (before|after) (\d+|now|noon|mid ?night)', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            s = re.split(r'\s', timex)
            offset = int(s[0])
            unit = s[1]
            direction = s[2]
            origin = s[3]

            if origin.isdigit():
                origin = int(origin)
            elif 'noon' in origin:
                origin = 12
            elif 'mid' in origin:
                origin = 0
            elif 'now' in origin:
                origin = base_date.hour

            td = base_date
            if not origin:      #if before/after midnight
                td = base_date + RelativeDateTime(days=+1)
            time_type = 'stamp'
            if 'before' in direction:
                if 'minute' in unit:
                    td = td + RelativeDateTime(hour=origin, minutes=-offset)
                elif 'hour' in unit:
                    td = td + RelativeDateTime(hour=origin, hours=-offset)
            elif 'after' in direction:
                if 'minute' in unit:
                    td = td + RelativeDateTime(hour=origin, minutes=+offset)
                elif 'hour' in unit:
                    td = td + RelativeDateTime(hour=origin, hours=+offset)
            time_data = td

        # 'at 5' kind of expression
        # have to add cases for 'at noon|mid ?night'
        elif re.match(r'at \d+', timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            offset = int(re.split(r'\s', timex)[1])
            time_type = 'stamp'
            time_data = base_date + RelativeDateTime(hour=offset)

        # 'in (the) evening' kind of expression
        elif re.match(r'in (the )?'+time, timex):
            if time_data:
                if type(time_data) is tuple:
                    base_date = time_data[0]
                else:
                    base_date = time_data

            t = re.split(r'\s', timex)[-1]
            if 'evening' in t or 'night' in t:
                offset = base_date.hour
                if offset < 12:
                    time_data = base_date + RelativeDateTime(hour=offset+12)


    if type(time_data) is tuple:        # period or trigger
        time_data = [str(td) for td in time_data]
    else:
        time_data = str(time_data)      # stamp

    identified_time = time_type, time_data
    return identified_time
    # return tagged_text

####




def demo():
    # sample inputs
    sample = ["So, when did you graduate?",
    "In 2015 only.",
    "You mean this year?",
    "Yup",
    "Cool, next year even I would graduate :)",
    "I see. What are your plans for today?",
    "Tonight, I'm gonna hold you tight!",
    "What??",
    "Ah, nothing. Are you free tonite?",
    "Nopes, perhaps tomorrow we can meet ;)",
    "Ok, btw I saw you yesterday at the library. You were looking good.",
    "I always look good.",
    "LOL! so what happened to you last Friday. You were quite upset?",
    "Forget that. I would be performing this friday anyway",
    "Cool, I would be doing the same next friday. :D",
    "Last week, I was quite free.",
    "Yeah, and this week you won't be :-/",
    "Neither next week. :P",
    "You know what, last year I topped the class",
    "Great!, This December I would climb Mt. Everest.",
    "What! Are you serious?",
    "Yeah, I tried last February too. But, I failed.",
    "Ohh, anyway next march is my parent's anniversary. You remember na?",
    "I thought it was last month?",
    "Nope, stupid. And next month my sister is getting engaged.",
    "Ohh, and this month I will meet Stephen Amell.",
    "You gotta be kidding me :D!",
    "No, I am not. Last year I liked his profile picture and he said we will meet. Its time now. :)",
    "Very funny. This year was quite fun. I met you -_-",
    "Next year would be even great, when we will be physically together finally :)",
    "3 days ago, I killed someone :-/",
    "What did you just say?",
    "I said, three days ago I killed someone.",
    "That I understood. Whom do you kill?",
    "I will tell you the complete story twenty four months later.",
    "Are you mad?",
    "Let's change the topic. Five weeks earlier I visited Romania.",
    "SOS! Can you meet me 20 minutes later?"
    ]
    '''
    text = 'I want to book a cab 20 minutes from now'
    text = 'Looking to a make reservation for two people day after tomorrow at seven in the evening'
    text = 'I was working in san francisco for last two years'
    text = 'Any timer after 2 is fine'
    text = 'Before 5 is good'
    text = 'yesterday at 5'
    text = 'day before yesterday'
    text = 'I want to book a cab 20 minutes after midnight'
    text = 'I want to book a cab five minutes from now'
    text = 'train leaves 20 minutes after 8'
    '''
    
    date = [int(d) for d in raw_input('Set Date<dd-mm-yyyy>: ').split('-')]
    time = raw_input('Set Time<hhmm>hrs: ')
    hh = int(time[:2])
    mm = int(time[2:])
    
    print("Hey, if you prefer sitting back and enjoying my performance just keep pressing Enter after each line.")
    print
    print("You can go manual any time, by typing 'try' and then pressing Enter.")
    print
    print("To exit, you have to type 'bye' and then press Enter")
    print
       
    for text in sample:
        print(text)
        text = text.lower()
        tagged_text = tag(text)
        s = re.search(r'(<TIMEX2>).*(</TIMEX2>)', tagged_text)
        if s:
            print(s.group(0))
        print identify_time(tagged_text, DateTime(date[2], date[1], date[0], hh, mm))
        inp = raw_input()
        if inp.lower() == 'try':
            break
        elif inp.lower() == 'bye':
            print('Sayonara!')
            exit()
    
    while True:
        text = raw_input('\nWhat can I do for you?\n')
        text = text.lower()
        if text == 'bye':
            print('Tata!')
            break
        tagged_text = tag(text)
        s = re.search(r'(<TIMEX2>).*(</TIMEX2>)', tagged_text)
        if s:
            print(s.group(0))
        print identify_time(tagged_text, DateTime(date[2], date[1], date[0], hh, mm))
        # print identify_time(tagged_text, DateTime(2015, 7, 20, 20, 00))
        # d2 = DateTimeFromAbsDateTime(d.absdate, d.abstime)
            

if __name__ == '__main__':
    demo()

