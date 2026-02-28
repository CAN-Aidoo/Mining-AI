"""
Prototype Builder service.

Uses Claude to generate complete, runnable Gradio applications
based on the prototype type and user description.
"""

import logging

import anthropic

from app.config import get_settings
from app.models.prototype import Prototype

logger = logging.getLogger(__name__)
settings = get_settings()

# ---------------------------------------------------------------------------
# Prompt templates per prototype type
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are an expert Python developer. Generate a complete, runnable Gradio application. "
    "The code must:\n"
    "1. Be syntactically correct Python 3.10+\n"
    "2. Include all necessary imports\n"
    "3. Use Gradio 4.x API (`import gradio as gr`)\n"
    "4. Include a `if __name__ == '__main__': demo.launch()` block\n"
    "5. Have inline comments explaining key steps\n"
    "6. Handle errors gracefully\n\n"
    "Return ONLY the Python code — no markdown fences, no explanation."
)

_REQUIREMENTS_BASE = "gradio>=4.0.0\n"

_TYPE_PROMPTS: dict[str, tuple[str, str]] = {
    "classifier": (
        "Build a text classification Gradio app. "
        "Include: (1) a Training tab where the user pastes CSV data with 'text' and 'label' columns "
        "and trains a scikit-learn TF-IDF + LogisticRegression pipeline, "
        "(2) a Prediction tab where the user types text and gets the predicted class with confidence. "
        "Use gr.Tabs, gr.Textbox, gr.Dataframe, gr.Label.",
        _REQUIREMENTS_BASE + "scikit-learn>=1.3.0\npandas>=2.0.0\n",
    ),
    "recommender": (
        "Build a content-based recommendation Gradio app. "
        "Include: (1) a Dataset tab to paste CSV data with 'id', 'title', and 'description' columns, "
        "(2) a Recommend tab where the user types a query and gets the top-5 most similar items "
        "using TF-IDF cosine similarity. Display results in a gr.Dataframe.",
        _REQUIREMENTS_BASE + "scikit-learn>=1.3.0\npandas>=2.0.0\n",
    ),
    "chatbot": (
        "Build a chatbot Gradio app using the Anthropic API. "
        "The user types messages into a gr.ChatInterface. Each message is sent to claude-haiku-4-5-20251001 "
        "via the anthropic Python SDK (ANTHROPIC_API_KEY from environment). "
        "Maintain conversation history. Handle API errors gracefully with a friendly error message.",
        _REQUIREMENTS_BASE + "anthropic>=0.40.0\n",
    ),
    "text_tool": (
        "Build a text analysis Gradio app with three tabs: "
        "(1) Summarisation — takes long text and returns a bullet-point summary using basic NLP, "
        "(2) Keyword Extraction — returns top keywords using TF-IDF, "
        "(3) Readability — returns Flesch reading ease score and grade level. "
        "Use only standard libraries + scikit-learn + textstat.",
        _REQUIREMENTS_BASE + "scikit-learn>=1.3.0\ntextstat>=0.7.0\n",
    ),
    "dashboard": (
        "Build a data dashboard Gradio app. "
        "Include: (1) a Data tab where the user uploads a CSV file, "
        "(2) a Charts tab showing: bar chart of value counts for the first categorical column, "
        "histogram of the first numeric column, correlation heatmap. "
        "Use Plotly for all charts (gr.Plot). Handle files with up to 10 000 rows.",
        _REQUIREMENTS_BASE + "plotly>=5.0.0\npandas>=2.0.0\n",
    ),
}


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

async def generate_prototype_code(prototype: Prototype) -> tuple[str, str]:
    """
    Generate a complete Gradio application for the prototype.
    Returns (python_code, requirements_txt).
    """
    if not settings.ANTHROPIC_API_KEY:
        placeholder = (
            "# ANTHROPIC_API_KEY not configured.\n"
            "# Set it in your .env to enable AI prototype generation.\n\n"
            "import gradio as gr\n\n"
            "with gr.Blocks() as demo:\n"
            "    gr.Markdown('# Prototype placeholder')\n"
            "    gr.Markdown('Configure ANTHROPIC_API_KEY and rebuild.')\n\n"
            "if __name__ == '__main__':\n"
            "    demo.launch()\n"
        )
        return placeholder, "gradio>=4.0.0\n"

    type_prompt, requirements = _TYPE_PROMPTS.get(
        prototype.prototype_type,
        (
            f"Build a general-purpose Gradio app for: {prototype.description}",
            _REQUIREMENTS_BASE,
        ),
    )

    user_message = (
        f"Project: {prototype.title}\n"
        f"Type: {prototype.prototype_type}\n"
        f"Description: {prototype.description}\n"
        f"Input/Data context: {prototype.input_description}\n\n"
        f"Task: {type_prompt}"
    )

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=4096,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    code = message.content[0].text.strip()

    # Strip accidental markdown fences
    if code.startswith("```"):
        lines = code.split("\n")
        code = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

    return code, requirements
