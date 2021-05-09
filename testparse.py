#test lex parse

from Klang import kparser

while True:
    s = input("Kl:>")
    result = kparser.parse(s)
    print(result)
