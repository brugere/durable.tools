"""
generic_api_insight_agent.py

Prototype agent that can ingest a (structured) API endpoint (REST or data.gouv), load the resulting data into Pandas, and answer natural‑language questions about it.

Author: Alexis GENDRONNEAU (June 2025, forward‑looking prototype)
"""

from __future__ import annotations
import io
import json
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
        numeric_description = numeric_df.describe().to_dict()
    else:
        numeric_description = {}

    insights = {
        "shape": df.shape,
        "columns": list(df.columns),
        "head": df.head().to_dict(orient="records"),
        "describe_numeric": numeric_description,
        "null_counts": df.isna().sum().to_dict(),
        "distinct_counts": df.nunique(dropna=False).to_dict(),
    }
    return insights

# -----------------------------------------------------------------------------
# 3. LangChain tool wrappers
# -----------------------------------------------------------------------------

def _load_dataset(dataset_id: str) -> str:
    """Load a dataset and store it in memory, stripping quotes from the ID."""
    global _memory  # store in a module‑level cache for reuse
    # The LLM may pass the ID with quotes, so we strip them.
    clean_id = dataset_id.strip("'\" ")
    df = load_dataset_as_dataframe(clean_id)
    _memory["current_df"] = df
    return f"Loaded dataset {clean_id} with shape {df.shape}"


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
        description="Load a dataset from data.gouv.fr by its ID. "
                    "Input should be the dataset ID as a string.",
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
    agent_executor = build_agent()
    chat_history = []

    # --- First turn ---
    q1 = "load the data.gouv dataset 684983b11152ff8e46707a5f"
    result1 = agent_executor.invoke({"input": q1, "chat_history": chat_history})
    print(f"User: {q1}\nAgent: {result1['output']}\n")
    chat_history.extend([
        HumanMessage(content=q1),
        AIMessage(content=result1["output"]),
    ])

    # --- Second turn ---
    q2 = "give me a summary of its numeric columns and what they mean"
    result2 = agent_executor.invoke({"input": q2, "chat_history": chat_history})
    print(f"User: {q2}\nAgent: {result2['output']}\n")
