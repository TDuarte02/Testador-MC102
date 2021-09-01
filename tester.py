#!python3
# -*- coding: utf-8 -*-

""" 
Script para testar tarefas de laboratório de MC102.
    
    Uso: python3 tester.py

O programa lab<x>.py será testado com todos os arquivos .in
encontrados no diretório corrente por padrão, e que tiverem
arquivos de mesmo nome, mas com extensão .out. 
Tanto o arquivo de script para ser testado quanto o diretório 
dos arquivos de teste podem ser configurados. Também é possível 
configurar a saída do programa. Execute 
    python3 tester.py --help
para mais detalhes.
"""

import os
from glob import glob
import itertools
import subprocess
import re
import argparse


#================#
#   ARG PARSER   #
#================#

parser = argparse.ArgumentParser(description="""\
    Script para testar tarefas de laboratório de MC102.

O programa lab<x>.py será testado com todos os arquivos .in
encontrados no diretório corrente por padrão, e que tiverem
arquivos de mesmo nome, mas com extensão .out. 
Tanto o arquivo de script para ser testado quanto o diretório 
dos arquivos de teste podem ser configurados.

As saídas serão comparadas identicamente com o arquivo .out,
então se atente a diferenças como espaços em branco e quebras
de linha.
""", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Mostra a diferença entre as respostas quando um teste não passa.')
parser.add_argument('--quiet', '-q', action='store_true',
                    help='Mostra apenas os testes que falharem.')
parser.add_argument('--summary', '-s', action='store_true',
                    help='Exibe apenas o sumário.')
parser.add_argument('--silent', '-x', action='store_true',
                    help='Não exibe nada na tela.')
parser.add_argument('--filename', '-f',
                    help='Arquivo para ser executado (.py).')
parser.add_argument('--directory', '-d',
                    help='Diretório dos arquivos de teste (.in e .out).')
args = parser.parse_args()
VERBOSE, QUIET, SUMMARY, SILENT = args.verbose, args.quiet, args.summary, args.silent


#=============#
#   HELPERS   #
#=============#


def get_test_files(directory: str) -> tuple:
    infiles = sorted(glob(os.path.join(directory, "*.in")))
    outfiles = [f"{x[:-2]}out" for x in infiles]
    outfiles_that_exists = [os.path.isfile(x) for x in outfiles]
    infiles = list(itertools.compress(infiles, outfiles_that_exists))
    outfiles = list(itertools.compress(outfiles, outfiles_that_exists))
    return infiles, outfiles


def basename(path):
    return os.path.splitext(os.path.basename(path))[0]


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


def diff_str(file1, text):
    with open(file1, "r") as fl:
        filecontent = fl.read()
    if filecontent == text:
        return None
    else:
        return filecontent, text


def log(msg, level=0):
    if SILENT:
        return None
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


#========================#
#   LOCALIZAR ARQUIVOS   #
#========================#


if args.directory is None:
    path = os.path.dirname(os.path.abspath(__file__))
elif os.path.isdir(args.directory):
    path = args.directory
elif os.path.isfile(args.directory):
    log(f"{args.directory} é um arquivo, mas -d espera um diretório. Rode o programa com a opção -h para ver a ajuda.", 1)
    exit(1)
else:
    log(f"O diretório {args.directory} não existe. Rode o programa com a opção -h para ver a ajuda.", 1)
    exit(1)


def abspath(filename):
    return os.path.normpath(os.path.join(path, filename))


if args.filename is None:
    r = re.compile(r'lab\d\d.py')
    for file in os.listdir(path):
        if r.match(file):
            labfile = file
            break
    else:
        log("Código do laboratório não encontrado. Rode o programa com a opção -h para ver a ajuda.", 1)
        exit(1)

elif os.path.isfile(args.filename):
    labfile = args.filename
else:
    log(f"O arquivo {args.filename} não existe. Rode o programa com a opção -h para ver a ajuda.", 1)
    exit(1)


#============#
#   TESTES   #
#============#


tests_passed = 0
tests_failed = 0
total_tests = 0

infiles, outfiles = get_test_files(path)
for infile, outfile in zip(infiles, outfiles):
    total_tests += 1

    output = subprocess.check_output(
        f'python3 "{labfile}" < "{infile}"', shell=True, text=True)

    diff = diff_str(outfile, output)

    if diff is None:
        if not SUMMARY:
            log("Teste {:02d} ({file}): resultado correto".format(
                total_tests, file=basename(infile)), 2)
        tests_passed += 1
    else:
        if not SUMMARY:
            log("Teste {:02d} ({file}): resultado incorreto".format(
                total_tests, file=basename(infile)), 1)
            if VERBOSE:
                log(">>> Sua resposta:", 3)
                log(diff[1])
                log(">>> Resposta correta:", 3)
                log(diff[0])
        tests_failed += 1

if total_tests == 0:
    log("Nenhum teste realizado. Execute o programa com a flag -h para obter ajuda.", 1)
    exit(1)

log("Sumário: | {green}Passou  {red}Falhou  {cyan}Total{reset}".format(**COLORS))
log("         | {green}{passed: >6}  {red}{failed: >6}  {cyan}{total: >5}{reset}".format(
    passed=tests_passed, failed=tests_failed, total=tests_passed + tests_failed, **COLORS))

if tests_failed > 0:
    exit(1)