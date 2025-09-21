import arxiv
import json
import os
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

PAPER_DIR = "papers"

# Initialize FastMCP server
mcp = FastMCP("research")

@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.
    Enhanced for pharmaceutical research with focus on active ingredients.

    Args:
        topic: The topic to search for (drug name, active ingredient, or condition)
        max_results: Maximum number of results to retrieve (default: 5)

    Returns:
        List of paper IDs found in the search
    """
    
    # Use arxiv to find the papers 
    client = arxiv.Client()

    # Enhanced search query for pharmaceutical research
    # Add relevant medical/pharmaceutical keywords to improve search results
    enhanced_query = f"{topic} AND (efficacy OR safety OR clinical OR pharmacology OR therapeutic OR adverse OR side effects)"

    # Search for the most relevant articles matching the queried topic
    search = arxiv.Search(
        query = enhanced_query,
        max_results = max_results,
        sort_by = arxiv.SortCriterion.Relevance
    )

    papers = client.results(search)
    
    # Create directory for this topic
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    
    file_path = os.path.join(path, "papers_info.json")

    # Try to load existing papers info
    try:
        with open(file_path, "r") as json_file:
            papers_info = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        papers_info = {}

    # Process each paper and add to papers_info  
    paper_ids = []
    for paper in papers:
        paper_ids.append(paper.get_short_id())
        paper_info = {
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'summary': paper.summary,
            'pdf_url': paper.pdf_url,
            'published': str(paper.published.date())
        }
        papers_info[paper.get_short_id()] = paper_info
    
    # Save updated papers_info to json file
    with open(file_path, "w") as json_file:
        json.dump(papers_info, json_file, indent=2)
    
    print(f"Results are saved in: {file_path}")
    
    return paper_ids

@mcp.tool()
def extract_info(paper_id: str) -> str:
    """
    Search for information about a specific paper across all topic directories.
    
    Args:
        paper_id: The ID of the paper to look for
        
    Returns:
        JSON string with paper information if found, error message if not found
    """
 
    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as json_file:
                        papers_info = json.load(json_file)
                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=2)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error reading {file_path}: {str(e)}")
                    continue
    
    return f"There's no saved information related to paper {paper_id}."

@mcp.tool()
def research_active_ingredient(ingredient_name: str, research_focus: str = "safety and efficacy") -> Dict[str, Any]:
    """
    Research a specific active ingredient with focus on pharmaceutical properties.

    Args:
        ingredient_name: Name of the active ingredient (e.g., "acetaminophen", "ibuprofen")
        research_focus: Specific aspect to research (safety, efficacy, interactions, etc.)

    Returns:
        Comprehensive research summary about the active ingredient
    """

    # Search for papers about this specific ingredient
    search_query = f"{ingredient_name} {research_focus}"
    paper_ids = search_papers(search_query, max_results=3)

    # Compile research findings
    research_summary = {
        "ingredient": ingredient_name,
        "research_focus": research_focus,
        "papers_found": len(paper_ids),
        "paper_ids": paper_ids,
        "key_findings": [],
        "safety_profile": "",
        "efficacy_data": "",
        "contraindications": []
    }

    # Add known pharmaceutical information (in real implementation, this would
    # extract from papers or medical databases)
    if "acetaminophen" in ingredient_name.lower():
        research_summary["safety_profile"] = "Generally safe when used as directed. Maximum daily dose: 3000-4000mg. Hepatotoxic in overdose."
        research_summary["efficacy_data"] = "Effective analgesic and antipyretic. Onset: 30-60 minutes. Duration: 4-6 hours."
        research_summary["contraindications"] = ["Severe liver disease", "Alcohol dependence"]

    elif "ibuprofen" in ingredient_name.lower():
        research_summary["safety_profile"] = "NSAID with anti-inflammatory properties. GI and cardiovascular risks with long-term use."
        research_summary["efficacy_data"] = "Effective for pain, inflammation, and fever. Onset: 20-30 minutes. Duration: 4-6 hours."
        research_summary["contraindications"] = ["Active GI bleeding", "Severe heart failure", "Third trimester pregnancy"]

    elif "loratadine" in ingredient_name.lower():
        research_summary["safety_profile"] = "Non-sedating antihistamine. Minimal side effects. Safe for long-term use."
        research_summary["efficacy_data"] = "Effective for allergic rhinitis and urticaria. Onset: 1-3 hours. Duration: 24 hours."
        research_summary["contraindications"] = ["Known hypersensitivity"]

    return research_summary

@mcp.tool()
def analyze_drug_interactions(ingredients: List[str]) -> Dict[str, Any]:
    """
    Analyze potential interactions between multiple active ingredients.

    Args:
        ingredients: List of active ingredient names to check for interactions

    Returns:
        Interaction analysis with warnings and recommendations
    """

    interactions = {
        "ingredients_analyzed": ingredients,
        "potential_interactions": [],
        "warnings": [],
        "recommendations": []
    }

    # Check for known problematic combinations
    ingredient_set = set(ing.lower() for ing in ingredients)

    # NSAIDs + other NSAIDs
    nsaids = {"ibuprofen", "naproxen", "aspirin", "diclofenac"}
    nsaid_count = len(ingredient_set.intersection(nsaids))
    if nsaid_count > 1:
        interactions["potential_interactions"].append({
            "type": "Increased NSAID exposure",
            "severity": "Moderate to High",
            "description": "Multiple NSAIDs increase risk of GI bleeding and kidney damage"
        })
        interactions["warnings"].append("Avoid combining multiple NSAIDs")

    # Acetaminophen + alcohol warning
    if "acetaminophen" in ingredient_set:
        interactions["warnings"].append("Limit alcohol consumption - increases liver toxicity risk")

    # Sedating antihistamines + other sedating drugs
    sedating_antihistamines = {"diphenhydramine", "chlorpheniramine", "doxylamine"}
    if ingredient_set.intersection(sedating_antihistamines):
        interactions["warnings"].append("May cause drowsiness - avoid driving or operating machinery")

    if not interactions["potential_interactions"]:
        interactions["recommendations"].append("No major interactions identified between these ingredients")

    return interactions



@mcp.resource("papers://folders")
def get_available_folders() -> str:
    """
    List all available topic folders in the papers directory.
    
    This resource provides a simple list of all available topic folders.
    """
    folders = []
    
    # Get all topic directories
    if os.path.exists(PAPER_DIR):
        for topic_dir in os.listdir(PAPER_DIR):
            topic_path = os.path.join(PAPER_DIR, topic_dir)
            if os.path.isdir(topic_path):
                papers_file = os.path.join(topic_path, "papers_info.json")
                if os.path.exists(papers_file):
                    folders.append(topic_dir)
    
    # Create a simple markdown list
    content = "# Available Topics\n\n"
    if folders:
        for folder in folders:
            content += f"- {folder}\n"
        content += f"\nUse @{folder} to access papers in that topic.\n"
    else:
        content += "No topics found.\n"
    
    return content

@mcp.resource("papers://{topic}")
def get_topic_papers(topic: str) -> str:
    """
    Get detailed information about papers on a specific topic.
    
    Args:
        topic: The research topic to retrieve papers for
    """
    topic_dir = topic.lower().replace(" ", "_")
    papers_file = os.path.join(PAPER_DIR, topic_dir, "papers_info.json")
    
    if not os.path.exists(papers_file):
        return f"# No papers found for topic: {topic}\n\nTry searching for papers on this topic first."
    
    try:
        with open(papers_file, 'r') as f:
            papers_data = json.load(f)
        
        # Create markdown content with paper details
        content = f"# Papers on {topic.replace('_', ' ').title()}\n\n"
        content += f"Total papers: {len(papers_data)}\n\n"
        
        for paper_id, paper_info in papers_data.items():
            content += f"## {paper_info['title']}\n"
            content += f"- **Paper ID**: {paper_id}\n"
            content += f"- **Authors**: {', '.join(paper_info['authors'])}\n"
            content += f"- **Published**: {paper_info['published']}\n"
            content += f"- **PDF URL**: [{paper_info['pdf_url']}]({paper_info['pdf_url']})\n\n"
            content += f"### Summary\n{paper_info['summary'][:500]}...\n\n"
            content += "---\n\n"
        
        return content
    except json.JSONDecodeError:
        return f"# Error reading papers data for {topic}\n\nThe papers data file is corrupted."

@mcp.prompt()
def generate_search_prompt(topic: str, num_papers: int = 5) -> str:
    """Generate a prompt for Claude to find and discuss academic papers on a specific topic."""
    return f"""Search for {num_papers} academic papers about '{topic}' using the search_papers tool.

Follow these instructions:
1. First, search for papers using search_papers(topic='{topic}', max_results={num_papers})
2. For each paper found, extract and organize the following information:
   - Paper title
   - Authors
   - Publication date
   - Brief summary of the key findings
   - Main contributions or innovations
   - Methodologies used
   - Relevance to the topic '{topic}'

3. Provide a comprehensive summary that includes:
   - Overview of the current state of research in '{topic}'
   - Common themes and trends across the papers
   - Key research gaps or areas for future investigation
   - Most impactful or influential papers in this area

4. Organize your findings in a clear, structured format with headings and bullet points for easy readability.

Please present both detailed information about each paper and a high-level synthesis of the research landscape in {topic}."""

@mcp.prompt()
def pharmaceutical_analysis_prompt(active_ingredients: List[str], condition: str) -> str:
    """Generate a prompt for comprehensive pharmaceutical analysis of active ingredients for a specific condition."""
    ingredients_str = ", ".join(active_ingredients)

    return f"""As a pharmaceutical research assistant, conduct a comprehensive analysis of the following active ingredients for treating {condition}:

Active Ingredients to Research: {ingredients_str}

Please follow this systematic approach:

1. **Individual Ingredient Analysis**
   For each ingredient ({ingredients_str}):
   - Use research_active_ingredient() to gather safety and efficacy data
   - Summarize mechanism of action
   - Identify optimal dosing and duration
   - Note contraindications and warnings

2. **Comparative Effectiveness**
   - Compare efficacy profiles for treating {condition}
   - Identify which ingredients work best for specific symptoms
   - Note onset and duration differences

3. **Safety Assessment**
   - Use analyze_drug_interactions() to check for interactions between ingredients
   - Identify patient populations who should avoid each ingredient
   - Highlight important safety warnings

4. **Evidence-Based Recommendations**
   - Rank ingredients by strength of evidence for {condition}
   - Provide clear recommendations with rationale
   - Include when to recommend seeking professional medical care

5. **Patient Education Points**
   - Key points patients should know about each ingredient
   - Proper usage instructions
   - When to discontinue use

Present your analysis in a professional, evidence-based format suitable for patient counseling."""

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')