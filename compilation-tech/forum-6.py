import re
from tracemalloc import start
import string


# token class 
token_dict = {
    '+' : 'addition-sign',
    '-' : 'minus',
    '=' : 'assignment',
    '*' : 'multiply',
    '/' : 'divide',
    ';' : 'semi-colon',
    '(' : 'open-bracket',
    ')' : 'close-bracket',
    '{' : 'open-bracket-curl',
    '}' : 'close-bracket-curl',
    '=='   : 'equal',
    '==='  : 'identical',
    '.'    :'string-concat',
    '//'   :'single-line',
    '#' :'single-comment',
    '.' : 'concat',
    '/*':'multi-line-comment',
    '*/':'close-multi-comment',
    '$' : 'variable',
    ' ' :'space',
}

#keywords 
identifier_dict = {
    'echo' : 'print-output',
    'function' :'function',
    'class' : 'class',
    '<?php' : 'php-opening-tag',
    '?>' : 'php-closing-tag',
}

# Read file
lines = []
with open('source.php') as f:
    for line in f:
        lines.append(line)

# Scanning
output = []

def output_line(line_number, column, token_class, token_value = None):
    return f'{line_number+1},{column+1},{token_class}' if token_value == None else f'{line_number+1},{column},{token_class},{token_value}'

is_string = False

for line_num in range(len(lines)):
    line = lines[line_num]
    # Calculate amount of whitespace (tab)
    # Add it to the initial column number
    # Get the index of the first character that is not empty string or \t

    # Calculate whitespace column
    padding = len(line) - len(line.lstrip())
    # "   xyz" => padding = 3

    #starts from column 1 (plus any padding) 
    column = padding

    while column < len(line)-1: 
        print(line)
        # Check if contain opening and closing tag
        if line_num == 0: 
            if line[column : column + len('<?php')] == '<?php':
                output.append(output_line(line_num, column, identifier_dict['<?php']))
                column = column + len('<?php')
            
                
                continue
            else:
                # todo error: no opening tag
                pass
        elif line_num == len(lines)-1: 
            if line[column : column + len('?>')] == '?>':
                output.append(output_line(line_num, column, identifier_dict['?>']))
                column = column + len('?>')
                continue
            else:
                # todo error: no closing tag
                pass   

        elif line[column] == '\"':
            is_string = True
            temp_index = column
            while is_string:
                column += 1
                if line[column] == '\"':
                    is_string = False
            column += 1
            word_string = line[temp_index:column]
            output.append(output_line(line_num, column, 'string-literal', word_string.replace(" ", "&nbsp")))

        elif line[column:column+len('//')] == '//' or line[column:column+len('#')] == '#':
            column = len(line)

        # Check if it is a class
        elif line[column : column + len('class')] == 'class':
            output.append(output_line(line_num, column, identifier_dict['class']))
            column = column + len('class') + 1
            starts_with = re.match("^[a-zA-Z_]", line[column])
            length = 1
            if starts_with:
                contains_only = True
                while contains_only:
                    # benerin regex cari yg ga ad spasi
                    contains_only = re.match('^[A-Za-z]*$', line[column+length]) 
                    length += 1
            else:
                # error no numbers allowed
                pass
            output.append(output_line(line_num, column+1, 'type-identifier', line[column:column+length-1]))
            column += (length-1)

            
            
        elif line[column : column + len('function')] == 'function':
            output.append(output_line(line_num, column, identifier_dict['function']))
            column = column + len('function') + 1
            starts_with = re.match("^[a-zA-Z_]", line[column])
            length = 1
            if starts_with:
                contains_only = True
                while contains_only:
                    contains_only = re.match('[\w_]+$', line[column+length]) 
                    length += 1
            else:
                # error no numbers allowed
                pass
            output.append(output_line(line_num, column+1, 'type-identifier', line[column:column+length-1]))
            column += (length-1)

        elif line[column] =='$':
            starts_with = re.match("^[a-zA-Z_]", line[column+1])
            length = 1
            if starts_with:
                contains_only = True
                while contains_only:
                    contains_only = re.match('[\w_]+$', line[column+length]) 
                    length += 1
            else:
                # error no numbers allowed
                pass
            output.append(output_line(line_num, column, 'variable'))
            output.append(output_line(line_num, column+length-1, 'type-identifier', line[column+1:column+length-1]))
            column += (length-1)


        elif line[column] in "1234567890":
            length = 0
            while line[column + length] in "1234567890":
                length += 1
            output.append(output_line(line_num, column, 'number', int(line[column:column+length])))
            column += length 

        elif line[column : column + len('echo')] == 'echo':
            output.append(output_line(line_num, column, identifier_dict['echo']))
            column = column + len('echo')



        elif line[column] in "+-=*/;}().{":
            output.append(output_line(line_num, column, token_dict[line[column]]))
            column += 1
        
        elif line[column] == ' ':
            column += 1
        

for n in output:
    print(n)