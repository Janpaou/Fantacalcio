import tkinter as tk
from tkinter import ttk
import pandas as pd
import os

FILE_EXCEL = "impostazioni_asta.xlsx"

def carica_file():
    if not os.path.exists(FILE_EXCEL):
        df_vuoto = pd.DataFrame(columns=["Nome"])
        with pd.ExcelWriter(FILE_EXCEL) as writer:
            df_vuoto.to_excel(writer, sheet_name="Partecipanti", index=False)
        return [], {}

    partecipanti = []
    squadre = {}
    try:
        xls = pd.ExcelFile(FILE_EXCEL)
        if "Partecipanti" in xls.sheet_names:
            df_partecipanti = pd.read_excel(xls, sheet_name="Partecipanti")
            partecipanti = df_partecipanti["Nome"].dropna().tolist()
            for nome in partecipanti:
                if nome in xls.sheet_names:
                    df_squadra = pd.read_excel(xls, sheet_name=nome)
                    squadre[nome] = df_squadra.to_dict("records")
                else:
                    squadre[nome] = []
    except Exception as e:
        print("Errore nel caricamento del file:", e)
    return partecipanti, squadre


def salva_squadre(squadre):
    try:
        with pd.ExcelWriter(FILE_EXCEL, mode="a", if_sheet_exists="replace") as writer:
            for nome, giocatori in squadre.items():
                df = pd.DataFrame(giocatori)
                df.to_excel(writer, sheet_name=nome, index=False)
    except Exception as e:
        print("Errore nel salvataggio delle squadre:", e)


def avvia_tool(callback_torna_indietro, centra_finestra, all_players):
    popup_impostazioni = None 
    root = tk.Tk()
    root.title("Tool Asta")
    centra_finestra(root, 1400, 1000)

    numero_partecipanti_var = tk.IntVar(value=0)
    budget_var = tk.StringVar(value="1000")

    partecipanti = []
    squadre = {}

    partecipante_selezionato = tk.StringVar()
    ricerca_var = tk.StringVar()

    def salva_file():
        partecipanti_df = pd.DataFrame([p["var_nome"].get() for p in partecipanti], columns=["Nome"])
        partecipanti_df.to_excel(FILE_EXCEL, sheet_name="Partecipanti", index=False)

        with pd.ExcelWriter(FILE_EXCEL, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
            for nome, squadra in squadre.items():
                df_squadra = pd.DataFrame(squadra)
                if not df_squadra.empty:
                    df_squadra.to_excel(writer, sheet_name=nome, index=False)


    def aggiorna_tabella_squadra():
        for item in tree_squadra.get_children():
            tree_squadra.delete(item)
        p = partecipante_selezionato.get()
        if p in squadre:
            for giocatore in squadre[p]:
                tree_squadra.insert("", "end", values=(giocatore["Nome"], giocatore["R"], giocatore["Squadra"], giocatore["Crediti"]))
                # Calcolo crediti residui
        totale_speso = sum(g.get("Crediti", 0) for g in squadre[p])
        try:
            budget = int(budget_var.get())
        except ValueError:
            budget = 1000  # default di sicurezza
        residui = budget - totale_speso
        label_crediti_residui.config(text=f"Crediti residui: {residui}")
                # Somma dei crediti per ruolo
        crediti_ruolo = {"P": 0, "D": 0, "C": 0, "A": 0}
        for g in squadre[p]:
            ruolo = g.get("R", "")
            crediti = g.get("Crediti", 0)
            if ruolo in crediti_ruolo:
                crediti_ruolo[ruolo] += crediti
                
        for ruolo, label in zip(["P", "D", "C", "A"], [label_portieri, label_difensori, label_centrocampisti, label_attaccanti]):
            if budget > 0:
                percentuale = crediti_ruolo[ruolo] / 10
            else:
                percentuale = 0
            label.config(text=f"{ruolo}: {percentuale:.1f}%")



    def inserisci_giocatore():
        nome_cercato = ricerca_var.get().strip().lower()
        crediti = entry_crediti.get().strip()

        if not crediti.isdigit():
            tk.messagebox.showwarning("Attenzione", "Inserisci un numero valido nei crediti.")
            return

        crediti = int(crediti)
        entry_ricerca.delete(0,tk.END)
        entry_crediti.delete(0, tk.END)
        entry_ricerca.focus_set()

        if not nome_cercato:
            return
        df = all_players
        giocatore_trovato = None
        for _, row in df.iterrows():
            if row["Nome"].lower() == nome_cercato:
                giocatore_trovato = row
                break
        if giocatore_trovato is None:
            print(f"Giocatore '{ricerca_var.get()}' non trovato.")
            return
        partecipante = partecipante_selezionato.get()
        if not partecipante:
            print("Seleziona un partecipante prima di inserire un giocatore.")
            return
        if partecipante not in squadre:
            squadre[partecipante] = []

        nomi_in_squadra = [g["Nome"] for g in squadre[partecipante]]
        if giocatore_trovato["Nome"] in nomi_in_squadra:
            print(f"Giocatore '{giocatore_trovato['Nome']}' già presente nella squadra di {partecipante}")
            return

        gioc_dict = {
            "Nome": giocatore_trovato["Nome"],
            "R": giocatore_trovato["R"],
            "Squadra": giocatore_trovato["Squadra"],
            "Crediti": crediti
        }
        squadre[partecipante].append(gioc_dict)
        aggiorna_tabella_squadra()
        salva_file()
        print(f"Inserito {giocatore_trovato['Nome']} per {partecipante}")

    def rimuovi_giocatore():
        p = partecipante_selezionato.get()
        if not p or p not in squadre:
            return
        selected = tree_squadra.selection()
        if not selected:
            return
        giocatore_nome = tree_squadra.item(selected[0])["values"][0]
        squadre[p] = [g for g in squadre[p] if g["Nome"] != giocatore_nome]
        aggiorna_tabella_squadra()
        salva_file()
        print(f"Rimosso {giocatore_nome} da {p}")

    def aggiorna_partecipanti():
        for widget in frame_partecipanti.winfo_children():
            widget.destroy()
        nuovi_partecipanti = []
        for i in range(numero_partecipanti_var.get()):
            var_nome = tk.StringVar()
            nome_default = f"Partecipante {i+1}"
            var_nome.set(nome_default)

            frame = tk.Frame(frame_partecipanti)
            frame.pack(side="left", padx=5)
            entry = tk.Entry(frame, textvariable=var_nome, width=15)
            entry.pack()

            btn = tk.Button(frame, text="👀", command=lambda v=var_nome: mostra_squadra(v.get()))
            btn.pack()

            nuovi_partecipanti.append({"nome": nome_default, "var_nome": var_nome})

        nonlocal partecipanti
        partecipanti = nuovi_partecipanti

        for p in partecipanti:
            n = p["var_nome"].get()
            if n not in squadre:
                squadre[n] = []

        aggiorna_dropdown()

    def mostra_squadra(nome):
        partecipante_selezionato.set(nome)
        aggiorna_tabella_squadra()

    def aggiorna_dropdown():
        nomi = [p["var_nome"].get() for p in partecipanti]
        partecipanti_dropdown["values"] = nomi
        if nomi:
            partecipante_selezionato.set(nomi[0])
            aggiorna_tabella_squadra()

    def on_partecipante_cambiato(event):
        aggiorna_tabella_squadra()

    def salva_impostazioni():
        try:
            n_partecipanti = int(entry_num_partecipanti.get())
            numero_partecipanti_var.set(n_partecipanti)
            aggiorna_partecipanti()
            popup_impostazioni.destroy()
            salva_file()
        except Exception as e:
            print("Errore nel salvare le impostazioni:", e)

    def apri_impostazioni():
        nonlocal popup_impostazioni
        popup_impostazioni = tk.Toplevel(root)
        popup_impostazioni.title("Impostazioni")
        centra_finestra(popup_impostazioni, 300, 200)

        tk.Label(popup_impostazioni, text="Numero partecipanti:").pack(pady=5)
        global entry_num_partecipanti
        entry_num_partecipanti = tk.Entry(popup_impostazioni)
        entry_num_partecipanti.insert(0, str(numero_partecipanti_var.get()))
        entry_num_partecipanti.pack(pady=5)

        tk.Label(popup_impostazioni, text="Crediti disponibili:").pack(pady=5)
        menu_budget = ttk.Combobox(popup_impostazioni, textvariable=budget_var, values=["300", "500", "1000"], state="readonly")
        menu_budget.pack(pady=5)

        tk.Button(popup_impostazioni, text="Salva", command=salva_impostazioni).pack(pady=10)

    # Layout
    top_frame = tk.Frame(root)
    top_frame.pack(fill="x", padx=10, pady=10)

    btn_settings = tk.Button(top_frame, text="⚙️", command=apri_impostazioni)
    btn_settings.pack(side="right")

    tk.Label(top_frame, text="Giocatore:").pack(side="left")
    entry_ricerca = tk.Entry(top_frame, textvariable=ricerca_var)
    entry_ricerca.pack(side="left", padx=5)
    entry_ricerca.focus_set()

    entry_crediti = tk.Entry(top_frame)
    entry_crediti.pack(side="left", padx=5)
    entry_crediti.bind("<Return>", lambda event: inserisci_giocatore())

    partecipanti_dropdown = ttk.Combobox(top_frame, textvariable=partecipante_selezionato, state="readonly")
    partecipanti_dropdown.pack(side="left", padx=5)
    partecipanti_dropdown.bind("<<ComboboxSelected>>", on_partecipante_cambiato)

    btn_inserisci = tk.Button(top_frame, text="Inserisci", command=inserisci_giocatore)
    btn_inserisci.pack(side="left", padx=5)

    btn_rimuovi = tk.Button(top_frame, text="Rimuovi giocatore selezionato", command=rimuovi_giocatore)
    btn_rimuovi.pack(side="left", padx=5)

    

    frame_partecipanti = tk.Frame(root)
    frame_partecipanti.pack(fill="x", padx=10, pady=10)

    frame_tabella = tk.Frame(root)
    frame_tabella.pack(fill="both", expand=True, padx=10, pady=10)

    tree_squadra = ttk.Treeview(frame_tabella, columns=("Nome", "Ruolo", "Squadra", "Crediti"), show="headings")
    for col in ("Nome", "Ruolo", "Squadra", "Crediti"):
        tree_squadra.heading(col, text=col)
        tree_squadra.column(col, width=150, anchor="center")
    tree_squadra.pack(fill="both", expand=True)

    label_portieri = tk.Label(root, text="P: ", font=("Arial", 12, "bold"))
    label_portieri.pack(side="left", pady=5, padx=20)

    label_difensori = tk.Label(root, text="D: ", font=("Arial", 12, "bold"))
    label_difensori.pack(side="left", pady=5, padx=20)

    label_centrocampisti = tk.Label(root, text="C: ", font=("Arial", 12, "bold"))
    label_centrocampisti.pack(side="left", pady=5, padx=20)

    label_attaccanti = tk.Label(root, text="A: ", font=("Arial", 12, "bold"))
    label_attaccanti.pack(side="left", pady=5, padx=20)

    label_crediti_residui = tk.Label(root, text="Crediti residui: -", font=("Arial", 12, "bold"))
    label_crediti_residui.pack(side="left", pady=5, padx=100)


    btn_torna_menu = tk.Button(root, text="⬅️ Torna al Menu", command=lambda: [salva_file(), root.destroy(), callback_torna_indietro()])
    btn_torna_menu.pack(pady=20)

    # Avvio iniziale
    carica_file()
    # Imposta iniziale partecipanti
    partecipanti_nomi, squadre = carica_file()

    partecipanti = []
    for nome in partecipanti_nomi:
        var_nome = tk.StringVar(value=nome)
        partecipanti.append({"nome": nome, "var_nome": var_nome})

    numero_partecipanti_var.set(len(partecipanti))

    aggiorna_dropdown()
    aggiorna_tabella_squadra()

    # Visualizza i nomi dei partecipanti nei campi di input e nei pulsanti 👀
    for p in partecipanti:
        frame = tk.Frame(frame_partecipanti)
        frame.pack(side="left", padx=5)
        entry = tk.Entry(frame, textvariable=p["var_nome"], width=15)
        entry.pack()
        btn = tk.Button(frame, text="👀", command=lambda v=p["var_nome"]: mostra_squadra(v.get()))
        btn.pack()



    root.mainloop()
