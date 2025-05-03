import pandas as pd

from langchain_chroma import Chroma

def retrieve_semantic_matches(
    query: str,
    top_k: int = 10,
    embeddings_db: Chroma = None,
    dataframe: pd.DataFrame = None
) -> pd.DataFrame:
    matches = embeddings_db.similarity_search(query=query, k = top_k)
    
    res_list = []
    for i in range(0, len(matches)):
        res_list += [int(matches[i].page_content.strip('"').split()[0].strip())]
        
    return dataframe[dataframe['id'].isin(res_list)]