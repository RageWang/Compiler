"""
关键字：
    char double enum float int long short signed struct union unsigned void
    for do while continue break
    if else goto
    switch case default
    return
    auto extern register static
    const sizeof typdef volatile

标识符：
    由字母或下划线开头 后面有若干字母、数字或下划线组成

常数：
    整数
    实数
运算符：
    算数运算符：
        + - * / % = & | ! && || >> <<
        组合：
    关系运算符：
        > < == != >= <=

界符：
    { } 空格 （）[] , . : " ' // /* */
"""

from Definition import ComplierBase, Token, Error


class Lexer:

    def __init__(self, filename="", text=""):
        self.file_con = self.load_file(filename, text)

        self.recorder = ComplierBase()

        self.token = Token()
        self.error = Error()

        self.__current_line = 1
        self.__current_row = 0

    def load_file(self, filename="", text=""):
        print(filename, text)
        if filename != "":
            with open(filename, "r") as f:
                file_con = f.read()
                # print(file_con)
                return  file_con
        elif text != "":
            return text
        else:
            import sys
            sys.exit("无编译内容")

    def get_next_char(self):
        if (self.__current_row + 1) < len(self.file_con):
            self.__current_row += 1
            return self.file_con[self.__current_row]
        return None

    def judge_alpha(self):
        index = self.__current_row

        while self.__current_row < len(self.file_con):
            ch = self.file_con[self.__current_row]
            if not (ch.isalpha() or ch.isdigit() or ch == '_'):# 其他字符
                break
            self.__current_row += 1
        word = self.file_con[index: self.__current_row]
        try:
            t = self.recorder.code[word] # 关键字
        except KeyError:
            t = self.recorder.code['id']

        self.token.token_append((self.__current_line, word, t))

        self.__current_row -= 1

    def isnum(self, state):
        if state == 1:
            while state == 1:
                c = self.get_next_char()
                if c:
                    if c.isdigit():
                        pass
                    elif c == '.':
                        state = 2
                    elif c == 'e' or c == 'E':
                        state = 4
                    else:
                        state = 7
                else:
                    self.__current_row += 1
                    state = 7
        if state == 2:
            while state == 2:
                c = self.get_next_char()
                if c.isdigit():
                    state = 3
                else:
                    state = 11  # . 多余
        if state == 3:
            while state == 3:
                c = self.get_next_char()
                if c.isdigit():
                    pass
                elif (c == 'e') or (c == 'E'):
                    state = 4
                else:
                    state = 7
        if state == 4:
            while state == 4:
                c = self.get_next_char()
                if c.isdigit():
                    state = 6
                elif (c == '+') or (c == '-'):
                    state = 5
                else:
                    state = 12
        if state == 5:
            while state == 5:
                c = self.get_next_char()
                if c.isdigit():
                    state = 6
                else:
                    state = 13
        if state == 6:
            while state == 6:
                c = self.get_next_char()
                if not c.isdigit():
                    state = 7
        if state == 9:
            while state == 9:
                c = self.get_next_char()
                if c.isdigit() or ('A' <= c <= 'F') or ('a' <= c <= 'f'):
                    state = 10
                else:
                    state = 14
        if state == 10:
            while state == 10:
                c = self.get_next_char()
                if not (c.isdigit() or ('A' <= c <= 'F') or ('a' <= c <= 'f')):
                    state = 7
        # 错误判断
        if state == 7:
            return True  # 没有错误
        elif state == 11:  # TODO: error . 多余
            self.error.error_append((1, self.__current_line, '.'))
            self.__current_row -= 1
            pass
        elif state == 12:  # TODO: error E/e 多余
            self.error.error_append((1, self.__current_line, 'E/e'))
            self.__current_row -= 1
            pass
        elif state == 13:  # TODO: error +/- 多余
            self.error.error_append((1, self.__current_line, '+/-'))
            self.__current_row -= 1
            pass
        elif state == 14:  # TODO: error x/X 多余
            self.error.error_append((1, self.__current_line, 'x/X'))
            self.__current_row -= 1
        return False

    def judge_number(self):
        index = self.__current_row

        if self.file_con[self.__current_row] == '0':
            ch = self.get_next_char()
            if (ch == 'x') or (ch == 'X'):  # 0x 0X
                state = 9
            elif ch.isdigit():
                state = 1
            else:
                state = 7  # 结束
        else:
            state = 1
        self.isnum(state)
        word = self.file_con[index:self.__current_row]
        self.token.token_append((self.__current_line, word, self.recorder.code['constNum']))

        self.__current_row -= 1

    def judge_sign_multi(self):
        self.__current_row += 1
        ch = self.file_con[self.__current_row]
        if ch == '*':  # /*
            while self.__current_row < len(self.file_con) - 1:
                if self.file_con[self.__current_row] == '\n':
                    self.__current_line += 1
                # 超前检测
                if not (self.file_con[self.__current_row] == '*' and self.file_con[self.__current_row + 1] == '/'):
                    self.__current_row += 1
                else:
                    self.__current_row += 1
                    break
        elif ch == '/':  # //
            while self.__current_row < len(self.file_con) - 1:
                if self.file_con[self.__current_row + 1] is not '\n':  # 超前检测
                    self.__current_row += 1
                else:
                    break
        elif ch == '=':  # /=
            word = self.file_con[self.__current_row - 1:self.__current_row + 1]
            self.token.token_append((self.__current_line, word, self.recorder.code['/=']))
        else:  # / 除法
            self.__current_row -= 1
            word = self.file_con[self.__current_row]
            self.token.token_append((self.__current_line, word, self.recorder.code['/']))

    def judge_char(self):
        if (self.__current_row+1) < len(self.file_con):
            word = self.file_con[self.__current_row+1]  # 超前检测
            if word is not '\n' and self.__current_row < len(self.file_con) - 2:
                if self.file_con[self.__current_row+2] == '\'':  # 超前 2位 检测
                    self.token.token_append((self.__current_line, word, self.recorder.code['charRealNum']))
                    word = word

                    self.__current_row += 2
                else:
                    self.error.error_append((0, self.__current_line, '\''))
                    # TODO : 错误 缺少 ’

            else:
                pass
                self.error.error_append((1, self.__current_line, '\''))
                # TODO: 错误 多余 ‘

    def judge_string(self):
        self.__current_row += 1
        index = self.__current_row
        flag = 0
        while self.__current_row < len(self.file_con):
            if self.file_con[self.__current_row] is '\"':
                word = self.file_con[index:self.__current_row]
                self.token.token_append((self.__current_line, word, self.recorder.code['string']))
                word = word
                self.sign_table.signtable_append((word, 'string'))
                break
            elif self.file_con[self.__current_row] is '\n':
                flag = 1
                break
            else:
                self.__current_row += 1
        if flag == 1:
            # TODO: 错误 多余"
            self.error.error_append((1, self.__current_line, '\"'))
            self.__current_row = index  # 回到原来位置

    def next_is_sign(self, c): #判断== >> 这种运算符
        if self.__current_row + 1 < len(self.file_con):
            if self.file_con[self.__current_row + 1] == c:
                self.__current_row += 1
                return True
        return False

    def judge_arithmetic_operator(self):
        ch = self.file_con[self.__current_row]
        index = self.__current_row

        if ch == '%':
            self.next_is_sign('=')
        elif ch == '!':
            self.next_is_sign('=')
        elif ch == '=':
            self.next_is_sign(ch)
        elif (ch == '+') or (ch == '-'):
            if self.next_is_sign('=') or self.next_is_sign(ch):
                pass
        elif ch == '*':
            self.next_is_sign('=')
        elif ch == '|':
            if self.next_is_sign('=') or self.next_is_sign("|"):
                pass
        elif ch == '&':
            if self.next_is_sign('=') or self.next_is_sign("&"):
                pass
        elif ch == '>':
            if self.next_is_sign('=') or (self.next_is_sign(">") and self.next_is_sign("=")):
                pass
        elif ch == '<':
            if self.next_is_sign('=') or (self.next_is_sign('<') and self.next_is_sign('=')):
                pass
        else:
            return

        word = self.file_con[index:self.__current_row + 1]
        self.token.token_append((self.__current_line, word, self.recorder.code[word]))

    def judge_delimiter(self):
        word = self.file_con[self.__current_row]
        self.token.token_append((self.__current_line, word, self.recorder.code[word]))

    def start_scanner(self):
        print(self.file_con)
        self.__current_row = 0
        while self.__current_row < len(self.file_con):
            ch = self.file_con[self.__current_row]
            if not (ch == ' ' or ch == '\t'):
                if ch == '\n' or ch == '\r\n':
                    self.__current_line += 1
                elif ch.isalpha() or ch == '_':  # 关键字 标识符
                    self.judge_alpha()

                elif ch.isdigit():  # 数字
                    self.judge_number()


                elif ch == '/':  # 注释 或 除法
                    self.judge_sign_multi()

                elif ch == '#':  # #
                    pass
                elif ch == '\'':  # 字符
                    self.judge_char()

                elif ch == '\"':  # 字符串
                    self.judge_string()

                elif ch in self.recorder.basic_arithmetic_operator:  # 算数运算符
                    self.judge_arithmetic_operator()

                elif ch in self.recorder.delimiters:
                    self.judge_delimiter()

                else:
                    self.error.error_append((2, self.__current_line, ch))
                    # TODO: 错误 无法识别的符号
            self.__current_row += 1

    def return_inf(self):
        return self.error

    def save_file(self):
        self.token.save_file()
        self.error.save_file()

    def read_file(self):
        token = self.token.read_file()
        error = self.error.read_file()
        # print(token, sign_table, error)
        return token, error

    def run(self):
        self.start_scanner()
        self.save_file()
        # self.error.show()
        self.token.show()




if __name__ == "__main__":
    exp="""
    int a = 1 ;

    void main(){
    
        int result ;
        int N = read() ;
        int M = read() ;
        
        if (M >= N)result = M ;
        else result = N;
        a = result + 100 ;
        write(a);

}
    """
    lexer = Lexer(text=exp)
    lexer.run()
