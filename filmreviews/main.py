import tomatoes,movie_search,imdbClass,merge_search
from whoosh.qparser import syntax, Plugin, QueryParser, MultifieldPlugin
import re
from whoosh.index import open_dir
import tqdm
from benchmark import parse_suite
from benchmark import BenchmarkSuite,BenchmarkResult,BenchmarkEntry
import argparse
import math



RELEVANCE_THRESHOLD = 2


def niceprint(top_k):
    #ogni elemento di topk è aggregatehit dove ho la lista delle hit e punteggio già ordinato

    #attualmente prendo solo u valori più lunghi per fare il marge, ma volevo farvelo vedere cosi mi dite se c'è altro da modificare
    with open('./file2.txt', 'a') as openfile:
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
            
            param =["id", "title","genres", "content", "directors", "casts", "release_date", "runtime","reviews"]
            answare = input('vuoi stampare le recensioni per',a["title"],'? (si = 1): ')
            for i in param:
                if i != "reviews":
                    print(i + ': ' + str(a[i]))
                elif answare == 1:
                    print(i + ': ' + str(a[i]))
    

            print("----------------------------")
            # for z in a:
                
            #     if z == 'reviews':
            #         answare = input('vuoi visualizzare anche i commenti? (1 = si)')
            #         if answare == 1:
            #             openfile.write(z + ":\n" + replaceReviews(a[z]))
            #     else:
            #         openfile.write(z + ": " + str(a[z]))  
            #     openfile.write("\n")
            
            #openfile.write("---------------------------\n")  



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

class FieldBoosterPlugin(Plugin):
        def __init__(self, boosts):
            self.boosts = boosts

        def filters(self, parser):
            return [(self.do_boost, 105)]

        def do_boost(self, parser, group):
            for i, node in enumerate(group):
                if isinstance(node, syntax.GroupNode):
                    group[i] = self.do_boost(parser, node)
                elif node.has_fieldname and node.fieldname is not None:
                    node.set_boost(node.boost * self.boosts.get(node.fieldname, 1.0))
            return group

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
    topk_results = merge_search.aggregate_search(query, searchers, 6)

    return topk_results

def create_parser(idx):
    p = QueryParser(None, idx.ix.schema, group=syntax.OrGroup)
    fieldboosts = {
            'title': 6,
            'content':1,
    }
    mfp = MultifieldPlugin(('title', 'content', 'casts','directors'), fieldboosts=fieldboosts)
    p.add_plugin(mfp)


    p.add_plugin(FieldBoosterPlugin({
            'title':40, 'casts':40, 'release_date':40,'genres':40,'directors':40,'content':40,
    }))
    return p


def searchInIndex(queryPom, queryImd, searchPOM, searchIMD):
    # #--------------------------------------------------------

    # im = QueryParser(None, imdb.ix.schema, group=syntax.OrGroup)
    # fieldboosts = {
    #         'title': 6,
    #         'content':1,
    # }
    # mfp = MultifieldPlugin(('title', 'content', 'casts','directors'), fieldboosts=fieldboosts)
    # im.add_plugin(mfp)


    # p.add_plugin(FieldBoosterPlugin({
    #         'title':40,'content':40,'release_date':40,'genres':40,'directors':40,'casts':40,
    # }))
    print(queryImd, " ", queryPom)
    searchers = [(searchPOM,'tomato'), (searchIMD,'imdb')]
    top_k = merge_search.aggregate_search(queryPom, searchers, 5)

    with open('./informations.txt', 'w') as openfile:
        for i in top_k:
            for j in i:
                openfile.write(str(j)+ ' ')
            openfile.write('\n')

    return top_k

def evaluate(suite,pomodoro, imdb):
    #print(suite.benchmarks)
    res = []
    for bench in suite.benchmarks:
        print(bench)
        topk = run_query(bench.query,pomodoro,imdb,10)
        data = {s.id:s.relevance for s in bench.scores}
        entries = []
        for row in topk:
            relevance = next((d for hit, source in row.hits if (d := data.get(hit['id'])) is not None), 0)
            entries.append(relevance)
        res.append(BenchmarkResult(bench, entries))
    return res


def main(pathBench):
    parser = argparse.ArgumentParser(description='Benvenuti in filmreviews')
    parser.set_defaults(action='prompt')
    subparsers = parser.add_subparsers()


    indexing = subparsers.add_parser('indexing', help='Make web scarping and create whoosh index')
    indexing.set_defaults(action='indexing')

    evaluate_t = subparsers.add_parser('evaluate', help='Evaluate')
    evaluate_t.add_argument('file', help="The benchmark to run the IR against", type=argparse.FileType('rt'))
    evaluate_t.set_defaults(action='evaluate')


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
         
    elif args.action == 'evaluate':
        with args.file as fd:
            suite = parse_suite(fd)
        res = evaluate(suite,pomodoro,imdb)
        avg_precisions = []
        interp_precisions = [0] * 10
        for el in res:
            print(f"{el.query.query} : {[x.relevance for x in el.query.scores]} {el.raw}")


            # DCG = r1 + r2/log_2(2) + r3/log_3(3) etc ...
            val = BenchmarkResult.compute_discounted_cumulative_gain(el.raw)
            print(f"DCG: {val}")

            # IDEAL DCG
            ideal_list = sorted([x.relevance for x in el.query.scores], reverse=True)
            val_ideal = BenchmarkResult.compute_discounted_cumulative_gain(ideal_list)

            print(f"IDEAL DCG: {val_ideal}")
            print(f"NDCG: {val/val_ideal}")

            # NATURAL PRECISION
            natural_pr = []
            tot_rel = sum([x.relevance >= RELEVANCE_THRESHOLD for x in el.query.scores])
            for i, entry in enumerate(el.raw):
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

            avg_prc = sum(natural_pr) / tot_rel
            print(f"Average non-interpolated precision: {avg_prc}")

            avg_int_prc = sum(precisions) / 10
            avg_precisions.append(avg_int_prc)
            print(f"Average interpolated precision: {avg_int_prc}")
            print("\n")

        mean_avg = sum(avg_precisions)/len(res)
        print(f"Mean average precision: {mean_avg}")
        print("Average Standard precision: ")
        print(" | ".join([f"{(key + 1) / 10}:{value / len(interp_precisions)}" for key, value in enumerate(interp_precisions)]))
    else:
        searchPOM = pomodoro.ix.searcher()
        searchIMD = imdb.ix.searcher()

        p = create_parser(pomodoro)
        query_txt = input('Inserire la query --> ')
        query = re.sub(r"\s+[1I]$", "", query_txt.strip())
        try:
            query = p.parse(query_txt)
        except:
            if 'reviews' in query_txt:
                print("Non puoi cercare una recensione")
            else:
                print("Query non valida")
            quit()


        resultPOM = searchPOM.search(query, terms=True, limit=10)
        resultIMD = searchIMD.search(query, terms=True, limit=10)

        print("POMODORO")
        printInformation(resultPOM)
        print("----------------------------")
        print("IMDB")
        printInformation(resultIMD)
        niceprint(searchInIndex(query, query, searchPOM, searchIMD))


    # inQuery = input('Inserire il parametro: ')
        # for i in range(len(queryList)):
        #     print(queryList[i])
        #     query_txt = re.sub("\s+[1I]$", "", queryList[i].strip())

        #     #elaboro query
        #     queryPom = p.parse(query_txt)
        #     queryImd = p.parse(queryList[i])

        #     searchInIndex(queryPom, queryImd, searchPOM, searchIMD) #ricerca negli index richiama anche la funzione printInformation()
    


# readLineBenchmark("benchmark/query.txt")
# writeLineBenchmark("benchmark/query.txt", '- title:"Spiderman" OR title:"Iron man"', "hello")
main("benchmark/query.txt")
