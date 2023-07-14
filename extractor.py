from typing import Any, Dict, List
import os
import re
import hashlib

from pypdf import PdfReader

from transformers import AutoTokenizer


class PdfExtractor:
    """Extract text from pdf documents and create text chunks for embedding model."""

    def __init__(self, embedding_model_name, max_chunk_size):
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model_name)
        self.max_chunk_size = max_chunk_size

    def extract_and_chunk(self, path: str) -> List[Dict[str, Any]]:
        data = []

        with open(path, "rb") as f:
            pdf_reader = PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                text_list = self._split_text(text)
                chunks = self._create_chunks(
                    text_list, self.max_chunk_size, page_num, self._get_source(path)
                )
                data.extend(chunks)

        return data

    def _create_chunks(self, text_list, max_size, page_number, source):
        """Function to create text chunks from a page."""

        chunks = []
        chunk = ""
        chunk_number = 0
        for sentence in text_list:
            new_chunk = chunk + "\n" + sentence if chunk else sentence
            new_chunk_size = len(self.tokenizer.encode(new_chunk))
            if new_chunk_size <= max_size:
                chunk = new_chunk
            else:
                chunks.append(
                    self._format_chunk(chunk, chunk_number, page_number, source)
                )
                chunk = sentence
                chunk_number += 1
        if chunk:
            chunks.append(self._format_chunk(chunk, chunk_number, page_number, source))
        return chunks

    @staticmethod
    def _format_chunk(
        text: str, chunk_number: int, page_number: int, source: str
    ) -> Dict[str, Any]:
        chunk = {}

        # For creating unique id of text chunk
        m = hashlib.md5()
        m.update(f"{source}-{page_number}-{chunk_number}".encode("utf-8"))
        uid = m.hexdigest()[:12]

        chunk["id"] = uid
        chunk["text"] = text
        metadata = {}
        metadata["chunk_number"] = chunk_number
        # pypdf indexes pages starting from 0
        metadata["page_number"] = page_number + 1
        metadata["source"] = source

        chunk["metadata"] = metadata

        return chunk

    @staticmethod
    def _split_text(text: str) -> List[str]:
        """Function to split text into elements based on newline characters."""

        # Split text based on occurence of one or more newline characters with zero or more spaces on et
        text_list = re.split(r"\s*\n\s*", text)

        # Remove leading and trailing whitespaces
        text_list = [s.strip() for s in text_list]

        # Remove empty strings
        text_list = [s for s in text_list if s != ""]

        return text_list

    @staticmethod
    def _get_source(path: str) -> str:
        dirname = os.path.basename(os.path.dirname(path))
        basename = os.path.splitext(os.path.basename(path))[0]
        return f"{dirname}-{basename}"
