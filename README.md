# 💼 Consulente di Investimento AI

Un agente intelligente basato su **LangGraph** e **GPT-4** che fornisce raccomandazioni di investimento personalizzate analizzando mercati finanziari in tempo reale.

## 🌟 Caratteristiche

- 🤖 **Agente AI Autonomo**: Utilizza LangGraph per orchestrare decisioni intelligenti
- 📊 **Analisi Multi-Mercato**: Analizza azioni, obbligazioni, settori e commodities
- 🎯 **Profili di Rischio Personalizzati**: Conservative, Moderate, Aggressive
- 📈 **Dashboard Interattiva**: Interfaccia Streamlit con visualizzazioni dettagliate
- 🔀 **Visualizzazione DAG**: Mostra l'architettura dell'agente
- 💡 **Raccomandazioni Giustificate**: Ogni suggerimento include rationale dettagliato

## 🏗️ Architettura

L'agente utilizza un grafo di stato (StateGraph) con i seguenti nodi:

```
START → agent → tools ⟲ → finalize → END
```

- **agent**: Nodo decisionale che sceglie quali strumenti utilizzare
- **tools**: Esegue chiamate ai tools (market data, quotazioni, analisi settori)
- **finalize**: Genera raccomandazioni finali con allocazione ottimale

## 📦 Installazione

### Prerequisiti
- Python 3.10+
- Account OpenAI con API key

### Setup

1. **Clona il repository**
```bash
git clone <your-repo-url>
cd PRJ-NEW-AGENT
```

2. **Crea ambiente virtuale**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

3. **Installa dipendenze**
```bash
pip install -r requirements.txt
```

4. **Configura variabili d'ambiente**

Crea un file `.env` nella root del progetto:
```env
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini
SSL_VERIFY=true
```

## 🚀 Utilizzo

### 1. Agente da Linea di Comando

```bash
# Con parametri di default (€10,000, moderate)
python investment_agent.py

# Con importo personalizzato
python investment_agent.py 5000

# Con importo e profilo di rischio
python investment_agent.py 15000 aggressive
python investment_agent.py 8000 conservative
```

### 2. Dashboard Streamlit

```bash
streamlit run dashboard.py
```

Apri il browser su `http://localhost:8501`

**Funzionalità Dashboard:**
- Input interattivo per importo e profilo rischio
- Panoramica mercato (S&P 500, NASDAQ, VIX, Sentiment)
- Allocazione portafoglio con grafici
- Raccomandazioni specifiche per titolo
- Report completo con giustificazioni
- Visualizzazione DAG dell'agente

### 3. Visualizzazione DAG

```bash
python visualize_investment_dag.py
```

Genera:
- `investment_agent_dag.png` - Diagramma grafico
- `investment_agent_mermaid.md` - Diagramma Mermaid

## 📁 Struttura Progetto

```
PRJ-NEW-AGENT/
├── investment_agent.py          # Agente principale
├── dashboard.py                  # Dashboard Streamlit
├── visualize_investment_dag.py  # Generatore visualizzazioni DAG
├── requirements.txt              # Dipendenze Python
├── .env                          # Variabili d'ambiente (da creare)
├── .gitignore                    # File da ignorare in Git
└── README.md                     # Documentazione
```

## 🛠️ Tools Disponibili

L'agente ha accesso ai seguenti strumenti:

- **`get_stock_quote(symbol)`**: Ottiene quotazione corrente di un titolo
- **`get_market_overview()`**: Panoramica mercati (S&P, NASDAQ, VIX, sentiment)
- **`analyze_sector_performance(sector)`**: Analisi performance settoriale
- **`calculate_portfolio_allocation(amount, risk_profile)`**: Calcola allocazione ottimale

## 🎯 Profili di Rischio

### Conservative (Conservativo)
- 30% Azioni
- 50% Obbligazioni
- 15% Liquidità
- 5% Commodities

### Moderate (Moderato)
- 60% Azioni
- 30% Obbligazioni
- 5% Liquidità
- 5% Commodities

### Aggressive (Aggressivo)
- 80% Azioni
- 10% Obbligazioni
- 5% Liquidità
- 5% Commodities

## 🔧 Tecnologie Utilizzate

- **LangChain & LangGraph**: Orchestrazione agente AI
- **OpenAI GPT-4**: Modello linguistico
- **Streamlit**: Dashboard web interattiva
- **Matplotlib**: Visualizzazioni grafiche
- **Python 3.12**: Linguaggio di programmazione

## ⚠️ Disclaimer

Questo progetto è solo a scopo educativo e dimostrativo. Le raccomandazioni sono generate da un'AI utilizzando dati simulati e **NON costituiscono consulenza finanziaria professionale**. 

Consulta sempre un consulente finanziario certificato prima di prendere decisioni di investimento.

## 📝 Licenza

MIT License

## 👤 Autore

Fabrizio Baldan

## 🤝 Contributi

Contributi, issues e feature requests sono benvenuti!

---

⭐ Se questo progetto ti è stato utile, lascia una stella!
