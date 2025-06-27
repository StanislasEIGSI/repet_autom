import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.ttk import Combobox

# Fichier de données
MUSICIENS_FILE = "musiciens.csv"

# Liste d'instruments proposés
INSTRUMENTS_LIST = [
    "Guitare", "Basse", "Batterie", "Piano", "Synthé", "Chant", "Saxophone", "Trompette", "Violon", "Flûte"
]

def charger_csv(fichier):
    if os.path.exists(fichier):
        return pd.read_csv(fichier)
    else:
        return pd.DataFrame(columns=["Nom", "Instrument(s)"])

def sauvegarder_csv(df, fichier):
    df.to_csv(fichier, index=False)

class RepetPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Planificateur de Répétitions pour Larsen")
        self.root.geometry("800x600")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.init_musiciens_tab()
        # Les autres onglets peuvent être ajoutés ici

        self.charger_donnees()

    def init_musiciens_tab(self):
        self.tab_musiciens = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_musiciens, text="Musiciens")

        self.tree_musiciens = ttk.Treeview(
            self.tab_musiciens,
            columns=("Nom", "Instrument(s)"),
            show="headings"
        )
        self.tree_musiciens.heading("Nom", text="Nom")
        self.tree_musiciens.heading("Instrument(s)", text="Instrument(s)")
        self.tree_musiciens.pack(fill='both', expand=True, pady=10)

        form_frame = ttk.Frame(self.tab_musiciens)
        form_frame.pack(pady=5)

        ttk.Label(form_frame, text="Nom :").grid(row=0, column=0)
        self.entry_nom = ttk.Entry(form_frame)
        self.entry_nom.grid(row=0, column=1)

        ttk.Label(form_frame, text="Instrument(s) :").grid(row=0, column=2)
        # Combobox pour choisir un instrument
        self.combo_instruments = Combobox(form_frame, values=INSTRUMENTS_LIST)
        self.combo_instruments.grid(row=0, column=3)
        self.combo_instruments.set('')

        # Bouton pour ajouter un instrument à la liste
        btn_ajouter_instr = ttk.Button(form_frame, text="+", width=2, command=self.ajouter_instrument_temp)
        btn_ajouter_instr.grid(row=0, column=4, padx=2)

        # Affichage des instruments sélectionnés
        self.label_instr_selection = ttk.Label(form_frame, text="Aucun instrument sélectionné")
        self.label_instr_selection.grid(row=1, column=0, columnspan=5, pady=2)

        # Liste temporaire pour les instruments sélectionnés
        self.instruments_temp = []

        btn_ajouter = ttk.Button(form_frame, text="Ajouter le musicien", command=self.ajouter_musicien)
        btn_ajouter.grid(row=2, column=0, columnspan=5, pady=5)

    def ajouter_instrument_temp(self):
        instr = self.combo_instruments.get().strip()
        if instr and instr not in self.instruments_temp:
            self.instruments_temp.append(instr)
            self.label_instr_selection.config(text=", ".join(self.instruments_temp))
        self.combo_instruments.set('')

    def ajouter_musicien(self):
        nom = self.entry_nom.get().strip()
        instruments = [i.strip() for i in self.instruments_temp if i.strip()]
        if not nom or not instruments:
            messagebox.showwarning("Champs manquants", "Merci de renseigner le nom et au moins un instrument.")
            return
        # Ajout dans le DataFrame
        new_row = pd.DataFrame([[nom, ",".join(instruments)]], columns=["Nom", "Instrument(s)"])
        self.df_musiciens = pd.concat([self.df_musiciens, new_row], ignore_index=True)
        sauvegarder_csv(self.df_musiciens, MUSICIENS_FILE)
        self.rafraichir_treeview(self.tree_musiciens, self.df_musiciens)
        self.entry_nom.delete(0, tk.END)
        self.instruments_temp = []
        self.label_instr_selection.config(text="Aucun instrument sélectionné")

    def charger_donnees(self):
        self.df_musiciens = charger_csv(MUSICIENS_FILE)
        self.rafraichir_treeview(self.tree_musiciens, self.df_musiciens)

    def rafraichir_treeview(self, tree, df):
        for row in tree.get_children():
            tree.delete(row)
        if not df.empty:
            for _, row in df.iterrows():
                tree.insert('', tk.END, values=(row["Nom"], row["Instrument(s)"]))

if __name__ == '__main__':
    root = tk.Tk()
    app = RepetPlannerApp(root)
    root.mainloop()