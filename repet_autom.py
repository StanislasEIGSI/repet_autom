import pandas as pd
from collections import defaultdict

# Fonction pour convertir un créneau "17h-19h" en tuple (17,19)
def parse_time_slot(slot):
    try:
        start, end = slot.split('-')
        start_h = int(start.replace('h','').strip())
        end_h = int(end.replace('h','').strip())
        return (start_h, end_h)
    except:
        return None

# Fonction pour vérifier si deux créneaux se chevauchent
def slots_overlap(slot1, slot2):
    s1, e1 = slot1
    s2, e2 = slot2
    return not (e1 <= s2 or e2 <= s1)

# Lecture du fichier Excel
file_path = 'ton_fichier.xlsx'  # adapte ici
musiciens_df = pd.read_excel(file_path, sheet_name='Musiciens')
dispos_df = pd.read_excel(file_path, sheet_name='Dispos')
musiques_df = pd.read_excel(file_path, sheet_name='Musiques')

# Préparation : dictionnaire musicien -> {jour: [créneaux]}
dispo_dict = defaultdict(lambda: defaultdict(list))

jours = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi']

for _, row in dispos_df.iterrows():
    nom = row[0]
    for jour in jours:
        cell = row[jour]
        if pd.isna(cell):
            continue
        slots = str(cell).split(',')
        for slot in slots:
            ts = parse_time_slot(slot.strip())
            if ts:
                dispo_dict[nom][jour].append(ts)

# Exemple : fonction pour récupérer musiciens sur un morceau
def musiciens_sur_morceau(morceau):
    row = musiques_df[musiques_df['Morceau']==morceau]
    if row.empty:
        print("Morceau inconnu")
        return []
    # Récupérer les noms dans les colonnes sauf la première (Morceau)
    musiciens = []
    for col in musiques_df.columns[1:]:
        val = row.iloc[0][col]
        if pd.notna(val) and val != '':
            musiciens.append(val)
    return musiciens

# Trouver créneaux communs entre plusieurs musiciens
def trouver_creneaux_communs(musiciens):
    # pour chaque jour, on va chercher les plages communes
    communs = defaultdict(list)  # jour -> liste de créneaux
    
    for jour in jours:
        # récupérer les créneaux de chaque musicien pour ce jour
        listes = []
        for m in musiciens:
            creneaux = dispo_dict[m][jour]
            if not creneaux:
                break
            listes.append(creneaux)
        else:
            # on a les créneaux pour tous, il faut trouver les overlaps
            # on va prendre l'intersection horaire des créneaux entre tous
            # méthode simplifiée : pour chaque créneau du premier, on cherche les overlaps dans les autres
            for slot in listes[0]:
                start, end = slot
                overlap_start = start
                overlap_end = end
                for other_list in listes[1:]:
                    # chercher s'il existe un slot qui chevauche
                    chev = [s for s in other_list if slots_overlap(s, (overlap_start, overlap_end))]
                    if not chev:
                        overlap_start = None
                        break
                    else:
                        # réduire la fenêtre d'intersection au chevauchement maximal
                        max_start = max(overlap_start, max(s[0] for s in chev))
                        min_end = min(overlap_end, min(s[1] for s in chev))
                        if max_start >= min_end:
                            overlap_start = None
                            break
                        else:
                            overlap_start = max_start
                            overlap_end = min_end
                if overlap_start is not None:
                    communs[jour].append((overlap_start, overlap_end))
    return communs

# Exemple d'utilisation
morceau_choisi = 'Clocks'
musiciens = musiciens_sur_morceau(morceau_choisi)
print(f"Musiciens sur '{morceau_choisi}' : {musiciens}")

creneaux = trouver_creneaux_communs(musiciens)

print(f"\nCréneaux communs possibles pour répéter '{morceau_choisi}':")
for jour, slots in creneaux.items():
    for start,end in slots:
        print(f"{jour} : {start}h-{end}h")
