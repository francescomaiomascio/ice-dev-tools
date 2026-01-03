# ice-devtools

`ice-devtools` è un pacchetto Python di **strumenti di sviluppo** per parsing, normalizzazione,
detection euristica ed esportazione di dati strutturati.

È progettato come **modulo standalone**, ma nasce come parte dell’ecosistema **ICE**.

---

## 🎯 Obiettivi

- Parsing robusto di log e testi semi-strutturati
- Detection euristica (pattern, timestamp, multiline)
- Normalizzazione eventi
- Utilities riutilizzabili (export, formatting, validation)
- Zero dipendenza dal runtime ICE / engine
- Codice leggibile, modulare, mantenibile

---

## 📁 Struttura

```
ice_devtools/
├── core/ # Tipi base, eccezioni, config
├── parsing/ # Reader, normalizer, processor
├── detection/ # Detector base, pattern, date parser
├── formatting/ # Exporter, colori, conversioni
├── generation/ # Generatori offline (CV, report)
├── validation/ # Validator puri (no side effects)
├── timeutils/ # Utility temporali
```


---

## 🔍 Parsing pipeline (concettuale)

File / Stream
↓
LogReader
↓
UniversalDetector (pattern, timestamp, multiline)
↓
LogNormalizer
↓
LogEvent pulito (ML-ready)


⚠️ **Nota:**  
`ice-devtools` **NON fa ML**.  
Qualsiasi classificazione, clustering o embedding è deliberatamente fuori scope.

---

## 🧠 Componenti principali

### Parsing
- `LogReader`: lettura file (text, CSV, JSON, JSONL)
- `LogProcessor`: pipeline di parsing base
- `LogNormalizer`: pulizia e standardizzazione eventi

### Detection
- `BaseDetector`: interfaccia comune
- `UniversalDetector`: detection euristica generale
- `DateParser`: parsing avanzato timestamp

### Formatting / Export
- `Exporter`: CSV / JSON / HTML / Markdown / TXT
- Utility colore e conversione

### Generation
- `CVGenerator`: generatore PDF CV data-driven (ReportLab)

---

