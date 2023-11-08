from typing import Any

from source.helpers.avaliador_regex import AvaliadorRegex
from source.excecoes.expressao_invalida import ExpressaoInvalida
from source.excecoes.formato_desconhecido import FormatoDesconhecido
from source.modelos.regex_grupo_interesse import RegexGrupoInteresse
from source.modelos.habilidade import Habilidade
from source.io_manager import IOManager

class HabilidadeCalculadora(Habilidade):
    __REGEX_ACEITACAO = r'^([-,+]?\d+(\.\d+)?) ?([\+,\-,\*,\/]) ?([-,+]?\d+(\.\d+)?$)'
    __INDEX_GRUPO_NUMERO_ESQUERDA = 0
    __INDEX_GRUPO_OPERADOR = 2
    __INDEX_GRUPO_NUMERO_DIREITA = 3

    @property
    def textos_ajuda(self) -> list[str]:
        return [
            'Consigo resolver cálculos no formato: operando_1 operador operando_2',
            '\toperando_1 e operando_2 devem ser números;',
            '\toperador deve ser: +, -, * ou /;',
            '\texemplo: -5 * 56.78'
        ]

    def __init__(self, io_manager: IOManager) -> None:
        self.__io_manager = io_manager
        self.__avaliador_regex = AvaliadorRegex(HabilidadeCalculadora.__REGEX_ACEITACAO, [
            RegexGrupoInteresse(HabilidadeCalculadora.__INDEX_GRUPO_NUMERO_ESQUERDA, float),
            RegexGrupoInteresse(HabilidadeCalculadora.__INDEX_GRUPO_OPERADOR, str),
            RegexGrupoInteresse(HabilidadeCalculadora.__INDEX_GRUPO_NUMERO_DIREITA, float),
        ])

    def execute_ou_raise(self, comando: str) -> None:
        numero_esquerda, operador, numero_direita = self.__avaliar_comando(comando)
        resultado = self.__calcular(numero_esquerda, operador, numero_direita)
        self.__io_manager.imprimir(resultado)

    def __avaliar_comando(self, comando: str) -> list[Any]:
        try:
            return self.__avaliador_regex.avaliar(comando)
        except ExpressaoInvalida:
            raise FormatoDesconhecido()

    def __calcular(self, numero_esquerda: float, operador: str, numero_direita: float) -> str:
        match(operador):
            case '+': return f'{numero_esquerda + numero_direita}'
            case '-': return f'{numero_esquerda - numero_direita}'
            case '*': return f'{numero_esquerda * numero_direita}'
            case '/': return self.__try_dividir(numero_esquerda, numero_direita)
            case _: raise FormatoDesconhecido() # nunca atingido

    def __try_dividir(self, numero_esquerda: float, numero_direita: float) -> str:
        try:
            return f'{numero_esquerda / numero_direita}'
        except ZeroDivisionError:
            return 'Divisão inválida.'
