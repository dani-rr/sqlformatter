import pyautogui as pya
import pyperclip  # handy cross-platform clipboard text handler
import time
import re
tab = '    '
comma_tab = '   ,'


def copy_clipboard():
    time.sleep(3)
    pya.hotkey('ctrl', 'c')
    return pyperclip.paste()


def select_formatter(sql_str):
    if sql_str and sql_str[0].lower() == 'select':
        for line in range(0, len(sql_str)):
            core_string, comment, position = comment_splitter(sql_str[line])
            if line == 0:
                sql_str[line] = sql_str[line].upper()
            elif line == 1:
                if position == 'pre':
                    sql_str[line] = comment + tab + core_string
                elif position == 'post':
                    sql_str[line] = tab + core_string + ' ' + comment 
                else:
                    sql_str[line] = tab + core_string
            else:
                core_string = comma_formatter(core_string)
                if position == 'pre':
                    sql_str[line] = comment + comma_tab + core_string
                elif position == 'post':
                    sql_str[line] = comma_tab + core_string + ' ' + comment 
                else:
                    sql_str[line] = comma_tab + core_string
        sql_str = as_formatter(sql_str)
        return sql_str
    else:
        return None


def from_formatter(from_str):
    if from_str and from_str[0].lower() == 'from':
        for line in range(0, len(from_str)):
            core_string, comment, position = comment_splitter(from_str[line])
            if line == 0:
                from_str[line] = from_str[line].upper()
            elif line == 1:
                if position == 'pre':
                    from_str[line] = comment + tab + core_string
                elif position == 'post':
                    from_str[line] = tab + core_string + ' ' + comment 
                else:
                    from_str[line] = tab + core_string
            else:
                core_string = comma_formatter(core_string)
                if position == 'pre':
                    from_str[line] = comment + comma_tab + core_string
                elif position == 'post':
                    from_str[line] = comma_tab + core_string + ' ' + comment 
                else:
                    from_str[line] = comma_tab + core_string
        return from_str
    else:
        return from_str
     

def where_formatter(where_str):
    if where_str and where_str[0].lower() == 'where':
        for line in range(0, len(where_str)):
            core_string, comment, position = comment_splitter(where_str[line])
            if line == 0:
                where_str[line] = where_str[line].upper()
            elif line == 1:
                if position == 'pre':
                    where_str[line] = comment + tab + core_string
                elif position == 'post':
                    where_str[line] = tab + core_string + ' ' + comment 
                else:
                    where_str[line] = tab + core_string
            else:
                if position == 'pre':
                    where_str[line] = comment +  ' ' + core_string
                elif position == 'post':
                    where_str[line] = core_string + ' ' + comment 
                else:
                    where_str[line] = core_string
        where_str = sub_where_formatter(where_str)
        return where_str
    else:
        return where_str


def groupby_formatter(groupby_str):
    if groupby_str and groupby_str[0].lower() == 'group by':
        for line in range(0, len(groupby_str)):
            core_string, comment, position = comment_splitter(groupby_str[line])
            if line == 0:
                groupby_str[line] = groupby_str[line].upper()
            elif line == 1:
                if position == 'pre':
                    groupby_str[line] = comment + tab + core_string
                elif position == 'post':
                    groupby_str[line] = tab + core_string + ' ' + comment 
                else:
                    groupby_str[line] = tab + core_string
            else:
                core_string = comma_formatter(core_string)
                if position == 'pre':
                    groupby_str[line] = comment + comma_tab + core_string
                elif position == 'post':
                    groupby_str[line] = comma_tab + core_string + ' ' + comment 
                else:
                    groupby_str[line] = comma_tab + core_string
        return groupby_str
    else:
        return groupby_str
    

def as_formatter(asString):
    if any(' AS ' in string for string in asString):
        line_str = {}
        for i in range(1, len(asString)):
            line_str[i] = asString[i].find(' AS ')
        max_position = max(line_str.values())
        for i in range(1, len(asString)):
            if line_str[i] != -1:
                pre_asString = asString[i].split(' AS ', 1)[0]
                post_asString = asString[i].split(' AS ', 1)[1]
                asString[i] = pre_asString + " " * (max_position - len(pre_asString)) + ' AS ' + post_asString
        return asString
    else:
        return asString


def sub_where_formatter(subWhereString):
    operators = ['<=', '>=', '=', '>', '<', 'IS NOT', 'IS']
    line_str = {}
    for operator in operators:
        for i in range(1, len(subWhereString)):
            if operator in subWhereString[i]:
                if i not in line_str:
                    line_str[i] = (operator + ' ' + str(subWhereString[i].rfind(operator) + len(operator)) )
    max_position_dict = line_str.copy()
    for i in range(1, len(subWhereString)): 
        max_position_dict[i] = int(max_position_dict[i].rsplit(' ', 1)[1])
    max_position = max(max_position_dict.values())
    for i in range(1, len(subWhereString)):
        if line_str[i] != -1:
            operator = line_str[i].rsplit(' ', 1)[0]
            pre_subWhereString = subWhereString[i].split(operator, 1)[0]
            post_subWhereString = subWhereString[i].split(operator, 1)[1]
            subWhereString[i] = pre_subWhereString + " " * (max_position - len(pre_subWhereString) - len(operator)) + operator + post_subWhereString
    return subWhereString


def comment_splitter(comment_string): 
    if comment_string.lstrip()[-1] == '-':
        return comment_string, False, False
    if comment_string.lstrip()[0] == '/':
        comment_pattern = r'/\*.*?\*/\s*'
        pre_comment = re.search(comment_pattern, comment_string)
        remaining_string = comment_string[pre_comment.end():].strip()
        position = 'pre'
        return remaining_string, pre_comment.group(0), position
    elif comment_string.rstrip()[-1] == '/':
        comment_pattern = r'/\*.*?\*/\s*'
        post_comment = re.search(comment_pattern, comment_string)
        remaining_string = comment_string[:post_comment.start()].strip()
        position = 'post'
        return remaining_string, post_comment.group(0), position
    else:
        return comment_string.strip(), False, False
    

def comma_formatter(comma_string):
    if comma_string[0] == ',':
        comma_string = comma_string.replace(',', '').strip()
        return comma_string
    elif comma_string[-1] == ',':
        comma_string = rreplace(comma_string, ',', '', 1).strip()
        return comma_string

def rreplace(s, old, new, occurrence):
    line = s.rsplit(old, occurrence)
    return new.join(line)


def query_splitter(query):
    start_select_index = sql_str.index('SELECT')
    start_from_index = sql_str.index('FROM')
    start_where_index = sql_str.index('WHERE')
    start_groupby_index = sql_str.index('GROUP BY')
    select_query = sql_str[start_select_index: start_from_index]
    from_query = sql_str[start_from_index: start_where_index]
    where_query = sql_str[start_where_index: start_groupby_index]
    groupby_query = sql_str[start_groupby_index: ]
    return select_query, from_query, where_query, groupby_query


def main(sql_str):
    select_query, from_query, where_query, groupby_query = query_splitter(sql_str)
    select_formatted = select_formatter(select_query)
    from_formatted = from_formatter(from_query)
    where_formatted = where_formatter(where_query)
    groupby_formatted = groupby_formatter(groupby_query)
    return select_formatted + from_formatted + where_formatted + groupby_formatted


sql_str = copy_clipboard().splitlines()
var = main(sql_str)

for i in var:
    print(i)

