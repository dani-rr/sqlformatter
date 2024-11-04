import pyautogui as pya
import pyperclip
import time
import re

class SQLFormatter:
    def __init__(self):
        self.tab = '    '
        self.comma_tab = '   ,'
        self.and_tab = 'AND '
        self.reserved_words = ['SELECT', 'FROM', 'WHERE', 'GROUP BY']
        self.level = 0
        
    def copy_clipboard(self):
        time.sleep(3)
        pya.hotkey('ctrl', 'c')
        return pyperclip.paste()

    def block_formatter(self, sql_str, reserved_word, sp_tab):
        """
        Applies formatting to splitted statements depending on the SELECT, FROM, WHERE, etc. part
        of the statement.
        """
        if sql_str and sql_str[0] == reserved_word:
            for line in range(0, len(sql_str)):
                core_string, comment, position = self.comment_splitter(sql_str[line])
                if line == 0:
                    continue
                elif line == 1:
                    sql_str[line] = self.format_line_with_comment(core_string, comment, position, self.tab)
                else:
                    sql_str[line] = self.format_line_with_comment(core_string, comment, position, sp_tab)
            match reserved_word:
                case 'SELECT':
                    sql_str = self.as_formatter(sql_str)
                case 'WHERE':
                    sql_str = self.where_formatter(sql_str)
            return sql_str
        else:
            return None

    def format_line_with_comment(self, core_string, comment, position, sp_tab):
        """
        Orders line with comments based on its position
        """
        if position == 'pre':
            return comment + sp_tab + core_string
        elif position == 'post':
            return sp_tab + core_string + ' ' + comment 
        else:
            return sp_tab + core_string

    def as_formatter(self, asString):
        """
        Aligns AS aliases on the same column level of SELECT statements
        """
        if any(' AS ' in string for string in asString):
            line_str = {}
            for i in range(1, len(asString)):
                paren_count = 0
                found_as_outside = -1
                j = 0
                while j < len(asString[i]):
                    char = asString[i][j]
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                    if paren_count == 0 and asString[i][j:j+4] == ' AS ':
                        found_as_outside = j
                        break
                    j += 1
                line_str[i] = found_as_outside
            max_position = max(pos for pos in line_str.values() if pos != -1)
            for i in range(1, len(asString)):
                if line_str[i] != -1:
                    pre_as, post_as = asString[i].rsplit(' AS ', 1)
                    asString[i] = pre_as + " " * (max_position - len(pre_as)) + ' AS ' + post_as
        return asString


    def where_formatter(self, subWhereString):
        """
        Aligns operators in the WHERE statements
        """
        operators = ['<=', '>=', '=', '>', '<', 'IS NOT', 'IS']
        line_str = {}
        for operator in operators:
            for i in range(1, len(subWhereString)):
                if operator in subWhereString[i]:
                    line_str[i] = operator + ' ' + str(subWhereString[i].rfind(operator) + len(operator))
        max_position = max(int(value.split()[1]) for value in line_str.values())
        for i in range(1, len(subWhereString)):
            if line_str[i] != -1:
                operator, position = line_str[i].split(' ')
                pre_sub, post_sub = subWhereString[i].split(operator, 1)
                subWhereString[i] = pre_sub + " " * (max_position - len(pre_sub) - len(operator)) + operator + post_sub
        return subWhereString

    def comment_splitter(self, comment_string):
        """ 
        Returns comment and its position in the statement
        """
        if comment_string.lstrip()[-1] == '-':
            return comment_string, False, False
        if comment_string.lstrip()[0] == '/':
            return self.extract_comment(comment_string, r'/\*.*?\*/\s*', 'pre')
        elif comment_string.rstrip()[-1] == '/':
            return self.extract_comment(comment_string, r'/\*.*?\*/\s*', 'post')
        else:
            return comment_string.strip(), False, False

    def extract_comment(self, comment_string, pattern, position):
        """
        Returns just the comment for a specific line
        """
        match = re.search(pattern, comment_string)
        if position == 'pre':
            return comment_string[match.end():].strip(), match.group(0), 'pre'
        else:
            return comment_string[:match.start()].strip(), match.group(0), 'post'

    def capitalize_reserved_words(self, sql_str):
        """
        Capitalizes any given reserved word in SQL
        """
        for word in self.reserved_words:
            pattern = re.compile(word, re.IGNORECASE)
            sql_str = pattern.sub(word, sql_str)
        return sql_str

    def query_splitter(self, select_query):
        """ Splits a SQL query into SELECT, FROM, WHERE, and GROUP BY sections """
        select_query_match = re.search(r'^SELECT.*(?=FROM )', select_query, re.IGNORECASE)
        from_query_match = re.search(r'FROM.*(?=WHERE )', select_query, re.IGNORECASE)
        where_query_match = re.search(r'WHERE.*(?=GROUP BY )', select_query, re.IGNORECASE)
        groupby_query_match = re.search(r'GROUP BY.*', select_query, re.IGNORECASE)

        select_query = select_query_match.group() if select_query_match else ""
        from_query = from_query_match.group() if from_query_match else ""
        where_query = where_query_match.group() if where_query_match else ""
        groupby_query = groupby_query_match.group() if groupby_query_match else ""
        
        return select_query, from_query, where_query, groupby_query

    def block_splitter(self, sql_str, reserved_word):
        """
        Splits a SELECT, WHERE, FROM, etc. block into lines using ',' or 'AND'
        depending on the part of the statement
        """
        result = []
        parentheses = 0
        current = ''
        pattern = rf'^({reserved_word})\s+(.*)'
        for char in sql_str:
            if (char == ',' or current[-5:] == ' AND ') and parentheses == 0:
                if current[-5:] == ' AND ':
                    current = current[:-5]
                if current.strip().startswith(reserved_word + ' '):
                    match = re.match(pattern, current.strip(), re.IGNORECASE)
                    keyword = match.group(1)
                    rest_of_string = match.group(2).strip()
                    result.append(keyword)
                    result.append(rest_of_string)
                else:
                    result.append(current.strip())
                current = ''
            elif char == '(':
                parentheses += 1
                current += char
            elif char == ')':
                parentheses -= 1
                current += char
            else:
                current += char
        if current:
            if current.strip().upper().startswith(reserved_word + ' '):
                reserved, rest = current.strip().split(' ', 1)
                result.append(reserved)
                result.append(rest)
            else:
                result.append(current.strip())
        return result

    def main(self, sql_str):
        sql_str = re.sub("\r\n| +", " ", sql_str)
        sql_str = self.capitalize_reserved_words(sql_str)
        select_query, from_query, where_query, groupby_query = self.query_splitter(sql_str)
        select_formatted = self.block_formatter(self.block_splitter(select_query, 'SELECT'), 'SELECT', self.comma_tab)
        from_formatted = self.block_formatter(self.block_splitter(from_query, 'FROM'), 'FROM', self.comma_tab)
        where_formatted = self.block_formatter(self.block_splitter(where_query, 'WHERE'), 'WHERE', self.and_tab)
        groupby_formatted = self.block_formatter(self.block_splitter(groupby_query, 'GROUP BY'), 'GROUP BY', self.comma_tab)
        
        return select_formatted + from_formatted + where_formatted + groupby_formatted


sql_formatter = SQLFormatter()
sql_str = 'SELECT\r\n2   AS Laufnummer\r\n   ,LBE.ArtikelID\r\n   ,LBE.ProfitKstId\r\n   ,LBE.BelieferungDatumId AS EreignisDatum\r\n   ,LBE.JahrMonatId  AS EreignisJahrMonatId\r\n   ,IBS.AktivDatum\r\n   ,IBS.AktivJahrMonat\r\n   ,1 AS PartnerSichtCode\r\n   ,MIN(COALESCE(HEP2.Datum-1,CAST(\'3000-01-01\' AS DATE))) AS BisDatum\r\nFROM\r\n    {instancename}Work.{processcode}_101_Belieferung LBE\r\nWHERE\r\n    ART.SammelnrCode = 0\r\nAND ART.BestandCode  = 1\r\nAND FIL.ScanningSeit IS NOT NULL\r\nAND FIL.VertriebstypInternID/100 = 2\r\nGROUP BY\r\n    LBE.ArtikelID\r\n   ,LBE.ProfitKstId\r\n   ,LBE.BelieferungDatumId\r\n   ,LBE.JahrMonatId\r\n   ,IBS.AktivDatum\r\n   ,IBS.AktivJahrMonat\r\n'
formatted_sql = sql_formatter.main(sql_str)
# for i in formatted_sql:
#     print(i)


with open("copy.txt", "w") as file:
    for i in formatted_sql:
        file.write(i + "\n")