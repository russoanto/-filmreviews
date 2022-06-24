import tomatoes,movie_search,imdbClass,merge_search
from whoosh.qparser import syntax, Plugin, QueryParser, MultifieldPlugin
import re
from whoosh.index import open_dir
from tqdm import tqdm
from setup_benchmark import parse_suite
from setup_benchmark import BenckmarkList,BenchmarkResult,RelevantDocument
import argparse
import math
import matplotlib.pyplot as plt
import numpy as np


RELEVANCE_THRESHOLD = 2


def plot(x,y):
    plt.plot(x, y)
    
    # naming the x axis
    plt.xlabel('x - axis')
    # naming the y axis
    plt.ylabel('y - axis')
    
    # giving a title to my graph
    plt.title('My first graph!')
    
    # function to show the plot
    plt.show()



def niceprint(top_k, p="default"):
    #ogni elemento di topk è aggregatehit dove ho la lista delle hit e punteggio già ordinato

    #attualmente prendo solo u valori più lunghi per fare il marge, ma volevo farvelo vedere cosi mi dite se c'è altro da modificare
    print()
    try:
        for agghit in top_k:
            #devo mettere assieme
            #e preparare una lista di risultati dove ho le info
            #sono già ordinate quindi mi basta fare degli append
            #trama più lubnga
            #recensioni metto assieme
            #durata 1 sola
            #genres (soluzione bonus)
            #attori e cast, regista(soluzione bonus)
            
            #score = agghit[1]

            hitlist = []
            #hitlist.clear()
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
    s = str(s)
    s = s.replace("\\'", "'").replace("\\n", '\n')
    s = s.replace("[['", "\'").replace("[[\"", "\"").replace("\"]]", "\"").replace("']]", "\'")
    s = s.replace("[\'", "'").replace("[\"", "\"").replace("\"]", "\"").replace("\']", "\'")    
    return s



def mergeSameHit(hitlist):
    
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
    '''
    print("entro, ", type(get))
    get.get_all_information_t()
    get.indexing()

def printInformation(result):
    '''
    stampa le informazioni della singola classe imdb o pomodoro
    '''
    if result.has_matched_terms():
        scores = []
        for x in result:
            print(x["title"] + ' --> ' + x["id"] + '   ' + str(x.score)+ '\n')
            scores.append(x.score)

def run_query(query_txt, pomodoro,imdb, k: int = 5):
    # Remove "1" from the end of queries, this helps since games are
    # always stored as "Portal" not "Portal 1"

    searchPOM = pomodoro.ix.searcher()
    searchIMD = imdb.ix.searcher()

    query_txt = re.sub(r"\s+[1I]$", "", query_txt.strip())
    p = create_parser(pomodoro)
    query = p.parse(query_txt)
    searchers = [(searchPOM,'tomato'), (searchIMD,'imdb')]
    topk_results = merge_search.aggregate_search(query, searchers, k)

    return topk_results

def create_parser(idx):
    p = QueryParser(None, idx.ix.schema, group=syntax.OrGroup)
    fieldboosts = {
            'title': 6,
            'content':2,
    }

    #Returns a QueryParser configured to search in multiple fields. (documentazione whoosh)
    #Instead of assigning unfielded clauses to a default field, this parser transforms them 
    # into an OR clause that searches a list of fields. For example, if the list of multi-fields is 
    # “f1”, “f2” and the query string is “hello there”, the class will parse “(f1:hello OR f2:hello) 
    # (f1:there OR f2:there)”. This is very useful when you have two textual fields (e.g. “title” and “content”) 
    # you want to search by default
    mfp = MultifieldPlugin(('title', 'content', 'casts','directors'), fieldboosts=fieldboosts)
    p.add_plugin(mfp)

    return p


def searchInIndex(query,searchPOM, searchIMD, k:int = 5):
    searchers = [(searchPOM,'tomato'), (searchIMD,'imdb')]
    top_k = merge_search.aggregate_search(query, searchers, k)
    return top_k

def evaluate(suite,pomodoro, imdb):

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

    pomodoro = tomatoes.indexTomatoes(data)

    imdb = imdbClass.imdbIndex("./movies/index.json", data, "https://www.imdb.com")


    if args.action == 'indexing':
        answare = input('Quale fonte si vuole indicizzare? (default all, 1 = tomato, 2 = imdb)')
        if answare == '1':
            getInformation_indexing(pomodoro)
        elif answare == '2':
            getInformation_indexing(imdb)
        else:
            getInformation_indexing(pomodoro)
            getInformation_indexing(imdb)
         
    elif args.action == 'bench':
        #leggo il file di benchmark
        with args.file as fd:
            suite = parse_suite(fd)
        res,topk = evaluate(suite,pomodoro,imdb) #estraggo i per ogni query i documenti rilevanti e il suo ranking dei risultati uniti
        
        avg_precisions = []
        interp_precisions = [0] * 10
        
        j = 0
        for el in res:
            print(el.results_point)
            print(f"{el.query.query} : {[x.relevance for x in el.query.scores]} {el.results_point}")
            
            schema = input("Inserire il tipo di ritorno si vuole visualizzare (default-invio- -> \"title\", altrimenti inserisci)")
            #schema = ""
            if schema == "":
                niceprint(topk[j], "title")
            else:
                niceprint(topk[j], schema)
            #---------------------------

            # DCG = r1 + r2/log_2(2) + r3/log_3(3) etc ...
            val = BenchmarkResult.compute_discounted_cumulative_gain(el.results_point)
           

            # IDEAL DCG (viene fatto)
            ideal_list = sorted([x.relevance for x in el.query.scores], reverse=True)
            val_ideal = BenchmarkResult.compute_discounted_cumulative_gain(ideal_list)
            if val_ideal != 0:
                # print(f"DCG: {val}")
                # print(f"IDEAL DCG: {val_ideal}")
                # print(f"NDCG: {val/val_ideal}")

                # NATURAL PRECISION

                natural_pr = []
                tot_rel = sum([x.relevance >= RELEVANCE_THRESHOLD for x in el.query.scores])
                for i, entry in enumerate(el.results_point):
                    if entry >= RELEVANCE_THRESHOLD:
                        precision = (len(natural_pr) + 1)/(i + 1)
                        natural_pr.append(precision)

                print("Natural precision: ")
                print(" | ".join([f"{(i + 1) / tot_rel}:{value}" for i, value in enumerate(natural_pr)]))

                # STANDARD PRECISION
                precisions = [0.0] * 10
                for i in range(10):
                    maxval = max([value for j, value in enumerate(natural_pr) if (j + 1) / tot_rel >= (i + 1) / 10], default=0)
                    precisions[i] = maxval
                    interp_precisions[i] += maxval
                print("Standard precision: ")
                print(" | ".join([f"{(i+1)/10}:{value}" for i, value in enumerate(precisions)]))
                #values = [value for i,value in enumerate(precisions)]
                avg_prc = sum(natural_pr) / tot_rel
                print(f"Average non-interpolated precision: {avg_prc}")

                avg_int_prc = sum(precisions) / 10
                avg_precisions.append(avg_int_prc)
                print(f"Average interpolated precision: {avg_int_prc}")
            else:
                print("Nessun risultato ottenuto")
            print("\n")
            j += 1


        mean_avg = sum(avg_precisions)/len(res)
        print(f"Mean average precision: {mean_avg}")
        print("Average Standard precision: ")
        values = [value/len(interp_precisions) for key, value in enumerate(interp_precisions)]
        plot(np.arange(0,1.0,0.1), values)
        print(" | ".join([f"{(key + 1) / 10}:{value / len(interp_precisions)}" for key, value in enumerate(interp_precisions)]))
    else:
        searchPOM = pomodoro.ix.searcher()
        searchIMD = imdb.ix.searcher()

        p = create_parser(pomodoro)
        query_txt = bytearray(input('Inserire la query --> ').encode()).decode('utf-8')
        query = re.sub(r"\s+[1I]$", "", query_txt.strip())
        try:
            query = p.parse(query_txt)
        except:
            if 'reviews' in query_txt:
                print("Non puoi cercare una recensione")
            else:
                print("Query non valida")
            quit()

               
        k = input("inserire il limite di match (default - invio - 5, altrimenti il tuo numero):")
        if k == "":
            k = 5
            resultPOM = searchPOM.search(query, terms=True, limit=k)
            resultIMD = searchIMD.search(query, terms=True, limit=k)

            print("POMODORO")
            printInformation(resultPOM)
            print("----------------------------")
            print("IMDB")
            printInformation(resultIMD)
        
            niceprint(searchInIndex(query, searchPOM, searchIMD))
        else:
            niceprint(searchInIndex(query, searchPOM, searchIMD, int(k)))


main()