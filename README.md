
**paty_projekt**

**Pátý projekt ENGETO akademie Tester s Pythonem**


**Popis projektu**

Jedná se o **správce úkolů**, který ukládá úkoly do **MySQL databáze**.
Program provádí operace **CRUD(Create, Read, Update, Delete)**.
Součástí programu je možnost využití **automatizovaných testů** 
na veškeré funkce spojené s **MySQL databází**. Program je možné spustit v **GUI**.

**Instalace knihoven**

Knihovny, které jsou použity v kódu jsou uložené v souboru requirements.txt.
Pro instalaci doporučuji použít nové virtuální prostředí a s naistalovaným manažerem spustit následovně:

**$ pip3 --version** *# ověřím verzi manažeru*
**$ pip3 --install -r requirements.txt** *# nainstalujeme knihovny*

**Nastavení MySQL**

Pomocí mysql.connector.connect() se pokoušíme navázat spojení s MySQL databází.

**host="localhost"**
- Označuje, že databáze běží lokálně (na stejném počítači jako tento skript).
**user="root"**
- Používá se uživatel root, což je výchozí administrátorský účet v MySQL.
**password="1234"**
- Heslo k účtu root.

**Spuštění projektu**

Spuštění souboru **paty_projekt.py** v rámci příkazového řádku.

**$paty_projekt.py**

Spuštění souboru **test_paty_projekt.py** v rámci příkazového řádku.

**$pytest -vs**

Spuštění souboru gui.py v rámci příkazového řádku.

**$qui.py**

