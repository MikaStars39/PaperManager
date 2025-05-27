from typing import List, Dict
import csv
import re
import os
from urllib.parse import urlparse
from .api import call_openrouter
from .prompts import general_prompt
from .config import ConfigManager

class PaperManager:
    def __init__(
        self, 
        config_manager: ConfigManager = None,
        csv_file: str = None, 
        api_key: str = None, 
        paper_types: List[str] = None,
        model: str = None
    ):
        # Use config manager or create default one
        self.config_manager = config_manager or ConfigManager()
        
        # Override config with provided parameters
        self.csv_file = csv_file or self.config_manager.csv_file
        self.api_key = api_key or self.config_manager.api_key
        self.model = model or self.config_manager.api_model
        self.paper_types = paper_types or self.config_manager.paper_types
        
        self.papers = []
        self.conversation = []
        
        self.load_papers()
        self._initialize_csv()
    
    def load_papers(self):
        """Load existing papers from CSV file"""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.papers = list(reader)
        except FileNotFoundError:
            self.papers = []
    
    def _initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['title', 'keywords', 'url', 'type'])
    
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
                writer = csv.DictWriter(file, fieldnames=['title', 'keywords', 'url', 'type'])
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
    
    def get_papers_summary(self) -> str:
        """Get a summary of all papers for context"""
        if not self.papers:
            return "No papers in the database."
        
        summary = f"Current papers in database ({len(self.papers)} total):\n"
        for i, paper in enumerate(self.papers[:10], 1):  # Show first 10
            summary += f"{i}. {paper['title']} ({paper['type']})\n"
        
        if len(self.papers) > 10:
            summary += f"... and {len(self.papers) - 10} more papers."
        
        return summary
    
    def chat(self, prompt: str) -> str:
        """Main chat interface"""
        # Add context about current papers
        context = f"{general_prompt}\n\nCurrent database status:\n{self.get_papers_summary()}\n\nUser: {prompt}"
        
        # Call LLM with config parameters
        self.conversation, response = call_openrouter(
            context, 
            self.api_key, 
            self.model,
            temperature=self.config_manager.api_temperature,
            max_tokens=self.config_manager.api_max_tokens,
            conversation=self.conversation
        )
        
        if response is None:
            return "Sorry, I couldn't process your request. Please check your API key."
        
        # Parse and execute any paper operations
        papers_to_add = self.parse_paper(response)
        
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
                response += f"\n\n✅ Successfully added {added_count} paper(s) to the database."
        
        return response