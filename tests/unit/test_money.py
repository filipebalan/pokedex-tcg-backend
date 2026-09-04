from decimal import Decimal
import pytest
from src.domain.value_objects.money import Money

def test_deve_somar_dois_valores_da_mesma_moeda() -> None:
    # Eu crio dois valores em dólar
    valor_um = Money(amount=Decimal("10.50"), currency="USD")
    valor_dois = Money(amount=Decimal("5.25"), currency="USD")

    # Eu realizo a soma
    resultado = valor_um.add(valor_dois)

    # Eu verifico se o resultado e a moeda estão corretos
    assert resultado.amount == Decimal("15.75")
    assert resultado.currency == "USD"

def test_deve_lancar_erro_ao_tentar_somar_moedas_diferentes() -> None:
    # Eu preparo moedas incompatíveis
    valor_dolar = Money(amount=Decimal("10.00"), currency="USD")
    valor_real = Money(amount=Decimal("10.00"), currency="BRL")

    # Eu valido que o domínio impede essa operação de negócio inválida
    with pytest.raises(ValueError, match="Não posso somar moedas diferentes"):
        valor_dolar.add(valor_real)

def test_deve_impedir_criacao_de_valor_negativo() -> None:
    # Eu testo a proteção contra valores negativos
    with pytest.raises(ValueError, match="não pode ser negativo"):
        Money(amount=Decimal("-1.00"), currency="USD")