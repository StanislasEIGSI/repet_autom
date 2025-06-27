import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

# Fichiers de données
MUSICIENS_FILE = "musiciens.csv"
MUSIQUES_FILE = "musiques.csv"
DISPOS_FILE = "dispos.csv"
PLANNING_FILE = "planning.xlsx"

# Liste d'instruments
INSTRUMENTS_LIST = [
    "Guitare", "Basse", "Batterie", "Clavier", "Chant", "Saxophone", "Trompette", "Violon", "Flûte"
]

# ------------------ Fonctions utilitaires ------------------
def charger_csv(fichier):
    if os.path.exists(fichier):
        return pd.read_csv(fichier)
    else:
        return pd.DataFrame()

def sauvegarder_csv(df, fichier):
    df.to_csv(fichier, index=False)

# ------------------ Application principale ------------------
class RepetPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Planificateur de Répétitions pour Larsen")
        self.root.geometry("800x600")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.init_musiciens_tab()
        self.init_musiques_tab()
        self.init_dispos_tab()
        self.init_planning_tab()

        self.charger_donnees()

    def init_musiciens_tab(self):
        self.tab_musiciens = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_musiciens, text="Musiciens")

        # Treeview pour afficher les musiciens
        self.tree_musiciens = ttk.Treeview(self.tab_musiciens, columns=("Nom", "Instruments"), show="headings")
        self.tree_musiciens.heading("Nom", text="Nom")
        self.tree_musiciens.heading("Instruments", text="Instruments")
        self.tree_musiciens.pack(fill='both', expand=True, pady=10)

        # Champs pour ajout
        form_frame = ttk.Frame(self.tab_musiciens)
        form_frame.pack(pady=5)

        ttk.Label(form_frame, text="Nom :").grid(row=0, column=0)
        self.entry_nom = ttk.Entry(form_frame)
        self.entry_nom.grid(row=0, column=1)

        ttk.Label(form_frame, text="Instruments :").grid(row=0, column=2)
        self.entry_instruments = ttk.Entry(form_frame)
        self.entry_instruments.grid(row=0, column=3)

        btn_ajouter = ttk.Button(form_frame, text="Ajouter", command=self.ajouter_musicien)
        btn_ajouter.grid(row=0, column=4, padx=10)

    def ajouter_musicien(self):
        nom = self.entry_nom.get().strip()
        instruments = self.entry_instruments.get().strip()
        
        if nom and instruments:
            # Ajouter au DataFrame
            self.df_musiciens = pd.concat([
                self.df_musiciens,
                pd.DataFrame([[nom, instruments]], columns=["Nom", "Instruments"])
            ], ignore_index=True)
            # Mettre à jour l'affichage et sauvegarder
            self.rafraichir_treeview(self.tree_musiciens, self.df_musiciens)
            sauvegarder_csv(self.df_musiciens, MUSICIENS_FILE)
            self.entry_nom.delete(0, tk.END)
            self.entry_instruments.delete(0, tk.END)
        else:
            messagebox.showwarning("Champs manquants", "T'es con ou quoi? Il manque des champs à remplir...")

    def init_musiques_tab(self):
        self.tab_musiques = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_musiques, text="Musiques")

        self.tree_musiques = ttk.Treeview(self.tab_musiques, columns=("Titre", "Instruments", "Affectations"), show="headings")
        self.tree_musiques.heading("Titre", text="Titre")
        self.tree_musiques.heading("Instruments", text="Instruments requis")
        self.tree_musiques.heading("Affectations", text="Musiciens affectés")
        self.tree_musiques.pack(fill='both', expand=True)

    def init_dispos_tab(self):
        self.tab_dispos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dispos, text="Disponibilités")

        label = ttk.Label(self.tab_dispos, text="Importer les disponibilités au format CSV")
        label.pack(pady=10)

        btn_import = ttk.Button(self.tab_dispos, text="Importer disponibilités", command=self.importer_dispos)
        btn_import.pack()

    def init_planning_tab(self):
        self.tab_planning = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_planning, text="Planning")

        self.tree_planning = ttk.Treeview(self.tab_planning, columns=("Morceau", "Jour", "Heure", "Musiciens"), show="headings")
        self.tree_planning.heading("Morceau", text="Morceau")
        self.tree_planning.heading("Jour", text="Jour")
        self.tree_planning.heading("Heure", text="Heure")
        self.tree_planning.heading("Musiciens", text="Musiciens")
        self.tree_planning.pack(fill='both', expand=True)

        btn_generer = ttk.Button(self.tab_planning, text="Générer planning (exemple)", command=self.generer_planning)
        btn_generer.pack(pady=10)

        btn_export = ttk.Button(self.tab_planning, text="Exporter planning vers Excel", command=self.exporter_planning)
        btn_export.pack()

    def charger_donnees(self):
        self.df_musiciens = charger_csv(MUSICIENS_FILE)
        self.df_musiques = charger_csv(MUSIQUES_FILE)
        self.df_dispos = charger_csv(DISPOS_FILE)

        self.rafraichir_treeview(self.tree_musiciens, self.df_musiciens)
        self.rafraichir_treeview(self.tree_musiques, self.df_musiques)

    def rafraichir_treeview(self, tree, df):
        tree.delete(*tree.get_children())
        for _, row in df.iterrows():
            tree.insert('', 'end', values=tuple(row))

    def importer_dispos(self):
        filepath = filedialog.askopenfilename(title="Choisir un fichier CSV")
        if filepath:
            try:
                self.df_dispos = pd.read_csv(filepath)
                sauvegarder_csv(self.df_dispos, DISPOS_FILE)
                messagebox.showinfo("Succès", "Disponibilités importées.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de lire le fichier : {e}")

    def generer_planning(self):
        # Planning fictif pour démonstration
        planning_exemple = pd.DataFrame([
            ["Seven Nation Army", "Jeudi", "18h-19h", "Clément, Lisa, Ambre"],
            ["Feeling Good", "Vendredi", "17h-18h", "Melissande, Lilian, Théo"]
        ], columns=["Morceau", "Jour", "Heure", "Musiciens"])

        self.df_planning = planning_exemple
        self.rafraichir_treeview(self.tree_planning, self.df_planning)

    def exporter_planning(self):
        if hasattr(self, 'df_planning'):
            self.df_planning.to_excel(PLANNING_FILE, index=False)
            messagebox.showinfo("Export", f"Planning exporté dans {PLANNING_FILE}")
        else:
            messagebox.showwarning("Attention", "Aucun planning à exporter.")

# ------------------ Lancer l'application ------------------
if __name__ == '__main__':
    root = tk.Tk()
    app = RepetPlannerApp(root)
    root.mainloop()
