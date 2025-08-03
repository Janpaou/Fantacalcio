import tkinter as tk
from tkinter import ttk
import pandas as pd
from toolAsta import avvia_tool
import os

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

        # Salva tutto in un Excel con più fogli
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
    # Filtra i ruoli ufficiali se specificato
    if per_ruolo:
        df = df[df["R"] == per_ruolo]

    # Calcola valore solo per portieri (R == "P")
    if per_ruolo == "P":
        df["Valore"] = df.apply(calcola_valore_portiere, axis=1)
    else:
        df["Valore"] = df.apply(calcola_valore_mov, axis=1)

    return df

def get_quotazione(player_id):
    quotazioni = pd.read_excel("Quotazioni_Fantacalcio_Stagione_2025_26.xlsx", header=1)
    
    # Filtra per ID
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
    root = tk.Tk()
    root.title("Ricerca Giocatori Fantacalcio")
    centra_finestra(root, 800, 600)

    # Entry per ricerca
    search_entry = tk.Entry(root, width=50)
    search_entry.pack(pady=10)
    search_entry.bind("<Return>", lambda event: case(search_entry.get().lower()))
    search_entry.focus_set()
    # Area risultati
    #text = tk.Text(root, wrap="none", width=100, height=25)
    #text.pack()

    tree = ttk.Treeview(root, columns=[], show="headings")
    tree.pack(fill="both", expand=True)

    tk.Button(root, text="Cerca", command=lambda: case(search_entry.get().lower())).pack()
    tk.Button(root, text="⬅️ Torna al Menu", command=lambda: [root.destroy(), callback_torna_indietro()]).pack(pady=20)

    def case(scelta):
    
        match scelta:
            case "p":
                pd.set_option("display.max_rows", None)
                mostra_risultati(portieri[["Nome","Squadra", "R", "Pv", "Mv", "Rp", "Gs", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False))
            
            case "d":
                pd.set_option("display.max_rows", None)
                mostra_risultati(difensori[["Nome","Squadra", "R","Pv", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False))
            
            case "c":
                pd.set_option("display.max_rows", None)
                mostra_risultati(centrocampisti[["Nome","Squadra", "R","Pv", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False))

            case "a":
                pd.set_option("display.max_rows", None)
                mostra_risultati(attaccanti[["Nome","Squadra", "R","Pv", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False))

            case "tutti":
                mostra_risultati("Portieri:")
                print(portieri[["Nome","Squadra", "R","Pv", "Mv", "Rp", "Gs", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False).head(20))
                print("\nDifensori:")
                mostra_risultati(difensori[["Nome","Squadra", "R", "Pv","Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore", ascending=False).head(30))
                print("\nCentrocampisti:")
                mostra_risultati(centrocampisti[["Nome","Squadra", "R","Pv", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore", ascending=False).head(30))
                print("\nAttaccanti:")
                mostra_risultati(attaccanti[["Nome","Squadra", "R","Pv", "Mv", "Gf", "Ass", "Amm", "Esp", "Au",  "Valore_norm", "Pc"]].sort_values("Valore", ascending=False).head(30))

            case _:
                all_players = pd.concat([portieri, difensori, centrocampisti, attaccanti])
                risultati = all_players[all_players["Squadra"].str.lower().str.contains(scelta, na=False)]

                if risultati.empty:
                    risultati = all_players[all_players["Nome"].str.lower().str.contains(scelta, na=False)]
                    mostra_risultati(risultati[["Nome","Squadra", "R","Pv", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False))
                else:
                    mostra_risultati(risultati[["Nome","Squadra", "R","Pv", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore_norm", "Pc"]].sort_values("Valore_norm", ascending=False))


    def mostra_risultati(risultati):
        tree.delete(*tree.get_children())
        tree["columns"] = list(risultati.columns)
        search_entry.delete(0, tk.END)
        if risultati.empty:
            tree.insert(tk.END, "Nessun risultato trovato.")
        else:
            for col in risultati.columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor="center")  # personalizza larghezza

    # Inserisci righe
            for _, row in risultati.iterrows():
                tree.insert("", "end", values=list(row))

if __name__ == "__main__":
    try:
        main_menu()
        
    except Exception as e:
        print("Errore:", e)
    input("\nPremi invio per chiudere...")
