# Filmreviews
Filmreviews
#### Table of Contents
- [Summary](#summary)
- [Installazione](#Installazione)
  - [Dipendenze](#dipendenze)
    - [Linux/Unix](#Linux/Unix)
    - [Windows](#windows)
  


## Summary
Questo progetto si occupa di indicizzare i film presenti (solo una parte per ragioni di tempo e spazio) su [Rottentomatoes](https://www.rottentomatoes.com/) e su [IMDB](https://www.imdb.com/). Il progetto ha gia i 2 indici pronti, è possibile eseguire una nuova indicizzazione ma bisogna considerare che richiede più di 1 ora di tempo.

## Installazione
Per l'installazione si consiglia l'uso di python 3.9.2 e superiori. Per comodità abbiamo scelto l'uso di pipenv in modo da facilitare l'installazione delle dipendenze.

### Dipendenze
### -------------------------------------------------
#### Linux/Unix


Come detto in precedenza questo progetto fa uso di pipenv, quindi una volta installato pipenv eseguire
```bash
$ cd filmreviews/
$ pipenv install -r requirements.txt
$ cd filmreviews/
```
In questo modo abbiamo un ambiente virtuale con tutte le dipendenze del progetto.
Se ci sono problemi durante la crazione del virtual environment a causa della versione di python è possibile cambiarla manualmente modificando il file Pipenv. Come specificato in precedenza la versione minima su cui è stato testato è su python 3.9 

Se si vuole eseguire un installazione automatizzata si può lanciare il seguente comando da una console bash

```bash
$ bash installUpdate.sh
```

### -------------------------------------------------

#### Windows

Bisogna aver installato python - pip sul proprio computer, non si potrà utilizzare gli script per l'installazione, ma si dovrà fare necessariamente a mano.

```power shell
$ cd ./filmrewies/
$ python.exe -m pip install -r requirements.txt
$ cd ./filmrewies/
```
Non sarà presente un ambiente virtuale con questa serie di comandi.

### Running

Attenzione !!! bisogna essere nella directory filmreviews/filmreviews per lanciare i comandi.

```bash
$ python main.py --help
```

1.	indexing: permette di avviare la fase di web scraping e indicizzazione delle 2 fonti, richiede molto tempo (+ 1h), il progetto ha già di default ha già i due indici. Attenzione: Una volta che l'indicizzazione verrà avviata, se interrotta i progressi fino a quel punto non saranno salvati e l'operazione di indicizzazione dovrà essere riavviata.

```bash
$ python main.py  indexing
```

2. benchmark: peremtte di calcolare i vari parametri di benchmark rispetto a 10 query di testing, bisogna passare il file contenente le query con i rispettivi "documenti rilevanti"
```bash
$ python main.py benchmark  filmreviews/query_benchmark
```
3. di default se non si inseriscono parametri sarà possibile effettuare una ricerca mediante il linguaggio di interrogazione definito
```bash
$ python main.py 
```

Per eseguire un processo di esecuzione automatizzato (ricerca query -> benchmark) si può lanciare il seguente comando da una console bash:

```bash
$ bash executePython.sh
```
