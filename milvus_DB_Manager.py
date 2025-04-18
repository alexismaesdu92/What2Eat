from pymilvus import MilvusClient, DataType
from dataclasses import dataclass
import  concurrent.futures
import torch
from tqdm import tqdm
from typing import Dict, List

import os
import numpy as np

from encoder import Encoder


class CollectionCreator:

    def __init__(self, milvus_client: MilvusClient, collection_name:str, dim:int = 768):
        self.client = milvus_client
        self.collection_name = collection_name
        self.dim = dim

    def create_collection(self):
        if self.client.has_collection(self.collection_name):
            self.client.drop_collection(self.collection_name)

        schema = self.client.create_schema(enable_dynamic_fields=True)
        schema.add_field(field_name='id',
                         datatype=DataType.INT64,
                         is_primary=True,
                         auto_id=True)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self.dim)
        schema.add_field(field_name="nom", datatype=DataType.VARCHAR, max_length=128)
        schema.add_field(field_name="url", datatype=DataType.VARCHAR, max_length=512)
        
        client.create_collection(collection_name=self.collection_name,
                                      schema=schema,
                                      dimension=self.dim)
        
        print("collection crée avec succès")

class Indexor:
    def __init__(
            self, 
            client:MilvusClient,
            collection_name:str,
            encoder:Encoder,
            dim:int = 768,
    ):
        self.client = client
        self.collection_name = collection_name
        self.encoder = encoder
        self.dim = dim

    def create_index(self):
        self.client.release_collection(collection_name=self.collection_name)
        self.client.drop_index(collection_name=self.collection_name, index_name="vector")
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_name="vector_index",
            index_type="IVF_FLAT",
            metric_type="IP",
            params={"nlist":128}
        )
        self.client.create_index(
            collection_name=self.collection_name,
            index_params=index_params, sync=True
        )

    def index(self, recipe_name: str, url: str, recipe):
        embedding: torch.Tensor = self.encoder.encode(recipe)  # shape: (dim,)
        
        data: Dict = {
            "vector": embedding.cpu().tolist(),  
            "nom": recipe_name,
            "url": url
        }

        self.client.insert(
            collection_name=self.collection_name,
            data=[data])


class Retriever:
    def __init__(
        self,
        client: MilvusClient,
        encoder,
        collection_name: str,
        metric_type: str = "IP",
        nprobe: int = 10
    ):
        """
        :param client: instance de MilvusClient déjà connectée
        :param encoder: ton objet Encoder, avec une méthode encode(text)->torch.Tensor
        :param collection_name: nom de la collection à interroger
        :param metric_type: "IP" ou "L2"
        :param nprobe: nombre de probes à utiliser pour la recherche
        """
        self.client = client
        self.encoder = encoder
        self.collection_name = collection_name
        self.search_params = {
            "metric_type": metric_type,
            "params": {"nprobe": nprobe}
        }


    def retrieve(self, query_text: str, top_k: int = 1) -> List[Dict]:
        """
        :param query_text: texte de ta requête (ex: "recette avec coco et curry")
        :param top_k: nombre de résultats à retourner
        :return: liste de dicts {'nom': ..., 'url': ..., 'score': ...}
        """
        embedding = self.encoder.encode(query_text).cpu().tolist()

        # 2. Lance la recherche dans Milvus
        results = self.client.search(
            collection_name=self.collection_name,
            data=[embedding],
            limit=top_k,
            output_fields=["nom", "url"],
            search_params=self.search_params
        )

        # 3. Formate la sortie
        hits = []
        for hit in results[0]:  # results[0] car on a une seule requête
            hits.append({
                "nom": hit["entity"]["nom"],
                "url": hit["entity"]["url"],
                "score": hit["distance"]
            })

        return hits
    




NAME = "food_bank"
DBNAME = f"{NAME}.db"
DATA_PATH = "data"
PATH = os.path.join(DATA_PATH, DBNAME)



if __name__ == "__main__":
    encoder = Encoder()
    db_path = "data/test.db"
    client = MilvusClient(db_path)
    collection_name = "test_collection"
    collection_creator = CollectionCreator(client, collection_name)
    # collection_creator.create_collection()

    indexor = Indexor(client, collection_name, encoder)
    # indexor.create_index()

    # for i in tqdm(range(1000)):
    #     indexor.index(f"testing{i}", f"urllllll{i}", f"je mets ce qque je veux{i}")
    
    retriever = Retriever(client=client, encoder=encoder, collection_name=collection_name)

    hits = retriever.retrieve("je mets ce qque je veux99")
    print(hits)
    

    
    


