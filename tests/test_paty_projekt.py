import pytest
import mysql.connector
from mysql.connector import Error
from src.paty_projekt import (
    uloz_ukol_do_databaze,
    zmenit_stav_ukolu_v_databazi,
    odstranit_ukol_z_databaze,
)

# Funkce pro připojení k databazi
def pripojeni_k_testovaci_databazi():
    """
    Připojí se k testovací databázi 'ukoly_db_test'
    na lokálním serveru MySQL s danými přihlašovacími údaji.

    Návratova hodnota:
        Pokud je připojení úspěšné, vrátí objekt spojení.
        Pokud dojde k chybě, vypíše chybové hlášení a vrátí None.
    """
    try:
        pripojeni = mysql.connector.connect(
            host="127.0.0.1", user="root", password="1234", database="ukoly_db_test"
        )
        if pripojeni.is_connected():
            return pripojeni
    except Error as chyba:
        print(f"Chyba při připojení k databázi: {chyba}\n")
        return None


# vytvoření tabulky pokud neexistuje
def vytvoreni_testovaci_tabulky_v_databazi(pripojeni):
    """
    Vytvoří v předaném spojení databáze tabulku 'ukoly', pokud ještě neexistuje.
    Pokud dojde k chybě, vypíše chybové hlášení

    Parametry:
        pripojeni: aktivní spojení s databází.
    """
    try:
        kurzor = pripojeni.cursor()
        kurzor.execute(
            """
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT,
                stav ENUM('nezahájeno', 'hotovo', 'probíhá') NOT NULL,
                datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        pripojeni.commit()
        print("\nTabulka 'ukoly' je připravena.\n")
    except Error as chyba:
        print(f"Chyba při vytváření tabulky: {chyba}\n")
    finally:
        if "kurzor" in locals():
            kurzor.close()
        if "pripojeni" in locals():
            pripojeni.close()


@pytest.fixture(scope="session", autouse=True)
def pripravit_testovaci_databazi():
    """
    Fixture, která při startu testovací relace:
    - Připraví testovací databázi (vytvoří tabulku, pokud neexistuje)
    - Po ukončení všech testů tabulku odstraní
    - Spouští se automaticky (autouse=True, scope='session')
    """

    # při startu testů vytvoření tabulky
    pripojeni = pripojeni_k_testovaci_databazi()
    if pripojeni:
        vytvoreni_testovaci_tabulky_v_databazi(pripojeni)
        pripojeni.close()

    yield  # běh testů

    # po všech testech smazání tabulky
    pripojeni = pripojeni_k_testovaci_databazi()
    if pripojeni:
        kurzor = pripojeni.cursor()
        kurzor.execute("DROP TABLE IF EXISTS ukoly")
        pripojeni.commit()
        print("\nTabulka 'ukoly' je odstraněna.\n")
        kurzor.close()
        pripojeni.close()


@pytest.fixture
def transakce():
    """
    Fixture, která před každým testem:
    - Připojí se k testovací databázi a zahájí transakci.
    - Po skončení testu provede rollback všech změn.
    - Zabezpečuje izolaci testů
    """
    pripojeni = pripojeni_k_testovaci_databazi()
    if not pripojeni:
        pytest.skip("Nelze připojit k testovací databázi")
    pripojeni.start_transaction()
    yield pripojeni
    pripojeni.rollback()
    pripojeni.close()


# Test přidání úkolu - pozitivní
def test_pridat_ukol_pozitivni(transakce):
    """
    Test, který ověřuje, že funkce uloží úkol se správnými daty do databáze.
    Po úspěšném vložení kontroluje, že úkol je skutečně v databázi.
    """

    uspesne = uloz_ukol_do_databaze("Test název", "Test popis", pripojeni=transakce)
    assert uspesne

    kurzor = transakce.cursor(dictionary=True)
    kurzor.execute("SELECT * FROM ukoly WHERE nazev='Test název'")
    zaznam = kurzor.fetchone()
    kurzor.close()
    assert zaznam is not None


# Test přidání úkolu - negativní (například prázdný název)
def test_pridat_ukol_negativni(transakce):
    """
    Test, který ověřuje, že funkce neuloží úkol s neplatnými vstupy, například s prázdným názvem.
    Očekává se, že funkce vrátí False, protože údaje jsou neplatné.
    """

    uspesne = uloz_ukol_do_databaze("", "Název příliš krátký", pripojeni=transakce)
    assert not uspesne


# Test aktualizace stavu - pozitivní
def test_aktualizovat_stav_pozitivni(transakce):
    """
    Test ověřuje, že funkce správně aktualizuje stav existujícího úkolu v databázi.
    - Nejprve vloží testovací úkol.
    - Zjistí jeho ID.
    - Aktualizuje jeho stav na 'hotovo'.
    - Ověří, že stav byl skutečně změněn v databázi.
    """

    # Nejprve vložíme testovací úkol
    uspesne_vlozeno = uloz_ukol_do_databaze("UC test", "Popis", pripojeni=transakce)
    assert uspesne_vlozeno

    # načteme jeho ID
    kurzor = transakce.cursor()
    kurzor.execute("SELECT id FROM ukoly WHERE nazev='UC test'")
    id_radek = kurzor.fetchone()
    kurzor.close()
    assert id_radek is not None
    id_ukolu = id_radek[0]

    # aktualizujeme stav
    uspesne = zmenit_stav_ukolu_v_databazi(id_ukolu, "hotovo", pripojeni=transakce)
    assert uspesne

    # ověříme změnu stavu v databázi
    kurzor = transakce.cursor()
    kurzor.execute("SELECT stav FROM ukoly WHERE id=%s", (id_ukolu,))
    stav = kurzor.fetchone()[0]
    kurzor.close()
    assert stav == "hotovo"


# Test aktualizace - negativní (neexistující ID)
def test_aktualizovat_stav_negativni(transakce):
    """
    Ověřuje, že funkce správně vrací False při pokusu aktualizovat stav úkolu s neexistujícím ID.
    - Pokud ID neexistuje v tabulce, úprava by měla selhat a vrátit False.
    """

    uspesne = zmenit_stav_ukolu_v_databazi(999999, "hotovo", pripojeni=transakce)
    assert not uspesne


# Test odstranění úkolu - pozitivní
def test_odstranit_ukol_pozitivni(transakce):
    """
    Ověřuje, že funkce správně odstraní existující úkol z databáze.
    - Nejprve vloží testovací úkol.
    - Zjistí jeho ID.
    - Odstraní úkol podle ID.
    - Ověří, že úkol již v databázi není.
    """

    # vložíme testovací úkol
    uspesne_vlozeno = uloz_ukol_do_databaze(
        "Ukolem k odstranění", "Popis", pripojeni=transakce
    )
    assert uspesne_vlozeno

    # načteme ID
    kurzor = transakce.cursor()
    kurzor.execute("SELECT id FROM ukoly WHERE nazev='Ukolem k odstranění'")
    id_radek = kurzor.fetchone()
    kurzor.close()
    assert id_radek is not None
    id_ukolu = id_radek[0]

    # odstraníme úkol
    uspesne = odstranit_ukol_z_databaze(id_ukolu, pripojeni=transakce)
    assert uspesne

    # ověříme, že je úkol smazán
    kurzor = transakce.cursor()
    kurzor.execute("SELECT * FROM ukoly WHERE id=%s", (id_ukolu,))
    zaznam = kurzor.fetchone()
    kurzor.close()
    assert zaznam is None


# Test odstranění úkolu - negativní
def test_odstranit_ukol_negativni(transakce):
    """
    Ověřuje, že funkce vrátí False při pokusu odstranění neexistujícího úkolu.
    - Pokud ID neexistuje v tabulce, operace by měla selhat a vrátit False.
    """

    uspesne = odstranit_ukol_z_databaze(999999, pripojeni=transakce)  # ID neexistuje
    assert not uspesne
