import os
import pandas as pd

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from tqdm import tqdm  # For progress bar

from dotenv import load_dotenv
load_dotenv()

# Constants for file paths
TAGGED_DESC_PATH = "datasets/tagged_meanings.txt"
EMBEDDINGS_PATH = "datasets/chroma_db"

embedding_model = OpenAIEmbeddings(model='text-embedding-3-large')

# Create & Save Embeddings
def create_and_save_embeddings(padyas: pd.DataFrame) -> Chroma:
    """
    Creates and saves embeddings for padya meanings if no embeddings exist.
    Embeddings are stored in a Chroma vector database for efficient similarity search.
    """
    global embedding_model
    if not os.path.exists(TAGGED_DESC_PATH):
        if not os.path.exists(TAGGED_DESC_PATH.split("/")[0]):
            os.mkdir(TAGGED_DESC_PATH.split("/")[0])

        # Combine ID and meaning into a tagged meaning
        padyas_copy = padyas.copy(deep=True)
        padyas_copy['tagged_meaning'] = padyas_copy['id'].astype(str) + ' ' + padyas_copy['Meaning']
        padyas_copy.loc[:, 'tagged_meaning'] = padyas_copy['tagged_meaning'].apply(lambda meaning: meaning.replace('\n', ' '))
        tagged_meanings = list(padyas_copy['tagged_meaning'])
        tagged_meanings = [(meaning + '\n') for meaning in tagged_meanings]
        with open(TAGGED_DESC_PATH, 'w') as file:
            file.writelines(tagged_meanings)
    
    # Load raw documents and split into chunks
    raw_documents = TextLoader(TAGGED_DESC_PATH).load()
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=0, chunk_overlap=0)
    documents = text_splitter.split_documents(raw_documents)

    # Initialize Chroma DB to store embeddings
    ramayan_db = Chroma(
        collection_name='padya_meanings',
        embedding_function=embedding_model,
        persist_directory=EMBEDDINGS_PATH,
    )

    # Create embeddings in batches and add to the database
    print(
        "No saved Vector DB found for ramayan textual data, so creating a new DB. It might take some time."
    )
    batch_size = 50

    for i in tqdm(range(0, len(documents), batch_size)):
        # print(i)
        batch = documents[i: i+batch_size]
        ramayan_db.add_documents(batch)
    return ramayan_db

# Function to read embeddings
def fetch_embeddings(ramayan_df):
    global embedding_model
    try:
        # Attempt to load the existing embeddings database
        if not os.path.exists(EMBEDDINGS_PATH):
            raise Exception("No saved embeddings found")

        ramayan_db = Chroma(
            collection_name='padya_meanings',
            embedding_function=embedding_model,
            persist_directory=EMBEDDINGS_PATH,
        )

        # Validate the number of documents in the database
        if ramayan_db._collection.count() != len(ramayan_df):
            raise Exception("Invalid embeddings loaded")
            
        return ramayan_db
    except Exception as e:
        # Recreate embeddings if the database is invalid or missing
        print(f"{str(e)}, Recreating embeddings for meanings")
        ramayan_db = create_and_save_embeddings(ramayan_df)
        return ramayan_db

