#!python3
# -*- coding: utf-8 -*-

""" 
Script para testar tarefas de laboratório de MC102.
    
    Uso: python3 tester.py

O programa lab<x>.py será testado com todos os arquivos arq<i>.in
encontrados no diretório corrente. Os testes serão iniciados com i
igual a 01 e serão interrompidos quando arq<i>.in não for encontrado.

As saídas serão comparadas com os arquivos arq<i>.out.
"""

import os
import subprocess
import re
import argparse


#================#
#   ARG PARSER   #
#================#

parser = argparse.ArgumentParser(description="""\
    Script para testar tarefas de laboratório de MC102.

O programa lab<x>.py será testado com todos os arquivos arq<i>.in
encontrados no diretório corrente. Os testes serão iniciados com i
igual a 01 e serão interrompidos quando arq<i>.in não for encontrado.

As saídas serão comparadas com os arquivos arquivos arq<i>.out.
""", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Mostra a diferença entre as respostas quando um teste não passa.')
parser.add_argument('--quiet', '-q', action='store_true',
                    help='Mostra apenas os testes que falharem.')
parser.add_argument('--summary', '-s', action='store_true',
                    help='Exibe apenas o sumário.')
parser.add_argument('--silent', '-x', action='store_true',
                    help='Não exibe nada na tela.')
                    # --file / -f
args = parser.parse_args()
VERBOSE, QUIET, SILENT = args.verbose, args.quiet, args.silent


#=============#
#   HELPERS   #
#=============#


COLORS = {
    "reset": "\u001b[0m",
    "red": "\u001b[31m",
    "green": "\u001b[32m",
    "yellow": "\u001b[33m",
    "blue": "\u001b[34m",
    "magenta": "\u001b[35m",
    "cyan": "\u001b[36m",
    "white": "\u001b[37m",
}

path = os.path.dirname(os.path.abspath(__file__))
def abspath(filename):
    return os.path.normpath(os.path.join(path, filename))


def diff_str(file1, text):
    with open(file1, "r") as fl:
        filecontent = fl.read()
    if filecontent == text:
        return None
    else:
        return filecontent, text


def log(msg, level=0):
    if SILENT: return None
    elif level == 1:
        print(f"{COLORS['red']}{msg}{COLORS['reset']}")  # red
    elif QUIET:
        return None
    elif level == 2:
        print(f"{COLORS['green']}{msg}{COLORS['reset']}")  # green
    elif level == 3:
        print(f"{COLORS['yellow']}{msg}{COLORS['reset']}")  # yellow
    else:
        print(msg)


#=========================#
#   LOCALIZAR lab<x>.py   #
#=========================#

r = re.compile(r'lab\d\d.py')
for file in os.listdir(path):
    if r.match(file):
        labfile = file
        break
else:
    log("Código do laboratório não encontrado.", 1)
    exit(1)


#============#
#   TESTES   #
#============#

i = 1
testfile = "arq{:02d}.in".format(i)

tests_passed = 0
tests_failed = 0

while os.path.exists(testfile):
    resfile = "arq{:02d}.out".format(i)
    if not os.path.exists(resfile):
        log("Arquivo", resfile, "não encontrado.", 1)
        i += 1
        continue

    output = subprocess.check_output(
        f'python3 "{labfile}" < "{testfile}"', shell=True, text=True)

    diff = diff_str(resfile, output)

    if diff is None:
        if not SUMMARY:
            log("Teste {:02d}: resultado correto".format(i), 2)
        tests_passed += 1
    else:
        if not SUMMARY:
            log("Teste {:02d}: resultado incorreto".format(i), 1)
        if VERBOSE:
            log(">>> Sua resposta:", 3)
            log(diff[1])
            log(">>> Resposta correta:", 3)
            log(diff[0])
        tests_failed += 1

    i += 1
    testfile = "arq{:02d}.in".format(i)

if tests_passed + tests_failed == 0:
    log("Nenhum teste realizado. Execute o programa com a flag -h para obter ajuda.", 1)
    exit(1)

log("Sumário: | {green}Passou  {red}Falhou  {blue}Total{reset}".format(**COLORS))
log("         | {green}{passed: >6}  {red}{failed: >6}  {blue}{total: >5}{reset}".format(passed=tests_passed, failed=tests_failed, total=tests_passed+tests_failed, **COLORS))