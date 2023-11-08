from asyncio import AbstractEventLoop
from typing import Any, Optional

from source.excecoes.expressao_invalida import ExpressaoInvalida
from source.excecoes.falha_download import FalhaDownload
from source.excecoes.formato_desconhecido import FormatoDesconhecido
from source.excecoes.moeda_invalida import MoedaInvalida
from source.helpers.api_cotacoes import APICotacoes
from source.helpers.avaliador_regex import AvaliadorRegex
from source.io_manager import IOManager
from source.modelos.habilidade import Habilidade
from source.modelos.regex_grupo_interesse import RegexGrupoInteresse

class HabilidadeConversaoMoeda(Habilidade):
    __REGEX_ACEITACAO = r'^(\d+(\.\d+)?) para ([A-Za-z]+)$'
    __INDEX_QUANTIA = 0
    __INDEX_MOEDA = 2

    @property
    def textos_ajuda(self) -> list[str]:
        lista_moedas = self.__recuperar_lista_moedas_formatada()
        if not lista_moedas:
            return []

        return [
            'Posso converter um valor em Reais para outra moeda usando a cotação atual.',
            '\tO comando é: valor para codigo_moeda. Exempo: \"100 para USD\" converte 100 reais para dólares.',
            '\tA lista de moedas que tenho acesso é:',
        ] + lista_moedas

    def __recuperar_lista_moedas_formatada(self) -> list[str]:
        moedas = self.__obter_lista_moedas_da_api()
        return [f'\t\t{moeda}' for moeda in moedas]

    def __obter_lista_moedas_da_api(self) -> list[str]:
        try:
            return self.__running_loop.run_until_complete(self.__api.lista_moedas)
        except FalhaDownload:
            return []

    def __init__(self, running_loop: AbstractEventLoop, io_manager: IOManager) -> None:
        self.__running_loop = running_loop
        self.__api = APICotacoes(running_loop)
        self.__io_manager = io_manager
        self.__avaliador_regex = AvaliadorRegex(HabilidadeConversaoMoeda.__REGEX_ACEITACAO, [
            RegexGrupoInteresse(HabilidadeConversaoMoeda.__INDEX_QUANTIA, float),
            RegexGrupoInteresse(HabilidadeConversaoMoeda.__INDEX_MOEDA, str),
        ])

    def execute_ou_raise(self, comando: str) -> None:
        quantia, codigo_moeda = self.__avaliar_comando(comando)

        self.__io_manager.imprimir('Vou buscar a cotação atual e fazer a conversão...')
        cotacao = self.__try_obter_cotacao(codigo_moeda)
        if not cotacao:
            return

        self.__imprimir_resultado(quantia, cotacao, codigo_moeda)

    def __avaliar_comando(self, comando: str) -> list[Any]:
        try:
            return self.__avaliador_regex.avaliar(comando)
        except ExpressaoInvalida:
            raise FormatoDesconhecido()

    def __try_obter_cotacao(self, codigo_moeda: str) -> Optional[float]:
        try:
            return self.__running_loop.run_until_complete(self.__api.obter_cotacao(codigo_moeda))
        except MoedaInvalida:
            self.__io_manager.imprimir('Moeda inválida. Para obter uma lista de moedas digite ajuda.')
            return None
        except FalhaDownload:
            self.__io_manager.imprimir('Algo deu errado. Verifique sua conexão e tente com outra moeda.')
            return None

    def __imprimir_resultado(self, quantia: float, cotacao: float, codigo_moeda: str) -> None:
        nome_moeda = self.__running_loop.run_until_complete(self.__api.recuperar_nome_moeda(codigo_moeda))
        valor_convertido = self.__converter_valor(quantia, cotacao)
        self.__io_manager.imprimir(f'{valor_convertido} {nome_moeda}')

    def __converter_valor(self, quantia: float, cotacao: float) -> float:
        return round(quantia / cotacao, 2)
