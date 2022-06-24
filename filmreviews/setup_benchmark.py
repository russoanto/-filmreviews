from dataclasses import dataclass
from typing import TextIO, Optional
import math

import re


@dataclass
class RelevantDocument:
    relevance: int
    id: str


@dataclass
class Benchmark:
    query: str
    scores: list[RelevantDocument]


@dataclass
class BenckmarkList:
    benchmarks: list[Benchmark]

@dataclass
class BenchmarkResult:
    query: Benchmark
    raw: list[int]
    @staticmethod
    def compute_discounted_cumulative_gain(data):
        if len(data) == 0:
            return 0
        return data[0] + sum([(data[i] / math.log(i + 1, 2)) for i in range(1, len(data))])


# query portal 2 # comment
retrive_query = re.compile(r'^query->\s+([^#]+?)\s*(?:#.*)?$', re.IGNORECASE) #regex per recuperare la query
# 3 steam 24201 # comment
retrive_relevant_document = re.compile(r'^(\d+)\s+(\w+)\s*(?:#.*)?$')  #regex per recuperare i id e punteggio dei documenti rilevanti


def parse_suite(lines):
    res: list[Benchmark] = []
    query: Optional[str] = None
    entries: list[RelevantDocument] = []

    row_n = 0
    for line in lines:
        row_n += 1
        line = line.strip()
        if line == "" or line[0] == '#': #se trova una rigavuota o cancelletto allora passa alla riga successiva
            continue
        if match := retrive_query.fullmatch(line): #se una riga combacia con la regex query
            if query is not None:
                res.append(Benchmark(query, entries))
            query = match.groups()[0]
            entries = []
        elif match := retrive_relevant_document.fullmatch(line):
            if query is None:
                print(f"Errore di formattazione alla riga {row_n}")
                quit()

            rel, doc_id = match.groups()
            entries.append(RelevantDocument(int(rel), doc_id))
        else:
            print(f"Errore di sintassi alla riga {row_n}")
            quit()

    if query is not None:
        res.append(Benchmark(query, entries))

    return BenckmarkList(res)
