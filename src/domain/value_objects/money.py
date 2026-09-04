from decimal import Decimal
from dataclasses import dataclass

# Utilizo frozen=True para garantir imutabilidade (característica essencial de um Value Object)
# e slots=True para otimizar o uso de memória eliminando o dicionário interno padrão de instâncias Python.
@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        # Garanto a invariante de negócio: dinheiro não pode ter valor negativo neste contexto
        if self.amount < Decimal("0.00"):
            raise ValueError("O valor monetário não pode ser negativo.")
        
        # Como a classe é frozen (imutável), utilizo object.__setattr__ para normalizar a moeda em maiúsculas
        object.__setattr__(self, "currency", self.currency.upper())

    def add(self, other: "Money") -> "Money":
        # Eu impeço operações aritméticas entre moedas distintas
        if self.currency != other.currency:
            raise ValueError(f"Não posso somar moedas diferentes: {self.currency} e {other.currency}.")
        
        # Como o objeto é imutável, eu nunca altero o estado atual; eu retorno uma nova instância
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def multiply(self, factor: Decimal) -> "Money":
        # Eu valido que o multiplicador (ex: quantidade de cartas) seja positivo
        if factor < Decimal("0.00"):
            raise ValueError("O fator de multiplicação não pode ser negativo.")
        
        # Eu arredondo para duas casas decimais após a multiplicação
        valor_calculado = (self.amount * factor).quantize(Decimal("0.01"))
        return Money(amount=valor_calculado, currency=self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"