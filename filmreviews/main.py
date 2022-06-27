import tomatoes,movie_search,imdbClass,merge_search
from whoosh.qparser import syntax, Plugin, QueryParser, MultifieldPlugin
import re
import os
from whoosh.index import open_dir
from tqdm import tqdm
from setup_benchmark import parse_suite
from setup_benchmark import BenckmarkList,BenchmarkResult,RelevantDocument
import argparse
import shutil
import math
import matplotlib.pyplot as plt
import numpy as np


RELEVANCE_THRESHOLD = 2


def plot(x,y):
    '''
    Quasta funzione definisce e stampa il grafico delle query analizzate
    Riceve in ingresso due numeri float
    '''
    plt.plot(x, y)
    
    # naming the x axis
    plt.xlabel('x - axis')
    # naming the y axis
    plt.ylabel('y - axis')
    
    # giving a title to my graph
    plt.title('Average Precision (Standard Level)')
    
    # function to show the plot
    plt.show()



def niceprint(top_k, p="default"):
    '''
    Questa funzione stampa il contenuto dei risultati della query, e fa il merge delle due soluzioni
    #trama più lubnga
    #recensioni metto assieme
    #durata 1 sola
    #genere (soluzione bonus)
    #attori e cast, regista(soluzione bonus)
    prende in input top_k, il contenuto con rank più alto, ed una p il nome del contenuto da stampare, se è default li stampa tutti
    '''
    
    print()
    try:
        for agghit in top_k:

            hitlist = []

            for hitstr in agghit[0]:
                hit = hitstr[0]
                hitlist.append(hit)
            
            a = mergeSameHit(hitlist)

            if p == "default":
                param =["id", "title","genres", "content", "directors", "casts", "release_date", "runtime","reviews"]
                answare = input('vuoi stampare le recensioni per ' + str(a[param[1]]) + '? (si = 1): ')
                for i in param:
                    if i != "reviews":
                        print(i + ': ' + str(a[i]) + '\n')
                    elif answare == "1":
                        print(i + ': ' + replaceReviews(str(a[i])) + '\n')
            else:
                if p == "reviews":
                    print(replaceReviews(a[p]))
                else:
                    print(a[p])
            print("----------------------------")
    except:
        print("Inserito pramentro sbagliato")
    print()




def replaceReviews(s):
    '''
    visualizza correttamente il contenuto delle reviews e lo ritorna 
    prende in input una stringa
    '''
    s = str(s)
    s = s.replace("\\'", "'").replace("\\n", '\n')
    s = s.replace("[['", "\'").replace("[[\"", "\"").replace("\"]]", "\"").replace("']]", "\'")
    s = s.replace("[\'", "'").replace("[\"", "\"").replace("\"]", "\"").replace("\']", "\'")    
    return s



def mergeSameHit(hitlist):
    
    '''
    prende in input una lista di 
    '''

    if(len(hitlist)==1):
        return hitlist[0]
    
    res = dict()
    #metto tutti quelli che non ci sono tra uno e l'altro
    #print(len(hitlist[1]))
    for k0,v0 in hitlist[0].items(): 

        if k0 not in res:
            res[k0] = v0
    
    
    for k1,v1 in hitlist[1].items():
        if k1 not in res:
            res[k1] = v1
        else:
            #qua sono sicuro di dover fare magheggi
            if k1 == "reviews":
                #res[k1] = "lol"
                res[k1] = hitlist[0]["reviews"] + hitlist[1]["reviews"]
                # print("tot  ",len(res[k1]))
                # print("------------\n")

            if(len(hitlist[0][k1])>len(v1)):
                res[k1]=hitlist[0][k1]
            else:
                res[k1]=v1

    return res 



#######################################################



def getInformation_indexing(get):
    '''
    Fa scraping e indexing delle due fonti, imdb e pomodoro (get riceve uno dei due alla volta).
    la funzione richiede parecchio tempo per il suo completamento
    '''
    
    get.get_all_information_t()
    get.indexing()

def printInformation(result):
    '''
    stampa le informazioni della singola classe imdb o pomodoro
    '''
    if result.has_matched_terms():
        scores = []
        for x in result:
            print('title: ' + x["title"] + '\n id: ' + x["id"] + '\n score: ' + str(x.score)+ '\n')
            print("--------------------------------------------")
            scores.append(x.score)

def run_query(query_txt, pomodoro,imdb, k: int = 5, searchSingle = False):
    '''
    Questa funzione, esegue la query in ingresso, e ritorna il topk ovvero la lista dei risultati della query con il merge.
    prende in ingresso l'indice di tomatoes, imdb, un valore numerico, la stringa con la query, ed un boolean per la richiesta della stampa del singolo indice (prima tomatoes e poi imdb)
    '''
    searchPOM = pomodoro.ix.searcher()
    searchIMD = imdb.ix.searcher()
    query_txt = re.sub(r"\s+[1I]$", "", query_txt.strip())
    p = create_parser(pomodoro)
    query = p.parse(query_txt)

    if searchSingle:
        #ricerco sui singoli indici e li stampo
        resultPOM = searchPOM.search(query, terms=True, limit=k)
        resultIMD = searchIMD.search(query, terms=True, limit=k)

        print("POMODORO")
        printInformation(resultPOM)
        print("IMDB")
        printInformation(resultIMD)

    searchers = [(searchPOM,'tomato'), (searchIMD,'imdb')]
    topk_results = merge_search.aggregate_search(query, searchers, k)
    return topk_results

def create_parser(idx):

    '''
    Creo il parse della query
    '''
    p = QueryParser(None, idx.ix.schema, group=syntax.OrGroup)
    fieldboosts = {
            'title': 6,
            'content':2,
    }
    '''
    Returns a QueryParser configured to search in multiple fields. (documentazione whoosh)
    Instead of assigning unfielded clauses to a default field, this parser transforms them 
    into an OR clause that searches a list of fields. For example, if the list of multi-fields is 
    “f1”, “f2” and the query string is “hello there”, the class will parse “(f1:hello OR f2:hello) 
    (f1:there OR f2:there)”. This is very useful when you have two textual fields (e.g. “title” and “content”) 
    you want to search by default
    '''
    mfp = MultifieldPlugin(('title', 'content', 'casts','directors'), fieldboosts=fieldboosts)
    p.add_plugin(mfp)

    return p

def evaluate(suite,pomodoro, imdb):
    '''
    la valutazione dei benchmark, sulle proposte fatte sul file, query_benchmark, confronta con i suoi risultati ed inserisce 0 se non trova la corrispondenza
    altrimenti inserisce il numero proposto
    '''
    res = []
    topk = []
    for i in tqdm(range(len(suite.benchmarks))):
        bench = suite.benchmarks[i]
        topk.append(run_query(bench.query,pomodoro,imdb,6))
        # per ogni query salvo id dei documenti rilevanti con relativo score
        data = {s.id:s.relevance for s in bench.scores} 
        entries = []
        for row in topk[i]:
            relevance = next((d for hit, source in row.hits if (d := data.get(hit['id'])) is not None), 0)
            entries.append(relevance)
        res.append(BenchmarkResult(bench, entries))

    return res, topk


def create_command_line(subparsers):
    '''
    Selezione dei comandi da svolgere
    '''
    indexing = subparsers.add_parser('indexing', help='Make web scarping and create whoosh index')
    indexing.set_defaults(action='indexing')

    bench_t = subparsers.add_parser('benchmark', help='Benchmark')
    bench_t.add_argument('file', help="Avvia il processo di benchmark", type=argparse.FileType('r'))
    bench_t.set_defaults(action='bench')


def main():
    parser = argparse.ArgumentParser(description='Benvenuti in filmreviews')
    parser.set_defaults(action='prompt')
    subparsers = parser.add_subparsers()
    create_command_line(subparsers)

    args = parser.parse_args()

    searcher = movie_search.movie_search()
    # searcher.getGenrId()
    # searcher.getAllPageMovie()
    data = searcher.readIndex()  #creazione indice di base

    def delete_index(path):
        if os.path.exists(path):
            shutil.rmtree(path)
    def create_source():
        pomodoro = tomatoes.indexTomatoes(data)
        imdb = imdbClass.imdbIndex("./movies/index.json", data, "https://www.imdb.com")        
        return pomodoro,imdb

    pomodoro,imdb = create_source()

    if args.action == 'indexing':
        answare = input('Quale fonte si vuole indicizzare? (default all, 1 = tomato, 2 = imdb)')
        if answare == '1':
            delete_index('./indexdir')
            pomodoro,imdb = create_source()
            getInformation_indexing(pomodoro)
        elif answare == '2':
            delete_index('./indexdirIMDB')
            pomodoro,imdb = create_source()
            getInformation_indexing(imdb)
        else:
            delete_index('./indexdir')
            delete_index('./indexdirIMDB')

            pomodoro,imdb = create_source()

            getInformation_indexing(pomodoro)
            getInformation_indexing(imdb)
         
    elif args.action == 'bench':
        #Esecuzione del benchmark
        #leggo il file di benchmark
        with args.file as fd:
            suite = parse_suite(fd)
        res,tok = evaluate(suite,pomodoro,imdb) 
        #estraggo i per ogni query i documenti rilevanti con tutti i suoi risultati 
        
        avg_precisions = []
        interp_precisions = [0] * 10
        
        for el in res:
            #Eseguo le stampe e i calcoli per i benchmark di ogni singola query
            print(f"{el.query.query} : {[x.relevance for x in el.query.scores]} {el.results_point}")


            # DCG = r1 + r2/log_2(2) + r3/log_3(3) etc ...
            val = BenchmarkResult.compute_discounted_cumulative_gain(el.results_point)
           

            # IDEAL DCG (viene fatto)
            ideal_list = sorted([x.relevance for x in el.query.scores], reverse=True)
            val_ideal = BenchmarkResult.compute_discounted_cumulative_gain(ideal_list)
            if val_ideal != 0:
                print(f"DCG: {val}")
                print(f"IDEAL DCG: {val_ideal}")
                print(f"NDCG: {val/val_ideal}")

                # NATURAL PRECISION

                natural_precision = []
                tot_rel = sum([x.relevance >= RELEVANCE_THRESHOLD for x in el.query.scores])
                for i, entry in enumerate(el.results_point):
                    if entry >= RELEVANCE_THRESHOLD:
                        precision = (len(natural_precision) + 1)/(i + 1)
                        natural_precision.append(precision)
                print('====================================================')
                print("PRECISIONE A LIVELLI NATURALI: ")
                print("\n".join([f"lv. {(i + 1) / tot_rel} value {value}" for i, value in enumerate(natural_precision)]))

                # STANDARD PRECISION
                precisions = [0.0] * 10
                for i in range(10):
                    maxval = max([value for j, value in enumerate(natural_precision) if (j + 1) / tot_rel >= (i + 1) / 10], default=0)
                    precisions[i] = maxval
                    interp_precisions[i] += maxval
                print('====================================================')
                print("PRECISIONE A LIVELLI STANDARD: ")
                print("\n".join([f"lv. {(i+1)/10} value {value}" for i, value in enumerate(precisions)]))
                #values = [value for i,value in enumerate(precisions)]
                avg_prc = sum(natural_precision) / tot_rel
                print('====================================================')

                print(f"PRECISIONE MEDIA (NON INTERPOLATA): {avg_prc}")

                avg_int_prc = sum(precisions) / 10
                avg_precisions.append(avg_int_prc)
                print('====================================================')

                print(f"PRECISIONE MEDIA (INTERPOLATA): {avg_int_prc}")
            else:
                print("Nessun risultato ottenuto")
            print("\n")

        print('====================================================')
        mean_avg = sum(avg_precisions)/len(res)
        print(f"MEAN AVERAGE PRECISION: {mean_avg}")
        print('====================================================')
        print("AVERAGE STANDARD PRECISION: ")
        values = [value/len(interp_precisions) for key, value in enumerate(interp_precisions)]
        print("\n".join([f"lv. {(key + 1) / 10} value {value / len(interp_precisions)}" for key, value in enumerate(interp_precisions)]))
        ri = input("Inserire il carattere 's' per visualizzare il grafico (altrimenti qualsiasi altra stringa per andare oltre): ")
        if ri == "s":
            try:
                plot(np.arange(0,1.0,0.1), values)
            except:
                print("Pacchetto python3-tk mancante, serve per la stampa del grafico")
        else:
            print("Il grafico non verrà stampato, Grazie e arrivederci")

    else:
        #Esecuzione singola query
        query_txt = input('Inserire la query --> ')
        k = input("inserire il limite di match (default - invio - 5, altrimenti il tuo numero):")
        try:
            k = int(k)
        except:
            k = 5

        try:
            niceprint(run_query(query_txt, pomodoro, imdb, k, True))
        except:
            if 'reviews' in query_txt:
                print("Non puoi cercare una recensione")
            else:
                print("Query non valida")
            quit()

main()