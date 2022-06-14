from whoosh.analysis import RegexTokenizer,default_pattern, LowercaseFilter,StopFilter,Analyzer

def StandardAnalyzer_num():
    ret = RegexTokenizer(expression=default_pattern)
    chain = ret | LowercaseFilter() | StopFilter(minsize=1)
    return chain