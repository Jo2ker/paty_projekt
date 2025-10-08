import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pytest
import io
import sys
from paty_projekt import (uloz_ukol_do_databaze, nacist_ukoly_z_databaze,
 zmenit_stav_ukolu_v_databazi, odstranit_ukol_z_databaze, odstranit_ukol)

# -----------------------------------
# Funkce pro testování v GUI
# -----------------------------------

seznam_testu = [
    "test_pridat_ukol_pozitivni",
    "test_pridat_ukol_negativni",
    "test_aktualizovat_stav_pozitivni",
    "test_aktualizovat_stav_negativni",
    "test_odstranit_ukol_pozitivni",
    "test_odstranit_ukol_negativni"
]

def spustit_test(jmeno_testu):
    """Spustí jeden test podle názvu a vrátí výsledek."""
    zasobnik = io.StringIO()
    sys.stdout = zasobnik
    try:
        pytest.main(["-q", "--disable-warnings", "-k", jmeno_testu])
    finally:
        sys.stdout = sys.__stdout__
        vysledek = zasobnik.getvalue()
    return vysledek

def spustit_test_v_seznamu():
    """Vybere a spustí test ze seznamu."""
    vyber = seznam_listbox.curselection()
    if not vyber:
        messagebox.showwarning("Varování", "Vyberte test k spuštění.")
        return
    jmeno_testu = seznam_listbox.get(vyber)
    vysledek = spustit_test(jmeno_testu)
    messagebox.showinfo(f"Výsledek {jmeno_testu}", vysledek)

def spustit_vsechny():
    """Spustí všechny testy a vypíše výsledek."""
    zasobnik = io.StringIO()
    sys.stdout = zasobnik
    try:
        pytest.main(["-q", "--disable-warnings"])
    finally:
        sys.stdout = sys.__stdout__
        vysledek = zasobnik.getvalue()
    messagebox.showinfo("Výsledek testů", vysledek)

def testovac_gui():
    """Okno s výběrem testů a tlačítky pro spuštění."""
    okno = tk.Toplevel(koren)
    okno.title("Testy")
    okno.geometry("400x350")

    global seznam_listbox
    seznam_listbox = tk.Listbox(okno, height=12)
    for _ in seznam_testu:
        seznam_listbox.insert(tk.END, _)
    seznam_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

    tlc_spustit_jeden = tk.Button(okno, text="Spustit vybraný test", command=spustit_test_v_seznamu)
    tlc_spustit_jeden.pack(pady=5)

    tlc_spustit_vse = tk.Button(okno, text="Spustit všechny testy", command=spustit_vsechny)
    tlc_spustit_vse.pack(pady=5)

# -----------------------------------
# Funkce pro GUI operace
# -----------------------------------
def aktualizace_treeview(tree):
    """Aktualizuje seznam úkolů v Treeview."""
    for vetev in tree.get_children():
        tree.delete(vetev)
    ukoly = nacist_ukoly_z_databaze()
    for ukol in ukoly:
        tree.insert('', 'end', values=(ukol['id'], ukol['nazev'], ukol['stav']))

def pridej_ukol():
    nazev = simpledialog.askstring("Nový úkol", "Zadejte název úkolu (max 50 znaků):")
    if nazev is None:
        return
    popis = simpledialog.askstring("Nový úkol", "Zadejte popis úkolu (max 200 znaků):")
    if popis is None:
        return
    uspesne = uloz_ukol_do_databaze(nazev, popis)
    if uspesne:
        messagebox.showinfo("Úspěch", "Úkol byl přidán!")
        aktualizace_treeview(strom)
    else:
        messagebox.showerror("Chyba", "Nepodařilo se přidat úkol.")

def aktualizovat_stav():
    """Změní stav vybraného úkolu."""
    vybrany = strom.selection()
    if not vybrany:
        messagebox.showwarning("Varování", "Nejprve vyberte úkol ke změně stavu.")
        return
    radek = strom.item(vybrany[0])['values']
    id_ukolu = radek[0]
    soucasny_stav = radek[2]
    novy_stav = simpledialog.askstring("Změna stavu", 
        f"Zadejte nový stav ('nezahájeno', 'hotovo', 'probíhá')\nSoučasný stav: {soucasny_stav}")
    if novy_stav not in ('nezahájeno', 'hotovo', 'probíhá'):
        messagebox.showerror("Chyba", "Neplatný stav.")
        return
    uspesne = zmenit_stav_ukolu_v_databazi(id_ukolu, novy_stav)
    if uspesne:
        messagebox.showinfo("Úspěch", "Stav byl změněn.")
        aktualizace_treeview(strom)
    else:
        messagebox.showerror("Chyba", "Nepodařilo se změnit stav úkolu.")

def odstranit_ukol():
    """Mazání vybraného úkolu."""
    vybrany = strom.selection()
    if not vybrany:
        messagebox.showwarning("Varování", "Vyberte úkol ke smazání.")
        return
    radek = strom.item(vybrany[0])['values']
    id_ukolu = radek[0]
    nazev = radek[1]
    if messagebox.askyesno("Potvrzení", f"Opravdu chcete odstranit úkol '{nazev}'?"):
        uspesne = odstranit_ukol_z_databaze(id_ukolu)
        if uspesne:
            messagebox.showinfo("Úspěch", "Úkol byl odstraněn.")
            aktualizace_treeview(strom)
        else:
            messagebox.showerror("Chyba", "Nepodařilo se odstranit úkol.")

def vyber_a_spust_gui():
    """Okno s výběrem akcí: Přidat, Změnit, Odstranit."""
    okno = tk.Toplevel(koren)
    okno.title("Možnosti")
    okno.geometry("300x150")

    def prikaz_pridat():
        okno.destroy()
        pridej_ukol()

    def prikaz_zmenit():
        okno.destroy()
        aktualizovat_stav()

    def prikaz_mazat():
        okno.destroy()
        odstranit_ukol()

    tk.Label(okno, text="Vyberte akci:").pack(pady=10)

    tk.Button(okno, text="Přidat úkol", command=prikaz_pridat).pack(pady=5)
    tk.Button(okno, text="Změnit stav", command=prikaz_zmenit).pack(pady=5)
    tk.Button(okno, text="Odstranit úkol", command=prikaz_mazat).pack(pady=5)

# -----------------------------------
# Hlavička hlavního okna
# -----------------------------------

koren = tk.Tk()
koren.title("Správce úkolů")
koren.geometry("600x400")

# Treeview seznamu úkolů
bunky = ("ID", "Název", "Stav")
strom = ttk.Treeview(koren, columns=bunky, show='headings')
for bunka in bunky:
    strom.heading(bunka, text=bunka)
    strom.column(bunka, width=200, anchor='center')
strom.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Tlačítka
ramec_tlacitek = tk.Frame(strom)
ramec_tlacitek.pack(pady=10)


tlc_pridat = tk.Button(koren, text="Přidat úkol", command=pridej_ukol)
tlc_pridat.pack(side=tk.LEFT, padx=5)

tlc_aktualizovat = tk.Button(koren, text="Aktualizovat stav", command=aktualizovat_stav)
tlc_aktualizovat.pack(side=tk.LEFT, padx=5)

tlc_smazat = tk.Button(koren, text="Smazat", command=odstranit_ukol)
tlc_smazat.pack(side=tk.LEFT, pady=5)

tlc_testovat = tk.Button(koren, text="Testovat", command=testovac_gui)
tlc_testovat.pack(side=tk.LEFT, pady=5)

# Obnova seznamu při spuštění
aktualizace_treeview(strom)

# Aktualizace seznamu úkolů při spuštění
aktualizace_treeview(strom)

koren.mainloop()

