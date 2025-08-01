import pandas as pd

def calcola_valore_portiere(row):
    return (
        row["Mv"] * row["Pv"]+
        row["Rp"] * 3 -
        row["Gs"] * 1 -
        row["Amm"] * 0.5 -
        row["Esp"] * 2 -
        row["Au"] * 3
    ) * get_quotazione(row["Id"]) /1000

def calcola_valore_mov(row):
    return (
        row["Mv"] * row["Pv"]+
        (row["Gf"] - row["R-"])* 3 -
        row["Amm"] * 0.5 -
        row["Esp"] * 2 -
        row["Au"] * 3 +
        row["Ass"] * 1
    ) * get_quotazione(row["Id"]) /1000

def get_giocatori(per_ruolo):
    df = pd.read_excel("Statistiche_Fantacalcio_Stagione_2024_25.XLSX", header=1)

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
    df["Valore" + "_norm"] = ((df["Valore"] - min_val) / (max_val - min_val)) * (massimo - minimo) + minimo
    return df


# Esegui e mostra
portieri = get_giocatori("P")
portieri = normalizza_valori(portieri, 1, 100)
difensori = get_giocatori("D")
difensori = normalizza_valori(difensori, 1, 110)
centrocampisti = get_giocatori("C")
centrocampisti = normalizza_valori(centrocampisti, 1, 130)
attaccanti = get_giocatori("A")
attaccanti = normalizza_valori(attaccanti, 1, 320)
#print(portieri[["Nome", "R", "Mv", "Rp", "Gs", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore_norm", ascending=False).head(20))
#print(difensori[["Nome", "R", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore", ascending=False).head(30))
#print(centrocampisti[["Nome", "R", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore", ascending=False).head(30))
#print(attaccanti[["Nome", "R", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore", ascending=False).head(30))


def menu():
    print("Cosa vuoi fare?")
    print("1. Cerca un giocatore per nome")
    print("2. Cerca giocatori per squadra")
    print("3. Visualizza giocatori per ruolo (P, D, C, A)")
    print("4. Visualizza tutti i ruoli")
    scelta = input("Inserisci la tua scelta (1, 2, 3): ")

    if scelta == "1":
        nome = input("Inserisci il nome del giocatore: ").strip().lower()
        all_players = pd.concat([portieri, difensori, centrocampisti, attaccanti])
        risultati = all_players[all_players["Nome"].str.lower().str.contains(nome)]

        if risultati.empty:
            print("Nessun giocatore trovato.")
            menu()
        else:
            print("")
            print(risultati[["Nome", "R", "Valore", "Valore_norm"]].sort_values("Valore_norm", ascending=False))
            print("")
            print("")
            menu()
    elif scelta == "2":
        sqaudra = input("Inserisci il nome della squadra: ").strip().lower()
        all_players = pd.concat([portieri, difensori, centrocampisti, attaccanti])
        risultati = all_players[all_players["Squadra"].str.lower().str.contains(sqaudra)]

        if risultati.empty:
            print("Nessun giocatore trovato.")
            menu()
        else:
            print("")
            print(risultati[["Nome", "R", "Valore", "Valore_norm"]].sort_values("Valore_norm", ascending=False))
            print("")
            print("")
            menu()

    elif scelta == "3":
        ruolo = input("Inserisci il ruolo (P, D, C, A): ").upper()
        pd.set_option("display.max_rows", None)

        if ruolo == "P":
            print(portieri[["Nome","Squadra", "R", "Mv", "Rp", "Gs", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore_norm", ascending=False))
            print("")
            print("")
            menu()
        elif ruolo == "D":
            print(difensori[["Nome","Squadra", "R", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore", ascending=False))
            print("")
            print("")
            menu()
        elif ruolo == "C":
            print(centrocampisti[["Nome","Squadra", "R", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore", ascending=False))
            print("")
            print("")
            menu()
        elif ruolo == "A":
            print(attaccanti[["Nome","Squadra", "R", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore", ascending=False))
            print("")
            print("")
            menu()
        else:
            print("Ruolo non valido. Usa solo P, D, C o A.")

    elif scelta == "4":
        print("Portieri:")
        print(portieri[["Nome","Squadra", "R", "Mv", "Rp", "Gs", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore_norm", ascending=False).head(20))
        print("\nDifensori:")
        print(difensori[["Nome","Squadra", "R", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore", ascending=False).head(30))
        print("\nCentrocampisti:")
        print(centrocampisti[["Nome","Squadra", "R", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore", ascending=False).head(30))
        print("\nAttaccanti:")
        print(attaccanti[["Nome","Squadra", "R", "Mv", "Gf", "Ass", "Amm", "Esp", "Au", "Valore", "Valore_norm"]].sort_values("Valore", ascending=False).head(30))
    else:
        print("Scelta non valida.")

# Avvia il menu
menu()
