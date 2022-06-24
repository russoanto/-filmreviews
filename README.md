# Game Compendium
Filmreviews
#### Table of Contents
- [Summary](#summary)
- [Installazione](#Installazione)
  - [Dipendenze](#dipendenze)
  


## Summary
Questo progetto si occupa di indicizzare i film presenti (solo una parte per ragioni di tempo e spazio) su [Rottentomatoes](https://www.rottentomatoes.com/) e su [IMDB](https://www.imdb.com/). Il progetto ha gia i 2 indici pronti, è possibile eseguire una nuova indicizzazione ma bisogna considerare che richiede più di 1 ora di tempo.

## Installazione
Per l'installazione si consiglia l'uso di python 3.9.2 e superiori. Per comodità abbiamo scelto l'uso di pipenv in modo da facilitare l'installazione delle dipendenze.

### Dependencies

Come detto in precedenza questo progetto fa uso di pipenv, quindi una volta installato pipenv eseguire
```bash
$ cd filmreviews/
$ pipenv install -r requirements.txt
```
In questo modo abbiamo un ambiente virtuale con tutte le dipendenze del progetto

### Running

```bash
$ python filmreviews/main.py --help
```

1.	indexing: permette di avviare la fase di web scraping e indicizzazione delle 2 fonti, richiede molto tempo (+ 1h), il progetto ha già di default ha già i due indici. Attenzione: Una volta che l'indicizzazione verrà avviata, se interrotta i progressi fino a quel punto non saranno salvati e l'operazione di indicizzazione dovrà essere riavviata.

```bash
$ python filmreviews/main.py  indexing
```

2. benchmark: peremtte di calcolare i vari parametri di benchmark rispetto a 10 query di testing, bisogna passare il file contenente le query con i rispettivi "documenti rilevanti"
```bash
$ python filmreviews/main.py benchmark  filmreviews/query_benchmark
```
3. di default se non siinseriscono parametri sarà possibile effettuare una ricerca mediante il linguaggio di interrogazione definito
