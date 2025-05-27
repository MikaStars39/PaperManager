import os
import tempfile
from PaperManager.agent import PaperManager

def test_paper_manager():
    # Create a temporary CSV file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
        temp_csv = temp_file.name
    
    try:
        # Initialize PaperManager
        pm = PaperManager(csv_file=temp_csv, api_key="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")
        
        # Test 1: Add papers manually
        print("Test 1: Adding papers manually")
        success1 = pm.add_paper(
            title="Attention Is All You Need",
            url="https://arxiv.org/abs/1706.03762",
            keywords="transformer, attention, neural networks",
            paper_type="Efficiency"
        )
        print(f"Added paper 1: {success1}")
        
        success2 = pm.add_paper(
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            url="https://arxiv.org/abs/1810.04805",
            keywords="BERT, transformers, NLP",
            paper_type="Interpretability"
        )
        print(f"Added paper 2: {success2}")
        
        # Test 2: Search papers
        print("\nTest 2: Searching papers")
        results = pm.search_paper("attention")
        print(f"Search results for 'attention': {len(results)} papers found")
        for paper in results:
            print(f"  - {paper['title']}")
        
        # Test 3: Parse paper from text
        print("\nTest 3: Parsing papers from text")
        sample_response = """
        I'll add these papers for you:
        
        <add>
            Title: GPT-3: Language Models are Few-Shot Learners
            URL: https://arxiv.org/abs/2005.14165
            Keywords: GPT-3, language models, few-shot learning
            Type: Agent/RL
        </add>
        
        <add>
            Title: Chain-of-Thought Prompting
            URL: https://arxiv.org/abs/2201.11903
            Keywords: reasoning, prompting, chain-of-thought
            Type: Interpretability
        </add>
        """
        
        parsed_papers = pm.parse_paper(sample_response)
        print(f"Parsed {len(parsed_papers)} papers from text")
        for paper in parsed_papers:
            print(f"  - {paper['title']}")
        
        # Test 4: Delete paper
        print("\nTest 4: Deleting paper")
        deleted = pm.delete_paper("BERT: Pre-training of Deep Bidirectional Transformers")
        print(f"Deleted paper: {deleted}")
        
        # Test 5: Get summary
        print("\nTest 5: Papers summary")
        summary = pm.get_papers_summary()
        print(summary)
        
        # Test 6: Chat interface (mock - requires real API key)
        print("\nTest 6: Chat interface (would require real API key)")
        print("Example usage: pm.chat('Add a paper about reinforcement learning from this URL: https://example.com')")
        
    finally:
        # Clean up
        if os.path.exists(temp_csv):
            os.unlink(temp_csv)

if __name__ == "__main__":
    test_paper_manager()