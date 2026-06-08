"""
app.py — Gradio chat interface for the Job Search Assistant.

Each browser session gets a unique thread_id so LangGraph's MemorySaver
keeps conversations separate across users.
"""

import uuid
import gradio as gr
from agent import chat

# ---------------------------------------------------------------------------
# Core response function — called by Gradio on every user message
# ---------------------------------------------------------------------------

def respond(message: str, history: list, thread_id: str) -> str:
    """
    Receives the user's message and the current thread_id,
    calls the LangGraph agent, and returns the assistant's reply.

    'history' is managed by Gradio for display only — actual memory
    lives inside LangGraph's MemorySaver, keyed by thread_id.
    """
    return chat(message, thread_id)


# ---------------------------------------------------------------------------
# Gradio UI layout
# ---------------------------------------------------------------------------

with gr.Blocks(title="Job Search Assistant") as demo:

    # Session state — holds a unique thread_id per browser session
    # This is invisible to the user but persists across messages in one session
    thread_id_state = gr.State(value=lambda: str(uuid.uuid4()))

    gr.Markdown(
        """
        # Job Search Assistant
        Ask me about job listings, salary ranges, or paste a job description to summarize.
        """
    )

    gr.Markdown(
        """
        **Try asking:**
        - *Find me remote Python developer jobs*
        - *What is the average salary for a data scientist?*
        - *Paste a job description and say: summarize this*
        """
    )

    chat_interface = gr.ChatInterface(
        fn=respond,
        additional_inputs=[thread_id_state],
        textbox=gr.Textbox(
            placeholder="Ask about jobs, salaries, or paste a job description...",
            container=False,
        ),
    )

# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo.launch()
