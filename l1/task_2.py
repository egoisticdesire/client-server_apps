"""
Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность кодов
(не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.
"""


def words_bytes_types_len(a):
    for i in a:
        word_to_byte = eval(f"b'{i}'") \
            if i.isascii() \
            else i
        print(f"{i} :: {type(i)}\n"
              f"{word_to_byte} :: {type(word_to_byte)} :: <length '{len(word_to_byte)}'>\n") \
            if i.isascii() \
            else print(f'"\033[31m{i}\033[0m" - невозможно записать в байтовом типе')


WORDS = [
        'class',
        'function',
        'method',
        'йцу',
]

words_bytes_types_len(WORDS)
