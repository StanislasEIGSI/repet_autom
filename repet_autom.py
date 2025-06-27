import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.ttk import Combobox

# Fichiers de données
MUSICIENS_FILE = "musiciens.csv"
DISPOS_FILE = "dispos.csv"
MUSIQUES_FILE = "musiques.csv"

INSTRUMENTS_LIST = [
    "Guitare", "Basse", "Batterie", "Piano", "Synthé", "Chant", "Saxophone", "Trompette", "Violon", "Flûte"
]

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]


def charger_csv(fichier, colonnes=None):
    if os.path.exists(fichier):
        return pd.read_csv(fichier)
    else:
        return pd.DataFrame(columns=colonnes if colonnes else [])


def sauvegarder_csv(df, fichier):
    df.to_csv(fichier, index=False)


class RepetPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Planificateur de Répétitions pour Larsen")
        self.root.geometry("1000x600")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.init_musiciens_tab()
        self.init_dispos_tab()
        self.init_musiques_tab()

        self.charger_donnees()

    # --- Onglet Musiciens ---
    def init_musiciens_tab(self):
        self.tab_musiciens = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_musiciens, text="Musiciens")

        self.tree_musiciens = ttk.Treeview(
            self.tab_musiciens,
            columns=("Nom", "Instruments"),
            show="headings"
        )
        self.tree_musiciens.heading("Nom", text="Nom")
        self.tree_musiciens.heading("Instruments", text="Instruments")
        self.tree_musiciens.pack(fill='both', expand=True, pady=10)

        form_frame = ttk.Frame(self.tab_musiciens)
        form_frame.pack(pady=5)

        ttk.Label(form_frame, text="Nom :").grid(row=0, column=0)
        self.entry_nom = ttk.Entry(form_frame)
        self.entry_nom.grid(row=0, column=1)

        ttk.Label(form_frame, text="Instruments :").grid(row=0, column=2)
        self.combo_instruments = Combobox(form_frame, values=INSTRUMENTS_LIST)
        self.combo_instruments.grid(row=0, column=3)
        self.combo_instruments.set('')

        btn_ajouter_instr = ttk.Button(form_frame, text="+", width=2, command=self.ajouter_instrument_temp)
        btn_ajouter_instr.grid(row=0, column=4, padx=2)

        self.label_instr_selection = ttk.Label(form_frame, text="Aucun instrument sélectionné")
        self.label_instr_selection.grid(row=1, column=0, columnspan=5, pady=2)

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
        new_row = pd.DataFrame([[nom, ",".join(instruments)]], columns=["Nom", "Instruments"])
        self.df_musiciens = pd.concat([self.df_musiciens, new_row], ignore_index=True)
        sauvegarder_csv(self.df_musiciens, MUSICIENS_FILE)
        self.rafraichir_treeview(self.tree_musiciens, self.df_musiciens)
        self.entry_nom.delete(0, tk.END)
        self.instruments_temp = []
        self.label_instr_selection.config(text="Aucun instrument sélectionné")

    # --- Onglet Dispos ---
    def init_dispos_tab(self):
        self.tab_dispos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dispos, text="Dispos")

        columns = ["Nom"] + JOURS
        self.tree_dispos = ttk.Treeview(
            self.tab_dispos,
            columns=columns,
            show="headings",
            height=20
        )
        for col in columns:
            self.tree_dispos.heading(col, text=col)
            self.tree_dispos.column(col, width=120, anchor="center")
        self.tree_dispos.pack(fill='both', expand=True, pady=10)

        self.tree_dispos.bind("<Double-1>", self.on_double_click_dispo)

        btn_modif = ttk.Button(
            self.tab_dispos,
            text="Modifier la disponibilité sélectionnée",
            command=self.modifier_dispo_selection
        )
        btn_modif.pack(pady=5)

    def on_double_click_dispo(self, event):
        item_id = self.tree_dispos.identify_row(event.y)
        col = self.tree_dispos.identify_column(event.x)
        if not item_id or col == "#0":
            return
        col_index = int(col.replace("#", "")) - 1
        columns = ["Nom"] + JOURS
        if col_index == 0:
            return
        nom = self.tree_dispos.item(item_id, "values")[0]
        jour = columns[col_index]
        current_value = self.tree_dispos.item(item_id, "values")[col_index]
        new_value = simpledialog.askstring("Modifier disponibilité", f"Nouvelle disponibilité pour {nom} le {jour} :", initialvalue=current_value, parent=self.root)
        if new_value is not None:
            self.df_dispos.loc[self.df_dispos["Nom"] == nom, jour] = new_value
            sauvegarder_csv(self.df_dispos, DISPOS_FILE)
            self.rafraichir_treeview_dispos()

    def modifier_dispo_selection(self):
        selected = self.tree_dispos.selection()
        if not selected:
            messagebox.showinfo("Sélection", "Sélectionne une ligne à modifier.")
            return
        item = selected[0]
        values = self.tree_dispos.item(item, "values")
        nom = values[0]
        jour = simpledialog.askstring("Jour", f"Quel jour modifier ? ({', '.join(JOURS)})")
        if jour not in JOURS:
            messagebox.showerror("Erreur", "Jour invalide.")
            return
        current_value = self.df_dispos.loc[self.df_dispos["Nom"] == nom, jour].values[0]
        new_value = simpledialog.askstring("Modifier disponibilité", f"Nouvelle disponibilité pour {nom} le {jour} :", initialvalue=current_value, parent=self.root)
        if new_value is not None:
            self.df_dispos.loc[self.df_dispos["Nom"] == nom, jour] = new_value
            sauvegarder_csv(self.df_dispos, DISPOS_FILE)
            self.rafraichir_treeview_dispos()


    # --- Onglet Morceaux ---
    def init_musiques_tab(self):
        self.tab_musiques = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_musiques, text="Morceaux")

        self.postes = ["Titre", "Guitare 1", "Guitare 2", "Basse", "Batterie", "Clavier", "Chant 1", "Chant 2", "Chant 3"]
        self.tree_musiques = ttk.Treeview(self.tab_musiques, columns=self.postes, show="headings")

        for col in self.postes:
            self.tree_musiques.heading(col, text=col)
            self.tree_musiques.column(col, width=100)

        self.tree_musiques.pack(fill='both', expand=True, pady=10)
        self.tree_musiques.bind('<Double-1>', self.editer_cellule)

        form_frame = ttk.Frame(self.tab_musiques)
        form_frame.pack(pady=5)

        ttk.Label(form_frame, text="Titre du morceau :").grid(row=0, column=0)
        self.entry_titre_morceau = ttk.Entry(form_frame)
        self.entry_titre_morceau.grid(row=0, column=1)

        btn_ajouter_morceau = ttk.Button(form_frame, text="Ajouter morceau", command=self.ajouter_morceau)
        btn_ajouter_morceau.grid(row=0, column=2, padx=10)

    def ajouter_morceau(self):
        titre = self.entry_titre_morceau.get().strip()
        if titre:
            ligne = {poste: "" for poste in self.postes}
            ligne["Titre"] = titre
            self.df_musiques = pd.concat([self.df_musiques, pd.DataFrame([ligne])], ignore_index=True)
            self.rafraichir_treeview(self.tree_musiques, self.df_musiques)
            sauvegarder_csv(self.df_musiques, MUSIQUES_FILE)
            self.entry_titre_morceau.delete(0, tk.END)
        else:
            messagebox.showwarning("Champs manquant", "Veuillez entrer un titre de morceau.")

    def editer_cellule(self, event):
        item_id = self.tree_musiques.identify_row(event.y)
        column_id = self.tree_musiques.identify_column(event.x)

        if not item_id or column_id == '#0':
            return

        col_index = int(column_id.replace('#', '')) - 1
        colonne = self.postes[col_index]
        item = self.tree_musiques.item(item_id)
        ancien_valeur = item['values'][col_index]

        entry_popup = tk.Entry(self.tree_musiques)
        entry_popup.insert(0, ancien_valeur)
        entry_popup.focus()

        bbox = self.tree_musiques.bbox(item_id, column_id)
        if not bbox:
            return

        entry_popup.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])

        def valider(event=None):
            nouvelle_valeur = entry_popup.get()
            self.df_musiques.at[self.tree_musiques.index(item_id), colonne] = nouvelle_valeur
            self.rafraichir_treeview(self.tree_musiques, self.df_musiques)
            sauvegarder_csv(self.df_musiques, MUSIQUES_FILE)
            entry_popup.destroy()

        entry_popup.bind('<Return>', valider)
        entry_popup.bind('<FocusOut>', lambda e: entry_popup.destroy())

    # --- Chargement et affichage des données ---
    def charger_donnees(self):
        self.df_musiciens = charger_csv(MUSICIENS_FILE, ["Nom", "Instruments"])
        self.rafraichir_treeview(self.tree_musiciens, self.df_musiciens)

        self.df_dispos = charger_csv(DISPOS_FILE, ["Nom"] + JOURS)
        self.rafraichir_treeview_dispos()

        self.df_musiques = charger_csv(MUSIQUES_FILE, self.postes)
        self.rafraichir_treeview(self.tree_musiques, self.df_musiques)

    def rafraichir_treeview(self, tree, df):
        tree.delete(*tree.get_children())
        for _, row in df.iterrows():
            tree.insert('', 'end', values=tuple(row.get(col, "") for col in tree["columns"]))

    def rafraichir_treeview_dispos(self):
        for row in self.tree_dispos.get_children():
            self.tree_dispos.delete(row)
        if not self.df_dispos.empty:
            for _, row in self.df_dispos.iterrows():
                values = [row["Nom"]] + [row[jour] if pd.notna(row[jour]) else "" for jour in JOURS]
                self.tree_dispos.insert('', tk.END, values=values)


if __name__ == '__main__':
    root = tk.Tk()
    app = RepetPlannerApp(root)
    root.mainloop()
