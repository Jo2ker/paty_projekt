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

def spustit_test(jmno_testu):
    """Spustí jeden test podle názvu a vrátí výsledek."""
    result_stream = io.StringIO()
    sys.stdout = result_stream
    try:
        pytest.main(["-q", "--disable-warnings", "-k", jmno_testu])
    finally:
        sys.stdout = sys.__stdout__
        vysledek = result_stream.getvalue()
    return vysledek

def spustit_test_v_seznamu():
    """Vybere a spustí test ze seznamu."""
    wyber = seznam_listbox.curselection()
    if not wyber:
        messagebox.showwarning("Varování", "Vyberte test k spuštění.")
        return
    jmno_testu = seznam_listbox.get(wyber)
    vysledek = spustit_test(jmno_testu)
    messagebox.showinfo(f"Výsledek {jmno_testu}", vysledek)

def spustit_vsechny():
    """Spustí všechny testy a vypíše výsledek."""
    result_stream = io.StringIO()
    sys.stdout = result_stream
    try:
        pytest.main(["-q", "--disable-warnings"])
    finally:
        sys.stdout = sys.__stdout__
        vysledek = result_stream.getvalue()
    messagebox.showinfo("Výsledek testů", vysledek)

def testovac_gui():
    """Okno s výběrem testů a tlačítky pro spuštění."""
    okno = tk.Toplevel(root)
    okno.title("Testy")
    okno.geometry("400x350")

    global seznam_listbox
    seznam_listbox = tk.Listbox(okno, height=12)
    for t in seznam_testu:
        seznam_listbox.insert(tk.END, t)
    seznam_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

    btn_spustit_jeden = tk.Button(okno, text="Spustit vybraný test", command=spustit_test_v_seznamu)
    btn_spustit_jeden.pack(pady=5)

    btn_spustit_vse = tk.Button(okno, text="Spustit všechny testy", command=spustit_vsechny)
    btn_spustit_vse.pack(pady=5)

# -----------------------------------
# Funkce pro GUI operace
# -----------------------------------
def refresh_treeview(tree):
    """Aktualizuje seznam úkolů v Treeview."""
    for item in tree.get_children():
        tree.delete(item)
    ukoly = nacist_ukoly_z_databaze()
    for u in ukoly:
        tree.insert('', 'end', values=(u['id'], u['nazev'], u['stav']))

def pridej_ukol():
    nazev = simpledialog.askstring("Nový úkol", "Zadejte název úkolu (max 50 znaků):")
    if nazev is None:
        return
    popis = simpledialog.askstring("Nový úkol", "Zadejte popis úkolu (max 200 znaků):")
    if popis is None:
        return
    success = uloz_ukol_do_databaze(nazev, popis)
    if success:
        messagebox.showinfo("Úspěch", "Úkol byl přidán!")
        refresh_treeview(tree)
    else:
        messagebox.showerror("Chyba", "Nepodařilo se přidat úkol.")

def aktualizovat_stav():
    """Změní stav vybraného úkolu."""
    vybrany = tree.selection()
    if not vybrany:
        messagebox.showwarning("Varování", "Nejprve vyberte úkol ke změně stavu.")
        return
    row = tree.item(vybrany[0])['values']
    id_ukolu = row[0]
    current_stav = row[2]
    novy_stav = simpledialog.askstring("Změna stavu", 
        f"Zadejte nový stav ('nezahájeno', 'hotovo', 'probíhá')\nSoučasný stav: {current_stav}")
    if novy_stav not in ('nezahájeno', 'hotovo', 'probíhá'):
        messagebox.showerror("Chyba", "Neplatný stav.")
        return
    success = zmenit_stav_ukolu_v_databazi(id_ukolu, novy_stav)
    if success:
        messagebox.showinfo("Úspěch", "Stav byl změněn.")
        refresh_treeview(tree)
    else:
        messagebox.showerror("Chyba", "Nepodařilo se změnit stav úkolu.")

def odstranit_ukol():
    """Mazání vybraného úkolu."""
    vybrany = tree.selection()
    if not vybrany:
        messagebox.showwarning("Varování", "Vyberte úkol ke smazání.")
        return
    row = tree.item(vybrany[0])['values']
    id_ukolu = row[0]
    nazev = row[1]
    if messagebox.askyesno("Potvrzení", f"Opravdu chcete odstranit úkol '{nazev}'?"):
        success = odstranit_ukol_z_databaze(id_ukolu)
        if success:
            messagebox.showinfo("Úspěch", "Úkol byl odstraněn.")
            refresh_treeview(tree)
        else:
            messagebox.showerror("Chyba", "Nepodařilo se odstranit úkol.")

def vyber_a_spust_gui():
    """Okno s výběrem akcí: Přidat, Změnit, Odstranit."""
    okno = tk.Toplevel(root)
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

root = tk.Tk()
root.title("Správce úkolů")
root.geometry("600x400")

# Treeview seznamu úkolů
columns = ("ID", "Název", "Stav")
tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=200, anchor='center')
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Tlačítka
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)


btn_pridat = tk.Button(frame_buttons, text="Přidat úkol", command=pridej_ukol)
btn_pridat.pack(side=tk.LEFT, padx=5)

btn_aktualiz = tk.Button(frame_buttons, text="Aktualizovat stav", command=aktualizovat_stav)
btn_aktualiz.pack(side=tk.LEFT, padx=5)

btn_smazat = tk.Button(frame_buttons, text="Smazat", command=odstranit_ukol)
btn_smazat.pack(side=tk.LEFT, padx=5)

btn_testovat = tk.Button(root, text="Testovat", command=testovac_gui)
btn_testovat.pack(pady=10)

# Obnova seznamu při spuštění
refresh_treeview(tree)

# Aktualizace seznamu úkolů při spuštění
refresh_treeview(tree)

root.mainloop()

