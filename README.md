# Script para testar tarefas de laboratório de MC102. <!-- omit in toc -->

Este script foi desenvolvido para testar as atividades de laboratório da disciplina MC102 frente aos testes disponibilizados na página da disciplina. É necessário ter o Python 3 instalado na máquina para executá-lo.

## Sumário <!-- omit in toc -->
- [Download](#download)
- [Instruções de uso](#instruções-de-uso)
- [Configurando o programa](#configurando-o-programa)
  - [Combinações de opções](#combinações-de-opções)
- [Utilização programática](#utilização-programática)

## Download
Faça o download deste repositório clicando no botão verde e em [Download ZIP](https://github.com/TDuarte02/Testador-MC102/archive/refs/heads/main.zip). O arquivo `tester.py` é seu arquivo de interesse. Mova-o para a localização apropriada de onde possa ser executado.

## Instruções de uso
O programa deve ser executado de um terminal (ou prompt de comando) da seguinte forma:
```shell
python3 tester.py
```
Para ver a ajuda do programa, execute:
```shell
python3 tester.py -h
```

Ao executar o programa da forma mais simples mostrada acima, ele procurará pelo arquivo `lab<d><d>.py`, em que `<d>` simboliza um dígito, no mesmo diretório do arquivo `tester.py`. Assim, arquivos como `lab00.py`, `lab05.py` e `lab99.py` serão encontrados pelo programa, nesta ordem.

Os testes (arquivos `.in` e `.out`) também serão procurados na mesma pasta. Um teste compreende um arquivo `<nome>.in` no mesmo diretório de outro arquivo `<nome>.out`, em que `<nome>` pode ser qualquer nome válido. Caso você esteja usando a suíte de testes do Susy, é provável que seus arquivos de teste sejam do tipo `arq<d><d>.in` e `arq<d><d>.out`.

Por padrão, você verá uma saída do tipo (mas talvez mais colorida):
```plain
Teste 01 (arq01): resultado correto
Teste 02 (arq02): resultado correto
Teste 03 (arq03): resultado correto
Teste 04 (arq04): resultado correto
Teste 05 (arq05): resultado correto
Teste 06 (arq06): resultado correto
Teste 07 (arq07): resultado correto
Teste 08 (arq08): resultado incorreto
Teste 09 (arq09): resultado incorreto
Teste 10 (arq10): resultado incorreto
Sumário: | Passou  Falhou  Total
         |      7       3     10
```

Se atente ao fato de que a comparação entre a resposta do seu programa e o arquivo de teste será feita *identicamente*, o que significa que espaços e quebras de linhas adicionais ou faltantes gerarão erros. Isso é feito por *design*, já que é o procedimento adotado pelo Susy. No entanto, até o momento, o programa não fornece uma indicação visual desses casos, mesmo quando `-v` é usado (veja abaixo), então esteja atento.

Veja a seção a seguir para instruções sobre como configurar a entrada e a saída.
## Configurando o programa

- Para escolher o arquivo `.py` a ser executado, use a opção `-f` (ou `--filename`):
```shell
python3 tester.py -f lab98.py
```
- Para escolher o diretório no qual procurar os arquivos de teste, use a opção `-d` (ou `--directory`):
```shell
python3 tester.py -d testes
```
As opções podem ser combinadas em qualquer ordem:
```shell
python3 tester.py -d testes -f lab98.py
```

- Para ver a comparação entre a resposta esperada e fornecida nos testes que falharam, use a chave `-v` (ou `--verbose`):
```shell
python3 tester.py -v
```
O resultado será algo como:
```plain
Teste 01 (arq01): resultado correto
Teste 10 (arq10): resultado incorreto
>>> Sua resposta:
Cartao nao concedido

>>> Resposta correta:
Cartao concedido
Sumário: | Passou  Falhou  Total
         |      1       1     2
```

- Para ver apenas o sumário final, use a opção `-s` (ou `--summary`).
```plain
Sumário: | Passou  Falhou  Total
         |      1       1     2
```

- Para ver apenas as mensagens de erro (incluindo os testes que não passarem), use a opção `-q` (ou `--quiet`).

- Para que o programa execute silenciosamente, use a opção `-x` (ou `--silent`). Esta opção pode parecer inútil, já que, aparentemente, o resultado do programa se torna invisível. O fato é que o *return code* do programa será igual a 0 (*success*) apenas quando todos os testes passarem, ou 1 em todos os outros casos. Dessa forma, é possível usar esta opção programaticamente para verificar se todos os testes passaram.
- Para salvar a saída do programa em um arquivo de texto, é recomendável desabilitar a utilização de cores. Para isso, use a opção `--no-colors`:
```shell
python3 tester.py -d tests -v --no-colors > resultado_teste.txt
```

### Combinações de opções
> Aqui, *combinação* se refere à utilização simultânea de duas ou mais opções. 
- As opções `-d` e `-f` podem ser combinadas sem nenhum efeito colateral. 
- As *flags* `-q` e `-s` (o mesmo que `-qs`) podem ser combinadas, gerando como saída apenas erros do programa, mas não testes que eventualmente não passarem.
- As demais *flags* podem ser combinadas, mas apenas a mais restrita terá efeito. Por exemplo, se `-q` e `-v` forem usadas, apenas `-q` terá efeito. Se, por outro lado, `-x` e `-q` forem usadas, apenas `-x` terá efeito e nada será escrito na *standard output*. 

## Utilização programática

Você também pode utilizar o `tester.py` de maneira programática, isto é, através de outro programa Python. Isso pode ser interessante para executar várias suites de teste de uma vez, para automatizar o código, ou apenas por diversão. A API do `tester.py` é orientada a objetos e se baseia em duas classes: `Logger` e `Tester`. Para testar o arquivo `script.py` com os arquivos de teste no diretório `./tests`, alguém escreveria:
```python
from tester import Tester, Logger
tester = Tester() # cria o objeto tester
result = tester.test("./tests", "script.py") # usa o método test para realizar a testagem
```
Neste caso, `result` será um `dict` contendo as estatísticas:
```plain
{'passed': 9, 'failed': 1, 'total': 10}
```
Essas estatísticas podem ser transformadas em um sumário:
```python
from tester import Tester, Logger
tester = Tester() # cria o objeto tester
result = tester.test("./tests", "script.py") # usa o método test para realizar a testagem
tester.summarize(**result) # imprime o sumário
```
Aqui, `tester.summarize(**result)` é o mesmo que `tester.summarize(result["passed"], result["failed"], result["total"])`.

Por padrão, o `Tester` usa o `Logger` padrão para o *output* dos dados. Você pode, no entanto, fornecer um Logger personalizado:
```python
from tester import Tester, Logger
logger = Logger(colored=False) # cria o objeto logger que não utilizará cores
tester = Tester(logger) # criar o tester injetando o logger personalizado
result = tester.test("./tests", "script.py")
tester.summarize(**result)
```
Isso é equivalente à seguinte linha de comando:
```shell
python3 tester.py -d ./tests -f script.py --no-colors
```
A diferença principal é que você é responsável por tratar as exceções que serão eventualmente lançadas.

Para mostrar as informações de debug:
```python
from tester import Tester, Logger
logger = Logger(verbose=True) # cria o objeto logger que imprimirá informações de debug
tester = Tester(logger) # criar o tester injetando o logger personalizado
result = tester.test("./tests", "script.py")
tester.summarize(**result)
```
Isso é, basicamente, equivalente à seguinte linha de comando:
```shell
python3 tester.py -d ./tests -f script.py -v
```

Um caso particularmente útil na utilização programática é não gerar nenhuma saída.
```python
from tester import Tester, Logger
logger = Logger(silent=True) # cria o objeto logger que não imprimirá nada
tester = Tester(logger) # criar o tester injetando o logger personalizado
result = tester.test("./tests", "script.py") # não imprime nada
tester.summarize(**result) # funciona independentemente do Logger fornecido.
```
Porém isso pode ser feito de forma mais enxuta:
```python
from tester import Tester
tester = Tester(silent=True) # criar o tester que usará um Logger silencioso.
result = tester.test("./tests", "script.py") # não imprime nada
tester.summarize(**result) # funciona independentemente do Logger fornecido.
```
Esse último snippet é, essencialmente, uma forma mais curta do exemplo anterior. Os dois são totalmente equivalentes.

Esses dois últimos snippets são equivalentes à linha de comando:
```shell
python3 tester.py -d ./tests -f script.py -x
```
Por outro lado, a versão programática é mais útil, já que retorna as estatísticas de qualquer forma.

As configurações do `Logger` seguem as mesmas considerações feitas na seção [Combinações de Opções](#combinações-de-opções).