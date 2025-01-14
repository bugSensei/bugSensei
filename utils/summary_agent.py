import os
from mistralai import Mistral
from llama_index.core import SimpleDirectoryReader, get_response_synthesizer
from llama_index.core import DocumentSummaryIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import SimpleDirectoryReader
from llama_index.core import SummaryIndex, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_completion_callback
from typing import Optional

# custom mistral llm object for the MistralAPI
class MistralLLM(CustomLLM):
    context_window: int = 4096
    num_output: int = 2048
    model_name: str = "custom"

    mistral_client: Optional[Mistral] = None

    def __init__(self, api_key):
        super().__init__()
        self.mistral_client = Mistral(api_key=api_key)

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_name,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs) -> CompletionResponse:
        messages = [{"role": "user", "content": prompt}]
        chat_response = self.mistral_client.chat.complete(
            model="mistral-large-latest", messages=messages
        )
        response_text = chat_response.choices[0].message.content
        return CompletionResponse(text=response_text)

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs) -> CompletionResponseGen:
        messages = [{"role": "user", "content": prompt}]
        chat_response = self.mistral_client.chat.stream_complete(
            model="mistral-large-latest", messages=messages
        )
        response = ""
        for token in chat_response:
            response += token
            yield CompletionResponse(text=response, delta=token)

# this agent iterates over the directory, generates summary for the available documents.
class SummaryAgent:
    def __init__(self, api_key):
        self.llm = MistralLLM(api_key=api_key)
        self.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-large-en-v1.5",
            # model_kwargs=model_kwargs
        )
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model

    # generates summary for each single document in a particular directory
    def generate_summaries(self, input_dir="/content/output/"):
        splitter = SentenceSplitter(chunk_size=1024)
        file_doc_map = (
            []
        )  # contains tuples of "doc_id" and "file_paths" - (doc_id, file_path)
        for i in os.walk(input_dir):
            if i[2]:
                full_file_path = i[0] + "/" + i[2][0]
                doc_id = i[0].split("/")[-1] + "_" + i[2][0].split(".")[0]
                doc_map = (doc_id, full_file_path)
                file_doc_map.append(doc_map)
        final_docs = []
        for i in file_doc_map:
            docs = SimpleDirectoryReader(input_files=[i[1]]).load_data()
            docs[0].doc_id = i[0]
            final_docs.extend(docs)
        response_synthesizer = get_response_synthesizer(
            response_mode="tree_summarize", use_async=True
        )
        doc_summary_index = DocumentSummaryIndex.from_documents(
            final_docs,
            llm=self.llm,
            transformations=[splitter],
            response_synthesizer=response_synthesizer,
            show_progress=True,
            summary_query =  "Provide a detailed summary of the document with detailed steps and divisions.",
        )
        return doc_summary_index, file_doc_map


### Example Usage ###
# agent = SummaryAgent(api_key = "") - Enter your Mistral API Key
# index,map = agent.generate_summaries(input_dir = "") - Enter your input directory
# print(index.get_document_summary(map[1][0]))

### Note ###
## walks over the directory and reads only the text files,
## the directory looks something like this 
    ## output
    ##    |_ microsoftforum
    ##                     |_0.txt
    ##                     |_1.txt
    ##   |_ reddit
    ##           |_0.txt