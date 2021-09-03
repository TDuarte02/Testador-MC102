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


class Logger:
    NORMAL = 0
    ERROR = 1
    WARNING = 2
    SUCCESS = 3
    INFO = 4
    DEBUG = 10
    DEBUG2 = 11
    DEBUG3 = 12

    def __init__(self, colored=True, quiet=False, verbose=False, silent=False):
        self.colored = colored
        self.quiet = quiet
        self.verbose = verbose
        self.silent = silent

    def colorize(self, text, color):
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
        if not self.colored or color is None:
            return text
        return f"{COLORS[color]}{text}{COLORS['reset']}"

    def __call__(self, msg: str, level: int = 0):
        if self.silent:
            return
        if self.quiet and level != self.ERROR:
            return
        if not self.verbose and level >= self.DEBUG:
            return

        color = {
            self.NORMAL: None,        # normal
            self.ERROR: "red",       # error
            self.WARNING: "yellow",    # warning
            self.SUCCESS: "green",     # info
            self.INFO: "info",     # info
            self.DEBUG: None,        # debug (verbose)
            self.DEBUG2: "yellow",     # debug (verbose)
            self.DEBUG3: "blue"     # debug (verbose)
        }[level]
        if color is not None:
            print(self.colorize(msg, color))
        else:
            print(msg)


class Tester:
    def __init__(self, logger: Logger = None, silent: bool = False):
        """Creates a tester object with a customizable logger.

        Args:
            logger (Logger, optional): A Logger instance with your own configuration. If None, the default Logger is used. Defaults to None.
            silent (bool, optional): If True, the Logger will be called with silent=True and any other setting will be overriden. Defaults to False.
        """
        if logger is None or not isinstance(logger, Logger):
            self.logger = Logger(silent=silent)
        else:
            self.logger = logger

    def test(self, directory: str, scriptname: str, silent=False) -> dict:
        if not Tester.check_dir(directory):
            raise FileNotFoundError(f"Diretório {directory} não acessível.")
        if not Tester.check_file(scriptname):
            raise FileNotFoundError(f"Arquivo {scriptname} não acessível.")
        stats = {
            "passed": 0,
            "failed": 0,
            "total": 0,
        }

        infiles, outfiles = Tester.get_test_files(directory)
        for infile, outfile in zip(infiles, outfiles):
            stats["total"] += 1

            output = subprocess.check_output(
                f'python3 "{scriptname}" < "{infile}"', shell=True, text=True)

            diff = Tester.diff_str(outfile, output)

            if diff is None:
                if not silent:
                    self.logger("Teste {:02d} ({file}): resultado correto".format(
                        stats["total"], file=Tester.basename(infile)), self.logger.SUCCESS)
                stats["passed"] += 1
            else:
                if not silent:
                    self.logger("Teste {:02d} ({file}): resultado incorreto".format(
                        stats["total"], file=Tester.basename(infile)), self.logger.ERROR)
                    self.logger(">>> Sua resposta:", self.logger.DEBUG2)
                    self.logger(diff[1], self.logger.DEBUG)
                    self.logger(">>> Resposta correta:", self.logger.DEBUG2)
                    self.logger(diff[0], self.logger.DEBUG)
                stats["failed"] += 1
        return stats

    #=============#
    #   HELPERS   #
    #=============#

    @staticmethod
    def check_file(filename: str) -> bool:
        return os.path.isfile(filename) and os.access(filename, os.R_OK)

    @staticmethod
    def check_dir(directory: str) -> bool:
        """Checks if the given directory exists.

        Args:
            directory (str): The directory to check.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        return os.path.isdir(directory) and os.access(directory, os.R_OK)

    @staticmethod
    def get_test_files(directory: str) -> tuple:
        infiles = sorted(glob(os.path.join(directory, "*.in")))
        outfiles = [f"{x[:-2]}out" for x in infiles]
        outfiles_that_exists = [os.path.isfile(x) for x in outfiles]
        infiles = list(itertools.compress(infiles, outfiles_that_exists))
        outfiles = list(itertools.compress(outfiles, outfiles_that_exists))
        return infiles, outfiles

    @staticmethod
    def basename(path):
        return os.path.splitext(os.path.basename(path))[0]

    @staticmethod
    def diff_str(file1, text):
        with open(file1, "r") as fl:
            filecontent = fl.read()
        if filecontent == text:
            return None
        else:
            return filecontent, text

    def summarize(self, passed: int, failed: int, total: int) -> None:
        def _r(x): return self.logger.colorize(x, "red")
        def _g(x): return self.logger.colorize(x, "green")
        def _b(x): return self.logger.colorize(x, "cyan")
        p, f, t = f"{passed:>6}", f"{failed:>6}", f"{total:>5}"

        print(f"Sumário: | {_g('Passou')}  {_r('Falhou')}  {_b('Total')}")
        print(f"         | {_g(p)}  {_r(f)}  {_b(t)}")


if __name__ == "__main__":
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
    parser.add_argument('--no-colors', action='store_true',
                        help='Não utilizar cores para o output (útil para salvar a saída em um arquivo).')
    parser.add_argument('--filename', '-f',
                        help='Arquivo para ser executado (.py).')
    parser.add_argument('--directory', '-d',
                        help='Diretório dos arquivos de teste (.in e .out).')
    args = parser.parse_args()

    log = Logger(verbose=args.verbose, quiet=args.quiet,
                 silent=args.silent, colored=not args.no_colors)

    #========================#
    #   LOCALIZAR ARQUIVOS   #
    #========================#
    if args.directory is None:
        path = os.path.dirname(os.path.abspath(__file__))
    elif Tester.check_dir(args.directory):
        path = args.directory
    elif os.path.isfile(args.directory):
        log(f"{args.directory} é um arquivo, mas -d espera um diretório. Execute o programa com a opção -h para ver a ajuda.", log.ERROR)
        exit(1)
    else:
        log(f"O diretório {args.directory} não existe. Execute o programa com a opção -h para ver a ajuda.", log.ERROR)
        exit(1)

    def abspath(filename):
        return os.path.normpath(os.path.join(path, filename))

    if args.filename is None:
        r = re.compile(r'lab\d+.py')
        for file in os.listdir(path):
            if r.match(file):
                labfile = file
                break
        else:
            log("Código do laboratório não encontrado. Execute o programa com a opção -h para ver a ajuda.", log.ERROR)
            exit(1)
    elif Tester.check_file(args.filename):
        labfile = args.filename
    else:
        log(f"O arquivo {args.filename} não existe ou você não tem permissão para acessá-lo. Execute o programa com a opção -h para ver a ajuda.", log.ERROR)
        exit(1)

    #============#
    #   TESTES   #
    #============#

    tester = Tester(logger=log)
    stats = tester.test(path, labfile, args.summary)

    if not args.silent and not args.quiet:
        tester.summarize(**stats)

    if stats["total"] == 0:
        log("Nenhum teste realizado. Execute o programa com a flag -h para obter ajuda.", log.ERROR)
        exit(1)

    if stats["failed"] > 0:
        exit(1)
