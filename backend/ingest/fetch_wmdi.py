"""
generic_api_insight_agent.py

Prototype agent that can ingest a (structured) API endpoint (REST or data.gouv), load the resulting data into Pandas, and answer natural‑language questions about it.

Author: Alexis GENDRONNEAU (June 2025, forward‑looking prototype)
"""

from __future__ import annotations
import io
import json
import os
import numpy as np
import requests
import pandas as pd
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage

class NpEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

# -----------------------------------------------------------------------------
# 1. Utility helpers for data.gouv.fr datasets
# -----------------------------------------------------------------------------

DGOUV_BASE_V1 = "https://www.data.gouv.fr/api/2"

def get_dataset_metadata(dataset_id: str) -> Dict[str, Any]:
    """
    Return the metadata JSON for a given data.gouv.fr dataset.
    """
    url = f"{DGOUV_BASE_V1}/datasets/{dataset_id}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_resource_download_url(dataset_id: str, format_priority: List[str] = ["csv", "json"]) -> str:
    """
    Pick the first resource whose `format` matches one in `format_priority`
    and return its direct download URL.
    Handles paginated resources from the data.gouv.fr API.
    """
    meta = get_dataset_metadata(dataset_id)
    resources_obj = meta.get("resources")

    # Handle API v2 paginated resources where we must follow a link.
    if isinstance(resources_obj, dict) and "href" in resources_obj:
        resources_url = resources_obj["href"]
        resp = requests.get(resources_url, timeout=30)
        resp.raise_for_status()
        resources_data = resp.json()
        resource_list = resources_data.get("data", [])
    # Handle API v1-style direct resource list.
    elif isinstance(resources_obj, list):
        resource_list = resources_obj
    else:
        resource_list = []

    for fmt in format_priority:
        for res in resource_list:
            # The previous check is kept for robustness.
            if isinstance(res, dict) and res.get("format", "").lower() == fmt:
                return res["url"]
    raise ValueError(f"No resource with format in {format_priority} found.")


def load_dataset_as_dataframe(dataset_id: str) -> pd.DataFrame:
    """
    Download (stream) the first CSV resource found for the dataset
    and load it into a Pandas DataFrame. Falls back to JSON if needed.
    """
    url = get_resource_download_url(dataset_id)
    if url.endswith(".csv"):
        return pd.read_csv(url)
    data = requests.get(url, timeout=30).json()
    return pd.json_normalize(data)

def fetch_all_datasets(limit: int = 100) -> list[dict]:
    """
    Fetch datasets related to "indice de durabilité - Lave-linge" from data.gouv.fr (API v2).
    Supports pagination and limiting the number of results.
    """
    datasets = []
    page = 1
    page_size = min(limit, 100)  # API max page size is 100
    
    # Search specifically for washing machine durability index datasets
    search_query = "indice de durabilité lave-linge"
    
    while len(datasets) < limit:
        url = f"{DGOUV_BASE_V1}/datasets/?q={search_query}&page={page}&page_size={page_size}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        page_datasets = data.get("data", [])
        if not page_datasets:
            break
        datasets.extend(page_datasets)
        if len(page_datasets) < page_size:
            break  # No more pages
        page += 1
    return datasets[:limit]


def fetch_washing_machine_datasets(limit: int = 100) -> list[dict]:
    """
    Fetch all washing machine durability index datasets and their resources.
    Returns a list of datasets with their associated resources.
    """
    datasets = fetch_all_datasets(limit)
    enriched_datasets = []
    
    for dataset in datasets:
        dataset_id = dataset.get("id")
        if not dataset_id:
            continue
            
        try:
            # Get resources for this dataset
            resources_url = f"{DGOUV_BASE_V1}/datasets/{dataset_id}/resources/?page=1&page_size=50"
            resp = requests.get(resources_url, timeout=30)
            resp.raise_for_status()
            resources_data = resp.json()
            resources = resources_data.get("data", [])
            
            # Filter for CSV resources (the main data format for these datasets)
            csv_resources = [r for r in resources if r.get("format", "").lower() == "csv"]
            
            dataset["resources"] = csv_resources
            enriched_datasets.append(dataset)
            
        except Exception as e:
            print(f"Error fetching resources for dataset {dataset_id}: {e}")
            continue
    
    return enriched_datasets


def load_washing_machine_data(dataset_id: str, resource_id: str = None) -> pd.DataFrame:
    """
    Load washing machine durability data from a specific dataset and optionally a specific resource.
    If no resource_id is provided, loads the first available CSV resource.
    """
    try:
        if resource_id:
            # Load specific resource
            resource_url = f"{DGOUV_BASE_V1}/resources/{resource_id}/"
            resp = requests.get(resource_url, timeout=30)
            resp.raise_for_status()
            resource_data = resp.json()
            url = resource_data.get("url")
        else:
            # Load first available CSV resource
            url = get_resource_download_url(dataset_id, format_priority=["csv"])
        
        if url and url.endswith(".csv"):
            # Handle semicolon-separated CSV files (common in French datasets)
            # Try different encodings for French text
            for encoding in ['latin-1', 'iso-8859-1', 'cp1252', 'utf-8']:
                try:
                    return pd.read_csv(url, sep=';', encoding=encoding)
                except UnicodeDecodeError:
                    continue
            # If all encodings fail, try with error handling
            return pd.read_csv(url, sep=';', encoding='latin-1', errors='replace')
        else:
            raise ValueError(f"No valid CSV resource found for dataset {dataset_id}")
            
    except Exception as e:
        raise ValueError(f"Failed to load dataset {dataset_id}: {e}")


def get_washing_machine_datasets_summary() -> dict:
    """
    Get a summary of all available washing machine durability datasets.
    """
    datasets = fetch_washing_machine_datasets()
    
    summary = {
        "total_datasets": len(datasets),
        "datasets": []
    }
    
    for dataset in datasets:
        dataset_summary = {
            "id": dataset.get("id"),
            "title": dataset.get("title"),
            "description": dataset.get("description"),
            "organization": dataset.get("organization", {}).get("name", "Unknown"),
            "resource_count": len(dataset.get("resources", [])),
            "resources": [
                {
                    "id": r.get("id"),
                    "title": r.get("title"),
                    "format": r.get("format"),
                    "url": r.get("url")
                }
                for r in dataset.get("resources", [])
            ]
        }
        summary["datasets"].append(dataset_summary)
    
    return summary


def download_all_washing_machine_data_raw(output_dir: str = "backend/data/raw") -> dict:
    """
    Download all washing machine durability datasets as raw CSV files.
    
    Args:
        output_dir: Directory to save the raw CSV files
        
    Returns:
        dict: Summary of downloaded datasets with file paths
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all washing machine datasets
    datasets = fetch_washing_machine_datasets()
    
    download_summary = {
        "total_datasets": len(datasets),
        "downloaded": [],
        "failed": []
    }
    
    print(f"Found {len(datasets)} washing machine datasets to download...")
    
    for dataset in datasets:
        dataset_id = dataset.get("id")
        dataset_title = dataset.get("title", "Unknown")
        
        if not dataset_id:
            print(f"Skipping dataset without ID: {dataset_title}")
            continue
            
        print(f"\nProcessing dataset: {dataset_title} (ID: {dataset_id})")
        
        try:
            # Get the download URL for the first CSV resource
            download_url = get_resource_download_url(dataset_id, format_priority=["csv"])
            
            # Create filename (sanitize title for filesystem)
            safe_title = "".join(c for c in dataset_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
            filename = f"{dataset_id}_{safe_title}.csv"
            filepath = os.path.join(output_dir, filename)
            
            print(f"  Downloading from: {download_url}")
            print(f"  Saving to: {filepath}")
            
            # Download the file
            response = requests.get(download_url, timeout=60)
            response.raise_for_status()
            
            # Save to file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Verify the file was saved and is readable
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                download_summary["downloaded"].append({
                    "id": dataset_id,
                    "title": dataset_title,
                    "filepath": filepath,
                    "size_bytes": os.path.getsize(filepath),
                    "url": download_url
                })
                print(f"  ✓ Successfully downloaded ({os.path.getsize(filepath)} bytes)")
            else:
                raise Exception("File was not saved properly")
                
        except Exception as e:
            error_msg = f"Failed to download dataset {dataset_id}: {str(e)}"
            print(f"  ✗ {error_msg}")
            download_summary["failed"].append({
                "id": dataset_id,
                "title": dataset_title,
                "error": str(e)
            })
    
    # Print final summary
    print(f"\n{'='*50}")
    print(f"DOWNLOAD SUMMARY:")
    print(f"Total datasets found: {download_summary['total_datasets']}")
    print(f"Successfully downloaded: {len(download_summary['downloaded'])}")
    print(f"Failed downloads: {len(download_summary['failed'])}")
    print(f"Files saved to: {output_dir}")
    
    if download_summary["failed"]:
        print(f"\nFailed downloads:")
        for failed in download_summary["failed"]:
            print(f"  - {failed['title']} (ID: {failed['id']}): {failed['error']}")
    
    return download_summary

# -----------------------------------------------------------------------------
# 2. Core analysis tools
# -----------------------------------------------------------------------------

def quick_insights(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Return a lightweight JSON with common profiling statistics
    (null counts, distinct counts, sample rows, numeric distributions).
    """
    # Only describe numeric columns if they exist.
    numeric_df = df.select_dtypes(include=np.number)
    if not numeric_df.empty:
        try:
            numeric_description = numeric_df.describe().to_dict()
        except Exception:
            numeric_description = {}
    else:
        numeric_description = {}

    # Convert DataFrame head to records, handling any non-serializable objects
    try:
        head_records = df.head().to_dict(orient="records")
        # Convert any non-serializable objects to strings
        for record in head_records:
            for key, value in record.items():
                if not isinstance(value, (str, int, float, bool, type(None))):
                    record[key] = str(value)
    except Exception:
        head_records = []

    # Convert null counts and distinct counts to serializable format
    try:
        null_counts = df.isna().sum().to_dict()
        # Convert any non-serializable keys/values to strings
        null_counts = {str(k): int(v) for k, v in null_counts.items()}
    except Exception:
        null_counts = {}

    try:
        distinct_counts = df.nunique(dropna=False).to_dict()
        # Convert any non-serializable keys/values to strings
        distinct_counts = {str(k): int(v) for k, v in distinct_counts.items()}
    except Exception:
        distinct_counts = {}

    insights = {
        "shape": list(df.shape),  # Convert tuple to list for JSON serialization
        "columns": [str(col) for col in df.columns],  # Ensure all column names are strings
        "head": head_records,
        "describe_numeric": numeric_description,
        "null_counts": null_counts,
        "distinct_counts": distinct_counts,
    }
    return insights

# -----------------------------------------------------------------------------
# 3. LangChain tool wrappers
# -----------------------------------------------------------------------------

def _load_dataset(dataset_id: str) -> str:
    """Load a washing machine dataset and store it in memory, stripping quotes from the ID."""
    global _memory  # store in a module‑level cache for reuse
    # The LLM may pass the ID with quotes, so we strip them.
    clean_id = dataset_id.strip("'\" ")
    df = load_washing_machine_data(clean_id)
    _memory["current_df"] = df
    return f"Loaded washing machine dataset {clean_id} with shape {df.shape}"


def _load_washing_machine_datasets(_: str) -> str:
    """Fetch and return a summary of all available washing machine durability datasets."""
    summary = get_washing_machine_datasets_summary()
    return json.dumps(summary, indent=2, ensure_ascii=False, cls=NpEncoder)


def _summarise_dataset(_: str) -> str:
    df = _memory.get("current_df")
    if df is None:
        return "No dataset is currently loaded."
    insights = quick_insights(df)
    return json.dumps(insights, indent=2, ensure_ascii=False, cls=NpEncoder)

_memory: Dict[str, Any] = {}

tools = [
    Tool(
        name="load_dataset",
        func=_load_dataset,
        description="Load a washing machine durability dataset from data.gouv.fr by its ID. "
                    "Input should be the dataset ID as a string.",
    ),
    Tool(
        name="load_washing_machine_datasets",
        func=_load_washing_machine_datasets,
        description="Fetch and return a summary of all available washing machine durability datasets.",
    ),
    Tool(
        name="summarise_dataset",
        func=_summarise_dataset,
        description="Return JSON with quick statistical insights about the current loaded dataset.",
    ),
    PythonREPLTool(),  # gives raw Python execution if needed
]

# -----------------------------------------------------------------------------
# 4. Build the agent
# -----------------------------------------------------------------------------

def build_agent(llm_temperature: float = 0.0):
    llm = ChatOpenAI(temperature=llm_temperature, model="gpt-4o-mini")
    
    # Construct the ReAct chat prompt manually for robustness.
    system_prompt = (
        "You are a data‑analysis assistant.\n"
        "When asked analytical questions, first check the chat history to see if the required data or context "
        "is already available. Only ask the user for information if you cannot find it in the history or tools.\n"
        "You have access to the following tools:\n\n"
        "{tools}\n\n"
        "Use the following format:\n\n"
        "Question: the input question you must answer\n"
        "Thought: you should always think about what to do\n"
        "Action: the action to take, should be one of [{tool_names}]\n"
        "Action Input: the input to the action\n"
        "Observation: the result of the action\n"
        "... (this Thought/Action/Action Input/Observation can repeat N times)\n"
        "Thought: I now know the final answer\n"
        "Final Answer: the final answer to the original input question"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}"),
        ]
    )

    agent = create_react_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
    )
    return agent_executor


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "download":
        # Download all washing machine datasets as raw files
        print("Starting download of all washing machine datasets...")
        result = download_all_washing_machine_data_raw()
        print(f"\nDownload completed! Check the 'backend/data/raw/' directory for the files.")
    else:
        # Original agent-based functionality
        agent_executor = build_agent()
        chat_history = []

        # --- First turn: Get all washing machine datasets ---
        q1 = "load all washing machine durability datasets"
        result1 = agent_executor.invoke({"input": q1, "chat_history": chat_history})
        print(f"User: {q1}\nAgent: {result1['output']}\n")
        chat_history.extend([
            HumanMessage(content=q1),
            AIMessage(content=result1["output"]),
        ])

        # --- Second turn: Load a specific dataset ---
        q2 = "load the washing machine dataset 6866895d29776719135c922b"
        result2 = agent_executor.invoke({"input": q2, "chat_history": chat_history})
        print(f"User: {q2}\nAgent: {result2['output']}\n")
        chat_history.extend([
            HumanMessage(content=q2),
            AIMessage(content=result2["output"]),
        ])

        # --- Third turn: Analyze the data ---
        q3 = "give me a summary of the washing machine durability data and what the columns mean"
        result3 = agent_executor.invoke({"input": q3, "chat_history": chat_history})
        print(f"User: {q3}\nAgent: {result3['output']}\n")
