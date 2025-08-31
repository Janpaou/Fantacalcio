import tkinter as tk
from tkinter import ttk
import pandas as pd
from toolAsta import avvia_tool
import os
from PIL import Image, ImageTk  

CACHE_FILE = "giocatori_elaborati.xlsx"

def prepara_cache():
    if os.path.exists(CACHE_FILE):
        print("🟢 Cache trovata, caricamento rapido.")
        df = pd.read_excel(CACHE_FILE, sheet_name=None)
        return (
            df["Portieri"],
            df["Difensori"],
            df["Centrocampisti"],
            df["Attaccanti"]
        )
    else:
        print("⚠️ Nessuna cache trovata, calcolo in corso...")

        portieri = get_giocatori("P")
        portieri = normalizza_valori(portieri, 1, 100)

        difensori = get_giocatori("D")
        difensori = normalizza_valori(difensori, 1, 90)

        centrocampisti = get_giocatori("C")
        centrocampisti = normalizza_valori(centrocampisti, 1, 160)

        attaccanti = get_giocatori("A")
        attaccanti = normalizza_valori(attaccanti, 1, 320)

        
        with pd.ExcelWriter(CACHE_FILE) as writer:
            portieri.to_excel(writer, sheet_name="Portieri", index=False)
            difensori.to_excel(writer, sheet_name="Difensori", index=False)
            centrocampisti.to_excel(writer, sheet_name="Centrocampisti", index=False)
            attaccanti.to_excel(writer, sheet_name="Attaccanti", index=False)

        print("✅ Cache generata con successo.")
        return portieri, difensori, centrocampisti, attaccanti


def centra_finestra(finestra, larghezza=800, altezza=600):
    finestra.update_idletasks()
    screen_width = finestra.winfo_screenwidth()
    screen_height = finestra.winfo_screenheight()
    x = (screen_width // 2) - (larghezza // 2)
    y = (screen_height // 2) - (altezza // 2)
    finestra.geometry(f"{larghezza}x{altezza}+{x}+{y}")


def calcola_valore_portiere(row):
    return round((
        row["Mv"] * row["Pv"]+
        row["Rp"] * 3 -
        row["Gs"] * 1 -
        row["Amm"] * 0.5 -
        row["Esp"] * 2 -
        row["Au"] * 3
    ) * get_quotazione(row["Id"]) /1000, 2)

def calcola_valore_mov(row):
    return round((
        row["Mv"] * row["Pv"]+
        (row["Gf"] - row["R-"])* 3 -
        row["Amm"] * 0.5 -
        row["Esp"] * 2 -
        row["Au"] * 3 +
        row["Ass"] * 1
    ) * get_quotazione(row["Id"]) /1000, 2)

def get_giocatori(per_ruolo):
    df_stat = pd.read_excel("Statistiche_Fantacalcio_Stagione_2024_25.XLSX", header=1)
    df_quot = pd.read_excel("Quotazioni_Fantacalcio_Stagione_2025_26.xlsx", header=1)
    df = pd.merge(df_quot, df_stat, on="Id", how="left", suffixes=("", "_old"))
    colonne_statistiche = ["Mv", "Pv", "Rp", "Gs", "Amm", "Esp", "Au", "Gf", "R-", "Ass", "Pc"]
    for col in colonne_statistiche:
        if col in df.columns:
            df[col] = df[col].fillna(-1)
    
    if per_ruolo:
        df = df[df["R"] == per_ruolo]

    
    if per_ruolo == "P":
        df["Valore"] = df.apply(calcola_valore_portiere, axis=1)
    else:
        df["Valore"] = df.apply(calcola_valore_mov, axis=1)

    return df

def get_quotazione(player_id):
    quotazioni = pd.read_excel("Quotazioni_Fantacalcio_Stagione_2025_26.xlsx", header=1)
    
    
    riga = quotazioni[quotazioni["Id"] == player_id]

    if not riga.empty:
        return riga.iloc[0]["FVM"]
    else:
        return 1
    
def normalizza_valori(df, minimo, massimo):
    min_val = df["Valore"].min()
    max_val = df["Valore"].max()
    df["Valore" + "_norm"] = round(((df["Valore"] - min_val) / (max_val - min_val)) * (massimo - minimo) + minimo, 2)
    return df

portieri, difensori, centrocampisti, attaccanti = prepara_cache()
#print(portieri[["Nome", "R", "Mv", "Rp", "Gs", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore_norm", ascending=False).head(20))
#print(difensori[["Nome", "R", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore", ascending=False).head(30))
#print(centrocampisti[["Nome", "R", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore", ascending=False).head(30))
#print(attaccanti[["Nome", "R", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore", ascending=False).head(30))    





def main_menu():
    def apri_ricerca():
        root.destroy()
        avvia_ricerca(main_menu)

    def apri_altro():
        root.destroy()
        avvia_tool(main_menu, centra_finestra, pd.concat([portieri, difensori, centrocampisti, attaccanti]))

    root = tk.Tk()
    root.title("Menu Fantacalcio")
    centra_finestra(root, 800, 600)

    tk.Label(root, text="Seleziona una funzione:", font=("Arial", 14)).pack(pady=20)

    tk.Button(root, text="🔍 Ricerca Giocatori", command=apri_ricerca, width=30).pack(pady=10)
    tk.Button(root, text="📊 Tool Asta", command=apri_altro, width=30).pack(pady=10)

    root.mainloop()

def avvia_ricerca(callback_torna_indietro):
    
    note_file = "impostazioni_asta.xlsx"
    if os.path.exists(note_file):
        xls = pd.ExcelFile(note_file)
        if "Note" in xls.sheet_names:
            df_note = pd.read_excel(xls, sheet_name="Note")
            if "Id" not in df_note.columns:
                df_note["Id"] = ""
            if "Nota" not in df_note.columns:
                df_note["Nota"] = ""
        else:
            df_note = pd.DataFrame(columns=["Id", "Nota"])
    else:
        df_note = pd.DataFrame(columns=["Id", "Nota"])

    root = tk.Tk()
    root.title("Ricerca Giocatori Fantacalcio")
    centra_finestra(root, 800, 600)

    
    search_entry = tk.Entry(root, width=50)
    search_entry.pack(pady=10)
    search_entry.bind("<Return>", lambda event: case(search_entry.get().lower()))
    search_entry.focus_set()
    

    checkbox_states = set()  

    tree = ttk.Treeview(root, columns=[], show="headings")
    tree.pack(fill="both", expand=True)

    def toggle_checkbox(event):
        if last_risultati is None:
            return
        col = tree.identify_column(event.x)
        if col != "#1":  
            return
        item = tree.identify_row(event.y)
        if not item:
            return
        idx = tree.index(item)
        if idx in checkbox_states:
            checkbox_states.remove(idx)
        else:
            checkbox_states.add(idx)
        mostra_risultati(last_risultati)

    tree.bind("<Button-1>", toggle_checkbox)

    last_risultati = None

    def apri_popup_nota(event=None):
        selected_item = tree.focus()
        if not selected_item:
            return
        idx = tree.index(selected_item)
        if last_risultati is None or idx >= len(last_risultati):
            return
        
        player_id = str(last_risultati.iloc[idx]["Id"])

        nota_precedente = df_note[df_note["Id"].astype(str) == player_id]["Nota"].values
        nota_testo = nota_precedente[0] if len(nota_precedente) > 0 else ""

        popup = tk.Toplevel(root)
        popup.title("Nota Giocatore")
        centra_finestra(popup, 400, 300)
        tk.Label(popup, text="Inserisci/modifica nota:").pack(pady=5)
        text_nota = tk.Text(popup, width=50, height=10)
        text_nota.insert("1.0", nota_testo)
        text_nota.pack(padx=10, pady=10)
        text_nota.focus_set()

        def salva_nota(event=None):
            nonlocal df_note
            nuovo_testo = text_nota.get("1.0", tk.END).strip()
            df_note = df_note[df_note["Id"].astype(str) != str(player_id)]
            nuova_riga = pd.DataFrame([{"Id": player_id, "Nota": nuovo_testo}])
            df_note = pd.concat([df_note, nuova_riga], ignore_index=True)
            salva_note(df_note, note_file)
            df_note = carica_note(note_file)
            popup.destroy()

        tk.Button(popup, text="💾 Salva", command=salva_nota).pack(pady=5)
        tk.Button(popup, text="Annulla", command=popup.destroy).pack()
        text_nota.bind("<Return>", salva_nota)

    tree.bind("<Return>", apri_popup_nota)


    tk.Button(root, text="Cerca", command=lambda: case(search_entry.get().lower())).pack()
    tk.Button(root, text="⬅️ Torna al Menu", command=lambda: [root.destroy(), callback_torna_indietro()]).pack(pady=20)

    def case(scelta):
    
        match scelta:
            case "p":
                pd.set_option("display.max_rows", None)
                mostra_risultati(portieri[["Id","Nome","Squadra", "R", "Pv", "Mv", "Rp", "Gs", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False))
            
            case "d":
                pd.set_option("display.max_rows", None)
                mostra_risultati(difensori[["Id","Nome","Squadra", "R","Pv", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False))
            
            case "c":
                pd.set_option("display.max_rows", None)
                mostra_risultati(centrocampisti[["Id","Nome","Squadra", "R","Pv", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False))

            case "a":
                pd.set_option("display.max_rows", None)
                mostra_risultati(attaccanti[["Id","Nome","Squadra", "R","Pv", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False))


            case _:
                all_players = pd.concat([portieri, difensori, centrocampisti, attaccanti])
                risultati = all_players[all_players["Squadra"].str.lower().str.contains(scelta, na=False)]

                if risultati.empty:
                    risultati = all_players[all_players["Nome"].str.lower().str.contains(scelta, na=False)]
                    mostra_risultati(risultati[["Id","Nome","Squadra", "R","Pv", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False))
                else:
                    mostra_risultati(risultati[["Id","Nome","Squadra", "R","Pv", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False))


    def mostra_risultati(risultati):
        nonlocal last_risultati
        last_risultati = risultati.copy()
        risultati = risultati.copy()
        risultati["Nota"] = risultati["Id"].apply(
            lambda id_: df_note[df_note["Id"] == id_]["Nota"].values[0] if not df_note[df_note["Id"] == id_].empty else ""
        )
        
        risultati = risultati[[col for col in risultati.columns if col != "Id"]]
        risultati.insert(0, "Seleziona", ["X" if i in checkbox_states else "" for i in range(len(risultati))])
        cols = list(risultati.columns)
        tree.delete(*tree.get_children())
        tree["columns"] = cols
        search_entry.delete(0, tk.END)
        for col in tree["columns"]:
            if col == "Seleziona":
                tree.heading(col, text=col)
                tree.column(col, width=40, anchor="center")
            else:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor="center")
        for _, row in risultati.iterrows():
            values = [row[col] for col in risultati.columns]
            tree.insert("", "end", values=values)
        tree.focus_set()

def carica_note(note_file="impostazioni_asta.xlsx"):
    if os.path.exists(note_file):
        xls = pd.ExcelFile(note_file)
        if "Note" in xls.sheet_names:
            df_note = pd.read_excel(xls, sheet_name="Note")
            if "Id" not in df_note.columns:
                df_note["Id"] = ""
            if "Nota" not in df_note.columns:
                df_note["Nota"] = ""
            return df_note
    
    return pd.DataFrame(columns=["Id", "Nota"])

def salva_note(df_note, note_file="impostazioni_asta.xlsx"):
    with pd.ExcelWriter(note_file, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
        df_note.to_excel(writer, sheet_name="Note", index=False)

if __name__ == "__main__":
    try:
        main_menu()
        
    except Exception as e:
        print("Errore:", e)
    input("\nPremi invio per chiudere...")
