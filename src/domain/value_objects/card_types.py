from datetime import datetime
from enum import StrEnum
from dataclasses import dataclass
from uuid import UUID
from typing import Optional
from src.domain.value_objects.money import Money

# Eu utilizo StrEnum para que os valores sejam strings nativas,
# facilitando serialização em APIs e banco de dados sem conversão manual.
class CardSupertype(StrEnum):
    POKEMON = "Pokémon"
    TRAINER = "Trainer"
    ENERGY = "Energy"

class EnergyType(StrEnum):
    COLORLESS = "Colorless"
    DARKNESS = "Darkness"
    DRAGON = "Dragon"
    FAIRY = "Fairy"        # Mantido para integridade histórica de coleções legadas (XY, Sun & Moon)
    FIGHTING = "Fighting"
    FIRE = "Fire"
    GRASS = "Grass"
    LIGHTNING = "Lightning"
    METAL = "Metal"
    PSYCHIC = "Psychic"
    WATER = "Water"

# Eu modelo o PriceSnapshot como um Value Object (imutável):
# uma vez capturada a cotação no tempo, esse registro nunca mais é alterado (append-only).
@dataclass(frozen=True, slots=True)
class PriceSnapshot:
    card_id: UUID
    source: str
    captured_at: datetime
    market: Money
    low: Optional[Money] = None
    high: Optional[Money] = None

    def __post_init__(self) -> None:
        # Eu garanto que o identificador da fonte não seja uma string vazia
        if not self.source.strip():
            raise ValueError("A fonte da cotação (source) não pode ser vazia.")

        # Eu valido se as moedas informadas coincidem entre si
        if self.low and self.low.currency != self.market.currency:
            raise ValueError(f"Moeda do menor preço ({self.low.currency}) difere da moeda de mercado ({self.market.currency}).")
        if self.high and self.high.currency != self.market.currency:
            raise ValueError(f"Moeda do maior preço ({self.high.currency}) difere da moeda de mercado ({self.market.currency}).")

        # Eu valido a coerência econômica de mercado quando os limites existirem:
        # O menor preço (low) não pode ser maior que o preço de mercado (market)
        if self.low and self.low.amount > self.market.amount:
            raise ValueError("Inconsistência de mercado: o menor preço (low) não pode ser maior que o preço de mercado (market).")
        
        # O maior preço (high) não pode ser menor que o preço de mercado (market)
        if self.high and self.high.amount < self.market.amount:
            raise ValueError("Inconsistência de mercado: o maior preço (high) não pode ser menor que o preço de mercado (market).")