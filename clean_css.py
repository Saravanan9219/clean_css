#! /usr/bin/python

import StringIO
import sys
import os

html_handle = StringIO.StringIO()
css_file_handle = StringIO.StringIO()

try:
    file_name = os.path.split(sys.argv[1])[-1]
except IndexError:
    sys.stderr.write("No File Specified")
    sys.exit(-1)

with open(file_name, "rb") as file:
    html_handle.write(file.read())

html_handle.seek(0)

lines = html_handle.read().split(">")
styled_lines = [["style=" in line, line] for line in lines]

def extract_replace_style_gen():
    css_class = 0
    css_style = ''
    new_line = ''
    while True:
        line =  yield "class" + str(css_class), css_style, new_line
        css_class += 1
        style_pos = line.find("style=")
        if style_pos == -1:
            css_style = ""
            continue
        start_pos = style_pos + 6
        end_pos =  line.find('"', style_pos + 7)
        class_start_pos = line.find('class=')
        class_end_pos = line.find('"', class_start_pos + 7)

        inline_style = line[start_pos:end_pos].strip('"').rstrip('"')
        css_style = ';\n'.join(inline_style.split(';'))

        if class_start_pos > 0:
            if class_start_pos < style_pos:
                new_line = line[:class_end_pos] + " class" + str(css_class) +\
                    line[class_end_pos:style_pos] + line[end_pos + 1:]
                print new_line
            elif class_start_pos > style_pos:
                new_line = line[:style_pos] + line[end_pos + 1:class_end_pos -1] +\
                    "class" + str(css_class) + line[class_end_pos:]
                print new_line
        else:
            start_tag_pos = line.find("<")
            first_space_pos = line.find(" ", start_tag_pos + 1)
            new_line = line[:first_space_pos + 1] + "class=\"class" + str(css_class) +\
                "\" " + line[first_space_pos + 1:style_pos] + line[end_pos + 1:]
            print new_line

def process_styled_lines(lines):
    extract_replace_style = extract_replace_style_gen()
    extract_replace_style.send(None)
    for line_tuple in lines:
        flag = line_tuple[0]
        line = line_tuple[1]
        if flag:
            css_class, css_style, new_line = extract_replace_style.send(line)
            css_file_handle.write("." + str(css_class) + "{\n")
            css_file_handle.write(css_style + "\n")
            css_file_handle.write("}\n")
            line_tuple[1] = new_line
        
process_styled_lines(styled_lines)
css_file_handle.seek(0)
with open("new_files/" + file_name.split('.')[0] + "_styles.css", 'wb') as file:
    file.write(css_file_handle.read())

with open("new_files/" + file_name, 'wb') as file:
    file.write('>'.join([line for flag, line in styled_lines]))
css_file_handle.close()
html_handle.close()

