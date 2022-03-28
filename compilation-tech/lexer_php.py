import re
from tracemalloc import start



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
        lines.append(line)

# Scanning
output = []

def output_line(line_number, column, token_class, token_value = None):
    return f'{line_number+1},{column},{token_class}' if token_value == None else f'{line_number+1},{column},{token_class},{token_value}'

for line_num in range(len(lines)):
    line = lines[line_num]
    split_words = line.split()

    # Calculate amount of whitespace (tab)
    # Add it to the initial column number
    # Get the index of the first character that is not empty string or \t

    # Calculate whitespace column
    padding = len(line) - len(line.lstrip())
    # "   xyz" => padding = 3

    #starts from column 1 (plus any padding) 
    column = padding + 1
    
    #to check if it is the name of the function or class
    is_class = False
    is_function = False
    is_echo = False
    # [class] [MyClass]

    word_index = 0

    for word in split_words: 
        # Check if contain opening and closing tag
        if line_num == 0: 
            if word == '<?php':
                output.append(output_line(line_num, column, identifier_dict['<?php']))
                continue
            else:
                # todo error: no opening tag
                pass
        if line_num == len(lines)-1: 
            if word == '?>':
                output.append(output_line(line_num, column, identifier_dict['?>']))
                continue
            else:
                # todo error: no closing tag
                pass    

        # Check if it is a keyword
        if word == 'class':
            is_class = True
            output.append(output_line(line_num, column, 'class'))
            column = column + len(word) + 1
            continue
        elif word == 'function':
            is_function = True
            output.append(output_line(line_num, column, 'function'))
            column = column + len(word) + 1
            continue
        elif word == 'echo':
            is_echo = True
            quote_count = 0
            string_text = ""
            output.append(output_line(line_num, column, 'print-out'))
            column = column + len(word) + 1
            continue
        
        if word[:1] == '$':
            t_class = None
            for w in word:
                if w == '$':
                    t_class = 'type-identifier'
                    output.append(output_line(line_num, column, token_dict[w]))
                    column+=1
                    continue
                if t_class:
                    output.append(output_line(line_num, column, t_class, w))
                    column+=1
                    t_class = None
                    continue
                if re.match("^[0-9]+$", w):
                    output.append(output_line(line_num, column, "number", w))
                    column+=1
                    continue
                else:
                    output.append(output_line(line_num, column, token_dict[w]))
                    column+=1
                    continue

        # Check if name of class or function
        if is_class or is_function:
            if is_function:
                # It is name of a function
                starts_with = re.match("^[a-zA-Z_]", word)  # starts with A-Z or _
                contains_only = re.findall('[\w_]+$', word[:-3]) 
                contains_open_bracket = re.search ('\(', word)
                contains_closing_bracket = re.search("\)", word)
                contains_open_curly_bracket = re.search("\{", word)

                if starts_with and contains_only and contains_open_bracket and contains_closing_bracket and contains_closing_bracket:
                    # myFunction()
                    cleaned_word = word[0:-3]
                    output.append(output_line(line_num, column, 'type-identifier', cleaned_word))
                    column = column + len(cleaned_word) + 1
                    output.append(output_line(line_num, column, token_dict['(']))
                    column = column + 1
                    output.append(output_line(line_num, column, token_dict[')']))
                    column = column + 1
                    output.append(output_line(line_num, column, token_dict['{']))
                    column = column + 1
                    is_function = False

                elif starts_with and contains_only and contains_open_bracket:
                    # myFunction( or myFunction($parameter1
                    bracket_index = word.index('(')
                    cleaned_word = word[0:bracket_index] #fuction name without bracket, i.e. myFunction
                    output.append(output_line(line_num, column, 'type-identifier', cleaned_word))
                    column = column + len(cleaned_word) + 1
                    output.append(output_line(line_num, column, token_dict['(']))
                    column = column + 1
                    is_function = False
                    # check if there is parameter
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
                
                elif starts_with and contains_only:
                    # myFunction
                    output.append(output_line(line_num, column, 'type-identifier', word))
                    column = column + len(word) + 1
                    is_function = False
                continue
            else:
                # it is name of a class
                # class [myClass] {
                starts_with = re.match("^[a-zA-Z_]", word)
                contains_only = re.findall('[\w_]+$', word)
                if starts_with and contains_only : 
                    output.append(output_line(line_num, column, 'type-identifier', word))
                    column += len(word) + 1
                    continue
                if word == '{':
                    output.append(output_line(line_num, column, token_dict['{']))
                else:
                    # TODO: Error
                    pass
                is_class = False
                continue
            
        if is_echo:
            if quote_count % 2 == 1:
                string_text += '&nbsp'
            char_index = 0
            for w in word:
                if w == '\"':
                    quote_count += 1
                if quote_count % 2 == 1:
                    string_text += w
                    column += 1
                else:
                    string_text += w
                    column += 1
                    quote_count = 0

                    leftovers = word[char_index + 1:]
                    split_words.insert(word_index + 1, leftovers)

                    # [apple] [banana]
                    # ["apple"ab] [banana]
                    # ["apple"] [ab] [banana]

                    break
                char_index += 1
            if quote_count == 0:
                output.append(output_line(line_num, column, 'string-literal', string_text))
                is_echo = False

            # output.append(output_line(line_num, column, 'done'))    
        
        # TODO: Handles concat
        if word[:1] == '.':
            output.append(output_line(line_num, column, token_dict['.']))
            leftovers = word[1 : len(word)]
            split_words.insert(word_index + 1, leftovers)
                    

        column = column + 1
        word_index = word_index + 1




            

        


# Output
# print(output)
for n in output:
    print(n)