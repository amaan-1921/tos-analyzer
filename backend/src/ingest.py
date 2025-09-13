"""
Ingestion Utility for uploaded documents

"""

from langchain_setup import driver, llm

import spacy
import re
from typing import List, Tuple

nlp = spacy.load("en_core_web_sm")

TRIPLE_PATTERN = re.compile(r"^\(\s*[^,]+,\s*[^,]+,\s*[^,]+\s*\)$")


def store_chunks_in_neo4j(chunks, embeddings):
    """
    Stores chunks as nodes in the Neo4J database using the driver
    defined in langchain_setup. Creates a node with the values(id, 
    text, and embedding).

    Args:
        chunks (List[str]): The list of text chunks. Each chunk is
        an str.

        embeddings (List[numpy arr]): The list of the embeddings of
        the text chunks. Each embedding is a numpy array.

    Creates:
        Node/Chunk:
            - id (str): Unique ID corresponding to any node/chunk.
            - text (str): Chunk text.
            - embedding (List): The embedding numpy array as a list
    """
    with driver.session() as session:
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            session.run(
                """
                CREATE (c:Chunk {id: $id, text: $text, embedding: $embedding})
                """,
                id=str(i),
                text=chunk,
                embedding=emb.tolist()  
            )

def extract_triples_from_chunk(chunk_text: str) -> List[Tuple[str, str, str]]:
    """
    Utility to generate triplets from each chunk's text. Invokes the LLM defined in
    langchain_setup to create an a list of triplets of the form (Entity1, Relation, Entity2).

    Args:
        chunk_text (str): The text in the chunk to be used to generate the triples.

    Returns:
        List[Tuple[str, str, str]]: The list containing tuples representing each triple,
        which contains 3 strings representing entity1, relation, entity2 respectively.
    """

    prompt = f"Extract subject-relation-object triples from this text:\n {chunk_text} \nOutput as (S,R,O) tuples."
    response = llm.invoke(prompt)
    # Assuming response.content is parseable; e.g., "(User, agrees_to_share, Data)"
    triples : List[Tuple[str, str, str]] = []
    lines : list[str] = []

    for item in response.content:
        if isinstance(item, str):
            lines = item.split("\n")  # now safe, each item is a string
        elif isinstance(item, dict) and "text" in item:
            lines = item["text"].split("\n")
        else:
            continue

    for line in lines:
        line = line.strip()
        if TRIPLE_PATTERN.match(line):
            s, r, o = [x.strip() for x in line[1:-1].split(",")]
            if(all([s, r, o])):
                triples.append((s, r, o))
        else:
            print(f"Skipping line: {line}. Does not match pattern.")

    if not triples:
        print("No suitable triples found. Returning empty list")
    
    return triples

def store_triples(triples, chunk_id):
    """
    Utility to store the triples as a KG in the Neo4j database,
    using the driver defined in langchain_setup.

    Args:
        triples (List[Tuple[str, str, str]]): A list of tuples containing
        three strings that are semantically related as entity1, relation,
        entity2.

        chunk_id (str): Unique ID of the concerned chunk the triple came
        from.

    Creates:
        KG Node/Reln
    """
    with driver.session() as session:
        for s, r, o in triples:
            session.run(
                """
                MERGE (sub:Entity {name: $subj})
                MERGE (obj:Entity {name: $obj})
                MERGE (sub)-[rel:`$rel`]->(obj)
                MERGE (c:Chunk {id: $chunk_id})
                MERGE (sub)-[:MENTIONED_IN]->(c)
                MERGE (obj)-[:MENTIONED_IN]->(c)
                """,
                subj=s,
                obj=o,
                rel=r,
                chunk_id=chunk_id
            )

