from uuid import uuid4
from datetime import date
import pytest
from src.domain.entities.set import Set
from src.domain.entities.card import Card
from src.domain.value_objects.card_types import CardSupertype, EnergyType

def test_set_deve_ser_criado_com_sucesso() -> None:
    # Eu instancio um Set com dados válidos da primeira coleção clássica
    base_set = Set(
        id=uuid4(),
        external_id="base1",
        name="Base",
        series="Base",
        release_date=date(1999, 1, 9),
        total_cards=102,
    )

    assert base_set.name == "Base"
    assert base_set.total_cards == 102

def test_set_deve_falhar_quando_total_de_cartas_for_invalido() -> None:
    # Eu testo que uma coleção não pode ter zero cartas
    with pytest.raises(ValueError, match="maior que zero"):
        Set(
            id=uuid4(),
            external_id="base1",
            name="Base",
            series="Base",
            release_date=date(1999, 1, 9),
            total_cards=0,
        )

def test_card_deve_validar_hp_positivo_para_pokemon() -> None:
    # Eu garanto que o domínio bloqueia um Pokémon com HP inválido
    with pytest.raises(ValueError, match="HP de uma carta de Pokémon deve ser estritamente maior que zero"):
        Card(
            id=uuid4(),
            external_id="base1-4",
            name="Charizard",
            set_id=uuid4(),
            card_number="4",
            rarity="Rare Holo",
            supertype=CardSupertype.POKEMON,
            types=[EnergyType.FIRE],
            hp=-10,
            national_dex_number=6,
        )

def test_duas_entidades_com_mesmo_id_sao_iguais_mesmo_com_outros_campos_diferentes() -> None:
    # Eu testo o princípio do DDD: Entidades são comparadas por identidade (ID)
    mesmo_id = uuid4()
    set_id = uuid4()

    carta_versao_um = Card(
        id=mesmo_id,
        external_id="base1-4",
        name="Charizard",
        set_id=set_id,
        card_number="4",
        rarity="Rare Holo",
        supertype=CardSupertype.POKEMON,
    )

    carta_versao_dois = Card(
        id=mesmo_id,
        external_id="base1-4",
        name="Charizard Corrigido",  # Nome modificado
        set_id=set_id,
        card_number="4",
        rarity="Rare Holo",
        supertype=CardSupertype.POKEMON,
    )

    assert carta_versao_um == carta_versao_dois