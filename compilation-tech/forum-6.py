import re



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
        lines.append(line.strip())

# Scanning
output = []

def output_line(line_number, column, token_class, token_value = None):
    return f'{line_number},{column},{token_class}' if token_value == None else f'{line_number},{column},{token_class},{token_value}'

for line_num in range(lines):
    line = lines[line_num]
    split_words = line.split()

    #starts from column 1 
    column = 1
    
    #to check if it is the name of the function or class
    is_class = False
    is_function = False
    is_echo = False
    # [class] [MyClass]

    for word in split_words: 
        # Check if it is a keyword
        if word == 'class':
            is_class = True
            output.append(output_line(line_num, column, 'class'))
            column = column + len(word)
            continue
        elif word == 'function':
            is_function = True
            output.append(output_line(line_num, column, 'function'))
            column = column + len(word)
            continue
        elif word == 'echo':
            is_echo = True
            output.append(output_line(line_num, column, 'print-out'))
            column = column + len(word)
            continue
        
        # Check if name of class or function
        if is_class or is_function:
            if is_function:
                # It is name of a function
                starts_with = re.match("^[a-zA-Z_]", word)  # starts with A-Z or _
                contains_only = re.findall('[\w_]+$', word) 
                contains_open_bracket = re.match ("^[(]", word)
                contains_closing_bracket = re.match("[)]", word)
                
                if starts_with and contains_only and contains_open_bracket:
                    # myFunction( or myFunction($parameter1
                    bracket_index = word.index('(')
                    cleaned_word = word[0:bracket_index] #fuction name without bracket, i.e. myFunction
                    output.append(output_line(line_num, column, 'type-identifier', cleaned_word))
                    column = column + len(cleaned_word)
                    output.append(output_line(line_num, column, token_dict['(']))
                    column = column + 1
                    is_function = False
                    # Check if there is parameter
                    if bracket_index != len(word)-1:
                        # myFunction($parameter1
                        param = word[bracket_index + 1] # Gets $parameter1 
                        there_is_dollar = param[0:1] == '$' #parameter has to start with $ sign

                        #starts with alphanumeric and underscores 
                        starts_with = re.match("^[a-zA-Z_]", param[1])
                        contains_only = re.findall('[\w_]+$', param[1])
                        if there_is_dollar and starts_with and contains_only:
                            # Gets the $ sign from $paramter1
                            output.append(output_line(line_num, column, token_dict['$']))
                            column = column + 1
                            # Gets parameter1 from $parameter1
                            output.append(output_line(line_num, column, 'type-identifier', param[1]))
                            column = column + len(param[1])
                        else:
                            # TODO: Error
                            pass
                        #
                elif starts_with and contains_only and contains_open_bracket and contains_closing_bracket:
                    # myFunction()
                    cleaned_word = word[0:-2]
                    output.append(output_line(line_num, column, 'type-identifier', cleaned_word))
                    column = column + len(cleaned_word)
                    output.append(output_line(line_num, column, token_dict['(']))
                    column = column + 1
                    output.append(output_line(line_num, column, token_dict[')']))
                    column = column + 1
                    is_function = False
                elif starts_with and contains_only:
                    # myFunction
                    output.append(output_line(line_num, column, 'type-identifier', word))
                    column = column + len(word)
                    is_function = False
                continue
            else:
                # It is name of a class
                # class [myClass] {
                starts_with = re.match("^[a-zA-Z_]", word)
                contains_only = re.findall('[\w_]+$', word)
                if starts_with and contains_only : 
                    output.append(output_line(line_num, column, 'type-identifier', word))
                else:
                    # TODO: Error
                    pass
                is_class = False
                continue
        column = column + 1




            

        


# Output