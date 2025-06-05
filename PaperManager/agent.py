from typing import List, Dict, Generator
import csv
import re
import os
from urllib.parse import urlparse
from .api import call_openrouter, call_openrouter_stream
from .prompts import general_prompt
from .config import Config
from .hfd import upload_to_hf

ROW_TYPE = ["title", "keywords", "url", "type"]

def split_into_types(main_folder: str, types: List[str]):
    """Split papers from main folder into type-specific folders.
    
    Args:
        main_folder (str): Path to the main folder containing all papers (e.g., data/all)
        types (List[str]): List of paper types to split into (e.g., ["efficiency", "interpretability"])
    """
    try:
        main_folder = os.path.join(main_folder, "all")
        # Ensure main folder exists
        if not os.path.exists(main_folder):
            print(f"Main folder {main_folder} does not exist.")
            return False
            
        # Read the CSV file from main folder
        main_csv = os.path.join(main_folder, "papers.csv")
        print(f"Reading CSV file from {main_csv}")
            
        # Read all papers
        papers_by_type = {}
        with open(main_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for paper in reader:
                paper_type = paper['type'].lower()
                if paper_type not in papers_by_type:
                    papers_by_type[paper_type] = []
                papers_by_type[paper_type].append(paper)
        
        # Create type folders and save papers
        base_dir = os.path.dirname(main_folder)
        for paper_type in types:
            type_folder = os.path.join(base_dir, paper_type.lower())
            os.makedirs(type_folder, exist_ok=True)
            
            # Create CSV file for this type
            type_csv = os.path.join(type_folder, "papers.csv")
            papers = papers_by_type.get(paper_type.lower(), [])
            
            with open(type_csv, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=ROW_TYPE)
                writer.writeheader()
                writer.writerows(papers)
                
        return True
    except Exception as e:
        print(f"Error splitting papers: {str(e)}")
        return False

class PaperManager:
    def __init__(
        self, 
        config: Config = None,
        csv_file: str = None,
        api_key: str = None
    ):
        # Use provided config or create default one
        self.config = config or Config()
        
        # Override config with provided parameters if given
        if csv_file:
            self.config.csv_file = csv_file
        if api_key:
            self.config.api_key = api_key
            
        self.csv_file = self.config.csv_file
        self.api_key = self.config.api_key
        self.model = self.config.api_model
        self.paper_types = self.config.paper_types
        self.folder = self.config.hf_folder
        self.repo_id = self.config.hf_repo_id
        
        self.papers = []
        self.conversation = []
        
        # initialize papers and csv file
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.papers = list(reader)
        except FileNotFoundError:
            self.papers = []
    
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(ROW_TYPE)
    
    def parse_paper(self, input_text: str) -> List[Dict]:
        """Parse input text into paper details using regex"""
        papers = []
        
        # Find all <add> blocks - improved regex to handle multiple blocks better
        add_blocks = re.findall(r'<add>\s*(.*?)\s*</add>', input_text, re.DOTALL | re.IGNORECASE)
        
        for block in add_blocks:
            paper = {}
            
            # Extract title - more flexible matching
            title_match = re.search(r'Title:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
            if title_match:
                paper['title'] = title_match.group(1).strip()
            
            # Extract URL - more flexible matching
            url_match = re.search(r'URL:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
            if url_match:
                paper['url'] = url_match.group(1).strip()
            
            # Extract keywords - more flexible matching
            keywords_match = re.search(r'Keywords:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
            if keywords_match:
                paper['keywords'] = keywords_match.group(1).strip()
            
            # Extract type - more flexible matching
            type_match = re.search(r'Type:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
            if type_match:
                paper['type'] = type_match.group(1).strip()
            
            # Only add if we have at least title and url
            if 'title' in paper and 'url' in paper:
                papers.append(paper)
            else:
                print(f"Skipping incomplete paper block: {paper}")
        
        print(f"Parsed {len(papers)} papers from {len(add_blocks)} blocks")
        return papers
    
    def extract_arxiv_id(self, title: str) -> str:
        """Extract arXiv ID from title format [arXiv_ID] Title"""
        match = re.search(r'\[(\d{4}\.\d{4,5})\]', title)
        return match.group(1) if match else ""
    
    def add_paper(self, title: str, url: str, keywords: str = "", paper_type: str = ""):
        """Add a single paper to the CSV file"""
        paper = {
            'title': title,
            'keywords': keywords,
            'url': url,
            'type': paper_type
        }
        
        # Extract arXiv ID from the new paper
        new_arxiv_id = self.extract_arxiv_id(title)
        
        # Check if paper already exists (by title or arXiv ID)
        for existing_paper in self.papers:
            # Check by exact title match
            if existing_paper['title'].lower() == title.lower():
                print(f"Paper '{title}' already exists!")
                return False
            
            # Check by arXiv ID if both papers have arXiv IDs
            if new_arxiv_id:
                existing_arxiv_id = self.extract_arxiv_id(existing_paper['title'])
                if existing_arxiv_id and existing_arxiv_id == new_arxiv_id:
                    print(f"Paper with arXiv ID '{new_arxiv_id}' already exists: {existing_paper['title']}")
                    return False
        
        # Add to memory
        self.papers.append(paper)
        
        # Add to CSV file - correct order: title, keywords, url, type
        with open(self.csv_file, 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([title, keywords, url, paper_type])
        
        return True
    
    def delete_paper(self, title: str):
        """Delete a paper by title"""
        original_count = len(self.papers)
        self.papers = [p for p in self.papers if p['title'].lower() != title.lower()]
        
        if len(self.papers) < original_count:
            # Rewrite the entire CSV file
            with open(self.csv_file, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=ROW_TYPE)
                writer.writeheader()
                writer.writerows(self.papers)
            return True
        return False
    
    def search_paper(self, query: str) -> List[Dict]:
        """Search for papers by title or keywords"""
        results = []
        query_lower = query.lower()
        
        for paper in self.papers:
            if (query_lower in paper['title'].lower() or 
                query_lower in paper['keywords'].lower()):
                results.append(paper)
        
        return results
    
    def upload_to_hf(self):
        upload_to_hf(self.folder, self.repo_id, "dataset", self.config.api_key)
        
    def chat_stream(self, prompt: str) -> Generator[str, None, None]:
        """Main chat interface with streaming response"""
        # Add context about current papers
        context = f"{general_prompt}\n\nUser: {prompt}"
        
        # Call LLM with streaming
        full_response = ""
        for chunk in call_openrouter_stream(
            context, 
            self.api_key, 
            self.model,
            temperature=self.config.api_temperature,
            max_tokens=self.config.api_max_tokens,
            conversation=self.conversation.copy()  # Pass a copy to avoid modification during streaming
        ):
            full_response += chunk
            yield chunk
        
        # After streaming is complete, process the full response
        if full_response:
            # Update conversation with the complete response
            self.conversation.append({"role": "user", "content": prompt})
            self.conversation.append({"role": "assistant", "content": full_response})
            
            # Parse and execute any paper operations
            papers_to_add = self.parse_paper(full_response)
            
            if papers_to_add:
                added_count = 0
                for paper in papers_to_add:
                    if self.add_paper(
                        paper.get('title', ''),
                        paper.get('url', ''),
                        paper.get('keywords', ''),
                        paper.get('type', '')
                    ):
                        added_count += 1
                
                if added_count > 0:
                    if split_into_types(self.folder, self.paper_types):
                        success_msg = f"\n\n✅ Successfully split papers by type."
                        yield success_msg
                    else:
                        success_msg = f"\n\n❌ Failed to split papers by type."
                        yield success_msg
                    success_msg = f"\n\n✅ Successfully added {added_count} paper(s) to the database."
                    yield success_msg
                else:
                    success_msg = f"\n\n❌ Failed to add any paper(s) to the database."
                    yield success_msg
                    