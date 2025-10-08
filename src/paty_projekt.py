import os
import mysql.connector
from mysql.connector import Error

ukoly = []

# vytvoření připojení databáze
def pripojeni_k_databazi():
    """
    Připojí se k databázi 'ukoly_db' na lokálním serveru MySQL s danými přihlašovacími údaji.
        
    Návratová hodnota:
       Pokud je připojení úspěšné, vypíše hlášení o úspěchu a vrátí objekt spojení.
       Pokud dojde k chybě, vypíše chybové hlášení a vrátí None. 
    """
    
    try:
        pripojeni = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='123QweaSdyxC',
            database='ukoly_db'
        )
        if pripojeni.is_connected():
            print("Úspěšně připojeno k databázi\n")
            return pripojeni
    except Error as chyba:
        print(f"Chyba při připojení k databázi: {chyba}\n")
        return None

# vytvoření tabulky pokud neexistuje
def vytvoreni_tabulky_v_databazi(pripojeni):
    """
    Vytvoří v předaném spojení databáze tabulku 'ukoly', pokud ještě neexistuje.
    Pokud dojde k chybě během vytváření, vypíše chybové hlášení.
    Po úspěšném nebo selhávajícím pokusu zavře spojení.
    
    Parametry:
        pripojeni: aktivní spojení s databází
    """
    
    try:
        kurzor = pripojeni.cursor()
        kurzor.execute("""
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT,
                stav ENUM('nezahájeno', 'hotovo', 'probíhá') NOT NULL,
                datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        pripojeni.commit()
        print("Tabulka 'ukoly' je připravena.\n")
    except Error as chyba:
        print(f"Chyba při vytváření tabulky: {chyba}\n")
    finally:
        kurzor.close()
        pripojeni.close()

def uloz_ukol_do_databaze(nazev, popis, pripojeni=None):
    """
    Uloží nový úkol do databáze s výchozím stavem 'nezahájeno'.
Ověří, že 'nazev' a 'popis' nejsou prázdné nebo obsahující pouze mezery.

    Parametry:
        nazev (str): název úkolu; nesmí být prázdný.
        popis (str): popis úkolu; nesmí být prázdný.
        pripojeni: Pokud není parametr zadán, bude použito defaultní připojení.

    Návratová hodnota:
        bool: úspěšnost operace.
    """
    # Kontrola platnosti vstupních dat
    if not nazev or not nazev.strip():
        return False
    if not popis or not popis.strip():
        return False

    if pripojeni is None:
        pripojeni = pripojeni_k_databazi()
        je_samostatne_spojeni = True
    else:
        je_samostatne_spojeni = False

    if not pripojeni:
        print("Nelze se připojit k databázi.\n")
        return False
    
    try:
        kurzor = pripojeni.cursor()
        kurzor.execute(
            "INSERT INTO ukoly (nazev, popis, stav) VALUES (%s, %s, %s)",
            (nazev, popis, 'nezahájeno')
        )
        pripojeni.commit()
        if kurzor.rowcount == 0:
            return False
        kurzor.fetchall()
        return True
    except Error as chyba:
        print(f"Chyba při ukládání úkolu do databáze: {chyba}\n")
        return False
    finally:
        if 'kurzor' in locals():
            kurzor.close()
        if 'je_samostatne_spojeni' in locals() and je_samostatne_spojeni:
            pripojeni.close()

def nacist_ukoly_z_databaze(pripojeni=None):
    """Načte a vrátí všechny úkoly se stavem 'nezahájeno' nebo 'probíhá' z databáze.
    
    Parametry:
        pripojeni: Pokud není předán parametr připojení, použije defaultní připojení.
    
    Návratová hodnota:
        list: seznam úkolů nebo prázdný seznam při chybě či nepoužitelných datech
        """
    try:
        if pripojeni is None:
            pripojeni = pripojeni_k_databazi()
            je_samostatne_spojeni = True
        else:
            je_samostatne_spojeni = False

        if not pripojeni:
            print("Nelze se připojit k databázi.\n")
            return []

        kurzor = pripojeni.cursor(dictionary=True)
        kurzor.execute(
            "SELECT id, nazev, popis, stav FROM ukoly WHERE stav IN ('nezahájeno', 'probíhá')"
        )
        ukoly = kurzor.fetchall()
        return ukoly
    except Error as chyba:
        print(f"Chyba při načítání úkolů: {chyba}\n")
        return []
    finally:
        if 'kurzor' in locals():
            kurzor.close()
        if 'je_samostatne_spojeni' in locals() and je_samostatne_spojeni:
            pripojeni.close()

def zmenit_stav_ukolu_v_databazi(id_ukolu, novy_stav, pripojeni=None):
    """Aktualizuje stav úkolu v databázi podle ID.
    
    Parametry:
        id_ukolu (int): ID úkolu v databázi.
        novy_stav (str): Nový stav ('nezahájeno', 'hotovo', 'probíhá').
        pripojeni: Pokud není předán parametr připojení, použije defaultní připojení.
    
    Návratová hodnota:
        bool: úspěšnost operace.
    """
    try:
        if pripojeni is None:
            pripojeni = pripojeni_k_databazi()
            je_samostatne_spojeni = True
        else:
            je_samostatne_spojeni = False

        if not pripojeni:
           print("Nelze se připojit k databázi.\n")
           return False
        kurzor = pripojeni.cursor()
        kurzor.execute(
            "UPDATE ukoly SET stav=%s WHERE id=%s",
            (novy_stav, id_ukolu)
        )
        pripojeni.commit()
        if kurzor.rowcount == 0:
            return False
        return True 
    except Error as chyba:
        print(f"Chyba při aktualizaci stavu: {chyba}\n")
        return False
    finally:
        if 'kurzor' in locals():
            kurzor.close()
        if 'je_samostatne_spojeni' in locals() and je_samostatne_spojeni:
            pripojeni.close()

def odstranit_ukol_z_databaze(id_ukolu, pripojeni=None):
    """Odstraní úkol s daným ID z databáze.
    
    Parametry:
        id_ukolu (int): ID úkolu v databázi.
        pripojeni: Pokud není předán parametr připojení, použije defaultní připojení.
        
    Návratová hodnota:
        bool: úspěšnost operace.
    """
    try:
        if pripojeni is None:
            pripojeni = pripojeni_k_databazi()
            je_samostatne_spojeni = True
        else:
            je_samostatne_spojeni = False

        if not pripojeni:
            print("Nelze se připojit k databázi.\n")
            return False
        kurzor = pripojeni.cursor()
        kurzor.execute("DELETE FROM ukoly WHERE id=%s", (id_ukolu,))
        pripojeni.commit()
        if kurzor.rowcount ==0:
            return False
        return True
        
    except Error as chyba:
        print(f"Chyba při odstraňování: {chyba}\n")
        return False
    finally:
        if 'kurzor' in locals():
            kurzor.close()
        if 'je_samostatne_spojeni' in locals() and je_samostatne_spojeni:
            pripojeni.close()

# hlavní menu programu
def hlavni_menu():
    """Spustí hlavní uživatelské rozhraní pro správu úkolů.
    Uživatel může přidávat, zobrazovat nebo odstraňovat úkoly,
    případně ukončit program."""
    
    while True:
        print("Správce úkolů - Hlavní menu\n")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Konec programu\n")

        volba = input("Vyberte možnost (1-5): ")
        print()

        if volba == '1':
            pridat_ukol()
            print()
        elif volba == '2':
            zobrazit_aktivni_ukoly()
            print()
        elif volba == '3':
            aktualizovat_ukol()
            print()
        elif volba == '4':
            odstranit_ukol()
            print()
        elif volba == '5':
            print("Konec programu.")
            break
        else:
            print("Neplatná volba, zkuste to znovu.\n")

# přidání úkolu v programu
def pridat_ukol():
    """
    Umožňuje uživateli zadat název a popis nového úkolu a tento úkol uložit do databáze.
    
    Před vložením provádí základní validaci:
    
    Název nesmí být prázdný nebo obsahovat pouze mezery a délka nesmí přesáhnout 50 znaků.
    Popis nesmí být prázdný nebo obsahovat pouze mezery a délka nesmí přesáhnout 200 znaků.
    
    Pokud jsou data platná, uloží je a případně přidá do seznamu úkolů.
    """

    while True:
        nazev = input("Zadejte název úkolu (max 50 znaků): ").strip()
        popis = input("Zadejte popis úkolu (max 200 znaků): ").strip()
        
        if not nazev or not popis:
            print("\nNázev ani popis úkolu nemohou být prázdné. Zkuste to znovu.\n")
        elif len(nazev) > 50:
            print("\nNázev úkolu je příliš dlouhý. Zkuste to znovu.\n")
        elif len(popis) > 200:
            print("\nPopis úkolu je příliš dlouhý. Zkuste to znovu.\n")
        else:
            uspesne = uloz_ukol_do_databaze(nazev, popis)
            if uspesne:
                # Přidat do seznamu, pokud existuje
                if 'ukoly' in globals():
                    ukoly.append({"nazev": nazev, "popis": popis})
                print(f'\nÚkol "{nazev}" byl úspěšně uložen.')
            break

        
# zobrazení úkolu v programu
def zobrazit_aktivni_ukoly():
    """
    Načte a zobrazí všechny úkoly se stavem 'nezahájeno' nebo 'probíhá' z databáze.
    Pokud žádné takové úkoly nejsou, vypíše informaci, že seznam je prázdný.
    Jinak vypíše ID, název, popis a stav každého aktivního úkolu.
    """

    ukoly = nacist_ukoly_z_databaze()

    if not ukoly:
        print("Žádné úkoly se stavem 'nezahájeno' nebo 'probíhá'.\n")
    else:
        print("Aktivní úkoly:\n")
        for ukol in ukoly:
            print(f"ID: {ukol['id']}")
            print(f"Název: {ukol['nazev']}")
            print(f"Popis: {ukol['popis']}")
            print(f"Stav: {ukol['stav']}\n")

# aktualizace stavu úkolu v programu
def aktualizovat_ukol():
    """
    Načte všechny úkoly, vybere podle ID a umožní změnit jejich stav.
    
    Zobrazí seznam úkolů.
    Uživatel zadá ID úkolu pro aktualizaci.
    Zvolí nový stav ('probíhá' nebo 'hotovo') a potvrdí změnu.
    Pokud je operace potvrzena, stav úkolu se aktualizuje v databázi.
    Pokud je zadané ID neexistující nebo operace není potvrzena, operace se neprovede.
    """

    ukoly = nacist_ukoly_z_databaze()

    if not ukoly:
        print("Žádné úkoly k aktualizaci.\n")
        return

    print("Seznam úkolů:\n")
    for ukol in ukoly:
        print(f"ID: {ukol['id']} | Název: {ukol['nazev']} | Stav: {ukol['stav']}")

    while True:
        try:
            volba = input("Zadejte ID úkolu, který chcete upravit: ").strip()
            id_ukolu = int(volba)
        except ValueError:
            print("Neplatné ID. Zkuste znovu.\n")
            continue

        shoda_ukolu = next((_ for _ in ukoly if _['id'] == id_ukolu), None)
        if not shoda_ukolu:
            print("ID neexistuje, zkuste znovu.\n")
            continue
        else:
            break

    while True:
        stav_volba = input("Zvolte nový stav ('probíhá' nebo 'hotovo'): ").strip().lower()
        if stav_volba in ['probíhá', 'hotovo']:
            break
        else:
            print("Neplatná volba. Zvolte 'probíhá' nebo 'hotovo'.\n")

    # Smyčka potvrzení operace
    while True:
        potvrdit = input(f"Chcete změnit stav úkolu '{shoda_ukolu['nazev']}' na '{stav_volba}'? (ano/ne): ").strip().lower()
        if potvrdit == 'ano':
            # provedeme aktualizaci
            potvrzeni = zmenit_stav_ukolu_v_databazi(id_ukolu, stav_volba)
            if potvrzeni:
                print("Stav úkolu byl úspěšně aktualizován.\n")
            else:
                print("Nepodařilo se aktualizovat stav úkolu.\n")
            break
        elif potvrdit == 'ne':
            print("Operace zrušena.\n")
            break
        else:
            print("Neplatná volba. Zadejte 'ano' nebo 'ne'.")

def odstranit_ukol():
    """
    Načte všechny úkoly, zobrazí je, a podle zadaného ID umožní smazání.
    
    Uživatel zadá ID úkolu k odstranění.
    Potvrdí operaci ('ano'/'ne').
    Pokud je operace potvrzena, úkol se odstraní z databáze.
    Pokud ID neexistuje nebo není potvrzeno, operace není provedena.
    """
    ukoly = nacist_ukoly_z_databaze()

    if not ukoly:
        print("Žádné úkoly k odstranění.\n")
        return

    print("Seznam úkolů:\n")
    for ukol in ukoly:
        print(f"ID: {ukol['id']} | Název: {ukol['nazev']} | Stav: {ukol['stav']}")

    while True:
        try:
            volba = input("Zadejte ID úkolu, který chcete odstranit: ").strip()
            id_ukolu = int(volba)
        except ValueError:
            print("Neplatné ID. Zkuste znovu.\n")
            continue

        shoda_ukolu = next((_ for _ in ukoly if _['id'] == id_ukolu), None)
        if not shoda_ukolu:
            print("ID neexistuje, zkuste znovu.\n")
            continue
        else:
            break

    # Potvrzení s opakováním, dokud nezadá správně
    while True:
        potvrdit = input(f"Opravdu chcete odstranit úkol '{shoda_ukolu['nazev']}'? (ano/ne): ").strip().lower()
        if potvrdit == 'ano':
            # provedeme odstranění
            potvrzeni = odstranit_ukol_z_databaze(id_ukolu)
            if potvrzeni:
                print("Úkol byl úspěšně odstraněn.\n")
            else:
                print("Nepodařilo se odstranit úkol.\n")
            break
        elif potvrdit == 'ne':
            print("Operace zrušena.\n")
            break
        else:
            print("Neplatná volba. Zadejte 'ano' nebo 'ne'.")

if __name__ == "__main__":
# Vytvoření připojení a tabulky v databázi jestli neexistuje
    pripojeni = pripojeni_k_databazi()
    if pripojeni:
        vytvoreni_tabulky_v_databazi(pripojeni)

#Spuštění programu
    hlavni_menu()