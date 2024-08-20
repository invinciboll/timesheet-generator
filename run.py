from datetime import datetime
import os
import platform
import pdfkit
from PyPDF2 import PdfReader, PdfWriter

import locale


import tinydb

def generate_pdf(file_path, content:str):
    # Determine the platform and set the wkhtmltopdf path accordingly
    if platform.system() == 'Windows':
        wkhtmltopdf_path = os.path.join('tooling', 'wkhtmltopdf', 'bin', 'wkhtmltopdf.exe')
    else:  # Assuming Fedora or other Linux distributions
        wkhtmltopdf_path = '/usr/bin/wkhtmltopdf'  # Default installation path for Fedora

    options = {
        'page-size': 'A4',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
    }
    # Configure pdfkit with the correct path
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    # Generate the PDF
    return pdfkit.from_string(content, file_path, configuration=config, options=options)

def get_workdays(month, year):
    weekdays = []
    for i in range(1, 32):
        try:
            date = datetime(year, month, i)
            weekdays.append((date.strftime('%d.%m'), date.strftime('%A'), date.isocalendar()[1]))
        except ValueError:
            break

    # Filter out weekends
    workdays = [day for day in weekdays if day[1] not in ['Samstag', 'Sonntag']]

    # Group workdays by calendar weeks
    workdays_by_week = {}
    for day in workdays:
        week_number = day[2]
        if week_number not in workdays_by_week:
            workdays_by_week[week_number] = []
        workdays_by_week[week_number].append((day[0], day[1]))
    # If the week does not start with monday, add --- placeholders to the beginning so each week has 5 workdays
    for week in workdays_by_week:
        if workdays_by_week[week][0][1] != 'Montag':
            insert_days = 5 - len(workdays_by_week[week])
            workdays_by_week[week] = [('---', '---')]*insert_days + workdays_by_week[week]
        elif len(workdays_by_week[week]) < 5:
            insert_days = 5 - len(workdays_by_week[week])
            workdays_by_week[week] += [('---', '---')]*insert_days
    return workdays_by_week

def fill_table_rows_for_week(workdays):
    with open('table-row.html') as f:
        table_row = f.read()
    table_rows = ""
    for date, weekday in workdays:
        table_rows += table_row.replace('{date}', date).replace('{weekday}', weekday)
    return table_rows

def build_template_for_week(year, month_name, week, workdays, first_name, last_name, pers_nr):
    with open('table-body-start.html') as f:
        template_start = f.read()
    template_start = template_start.replace('{month}', month_name).replace('{year}', str(year)).replace('{week}', str(week)).replace('{firstName}', first_name).replace('{lastName}', last_name).replace('{persNr}', pers_nr)
    table_rows = fill_table_rows_for_week(workdays)
    with open('table-body-end.html') as f:
        template_end = f.read()
    return template_start + table_rows + template_end

def generate_file(month: int, year: int):
    locale.setlocale(locale.LC_TIME, 'de_DE')
    print(locale.getlocale(locale.LC_TIME))
    month_name = datetime.strptime(str(month), "%m").strftime("%B")
    print(month_name)
    dateinfo = get_workdays(month, year)

    db = tinydb.TinyDB('members.json')
    members = db.all()

    timesheets = []
    for week, workdays in dateinfo.items():
        for member in members:
            out = build_template_for_week(2024, month_name, week, workdays, member['firstname'], member['lastname'], member['persnr'])
            timesheets.append(out)

    if os.path.exists(f'generated_timesheets.pdf'):
        os.remove(f'generated_timesheets.pdf')

    with open("a4-wrapper.html") as f:
        a4_wrapper_original = f.read()
    filenames = []
    # iterate over two timesheets at a time
    for i in range(0, len(timesheets), 2):
        a4_wrapper = a4_wrapper_original
        a4_wrapper = a4_wrapper.replace('{content1}', timesheets[i])
        if i + 1 < len(timesheets):
            a4_wrapper = a4_wrapper.replace('{content2}', timesheets[i + 1])
        else:
            a4_wrapper = a4_wrapper.replace('{content2}', "")
        generate_pdf(f'output_{i}.pdf', a4_wrapper)
        filenames.append(f'output_{i}.pdf')

    pdf_writer = PdfWriter()
    for pdf_path in filenames:
        pdf_reader = PdfReader(pdf_path)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

    with open(f'generated_timesheets.pdf', 'wb') as output_pdf:
        pdf_writer.write(output_pdf)

    for pdf in filenames:
        os.remove(pdf)

    return f'generated_timesheets.pdf'
