from re import Match, match as re_match
from typing import Any

from source.excecoes.expressao_invalida import ExpressaoInvalida
from source.modelos.regex_grupo_interesse import RegexGrupoInteresse

class AvaliadorRegex():
    def __init__(self, regex: str, grupos_interesse: list[RegexGrupoInteresse]) -> None:
        self.__regex = regex
        self.__grupos_interesse = grupos_interesse

    def avaliar(self, expressao: str) -> list[Any]:
        """
        Avalia se a expressão é aceita pelo Regex passado na incialização.\n
        Caso seja aceita, retorna uma lista com as variáveis capturadas pelos grupos de interesse já convertidas em seus respectivos tipos.\n
        Caso contrário, lança a exceção `ExpressaoInvalida`.
        """
        matches = self.__avaliar_regex(expressao)
        return self.__try_extrair_elementos(matches)

    def __avaliar_regex(self, expressao: str) -> Match[str]:
        matches = re_match(self.__regex, expressao)
        if not matches:
            raise ExpressaoInvalida()
        return matches

    def __try_extrair_elementos(self, matches: Match[str]) -> list[Any]:
        try:
            return self.__extrair_elementos(matches)
        except Exception:
            raise ExpressaoInvalida()

    def __extrair_elementos(self, matches: Match[str]) -> list[Any]:
        grupos = matches.groups()
        return [grupo_interesse.tipo(grupos[grupo_interesse.index]) for grupo_interesse in self.__grupos_interesse]
