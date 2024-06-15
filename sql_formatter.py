import pyautogui as pya
import pyperclip  # handy cross-platform clipboard text handler
import time

def copy_clipboard():
    time.sleep(3)
    pya.hotkey('ctrl', 'c')
    return pyperclip.paste()


def select_formatter():
    sql_str = copy_clipboard().splitlines()
    if sql_str[0].lower() == 'select':
        for line in range(0, len(sql_str)):
            if line == 0:
                sql_str[line] = sql_str[line].upper()
            elif line == 1:
                sql_str[line] = '    ' + sql_str[line].strip()
            else:
                sql_str[line] = '   ,' + sql_str[line].replace(',', '', 1).strip()
        sql_str = as_formatter(sql_str)
    return sql_str


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

def from_formatter():
    sql_str = copy_clipboard().splitlines()
    if sql_str[0].lower() == 'from':
        for line in range(0, len(sql_str)):
            if line == 0:
                sql_str[line] = sql_str[line].upper()
            elif line == 1:
                sql_str[line] = '    ' + sql_str[line].strip()
            else:
                sql_str[line] = '   ,' + sql_str[line].replace(',', '', 1).strip()
    return sql_str

def where_formatter():
    sql_str = copy_clipboard().splitlines()
    if sql_str[0].lower() == 'where':
        for line in range(0, len(sql_str)):
            if line == 0:
                sql_str[line] = sql_str[line].upper()
            elif line == 1:
                sql_str[line] = '    ' + sql_str[line].strip()
            else:
                sql_str[line] = 'AND ' + sql_str[line].replace('AND ', '', 1).strip()
        sql_str = sub_where_formatter(sql_str)
    return sql_str

def sub_where_formatter(subWhereString):
    operators = ['<=', '>=', '=', '>', '<']
    line_str = {}
    for operator in operators:
        for i in range(1, len(subWhereString)):
            if operator in subWhereString[i]:
                if i not in line_str:
                    line_str[i] = (operator + ' ' + str(subWhereString[i].rfind(operator)))
    max_position_dict = line_str.copy()
    for i in range(1, len(subWhereString)): 
        max_position_dict[i] = int(max_position_dict[i].split(' ', 1)[1])

    max_position = max(max_position_dict.values())

    for i in range(1, len(subWhereString)):
        if line_str[i] != -1:
            operator = line_str[i].split(' ', 1)[0]
            operator_position = int(line_str[i].split(' ', 1)[1])
            pre_subWhereString = subWhereString[i].split(operator, 1)[0]
            post_subWhereString = subWhereString[i].split(operator, 1)[1]
            if len(operator) == 1:
                subWhereString[i] = pre_subWhereString + " " * (max_position - len(pre_subWhereString)) + operator + post_subWhereString
            else:
                subWhereString[i] = pre_subWhereString + " " * (max_position - len(pre_subWhereString) - 1) + operator + post_subWhereString
    return subWhereString
# lst = []
# var = copy_clipboard()
# lst.append(var) 
# print(lst)
var = where_formatter()
for i in var:
    print(i)


# SELECT
#   3 AS Laufnummer  /* Code: new events before date of stock event */
# , SSC.ArtikelID AS ArtikelID
# , SSC.FilialeID AS FilialeID
# , SSC.BestandesDatum AS BestandesDatum
# , SSC.Jahrmonat AS Jahrmonat
# , SSC.PartnerSichtCode AS PartnerSichtCode
# , - SUM(SEV.Menge) AS Menge  /* negative values */