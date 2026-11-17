import streamlit as st
import requests

API_URL = "https://ai-lead-assistant-v79o.onrender.com"

EXAMPLES = [
    "How much does a new roof cost?",
    "Do you serve Dublin, Ohio?",
    "Do you offer financing?",
]

HANDOFF_NOTE = "📞 Want to talk to a person? Call our team at (614) 555-0142."

SAMPLE_QUALIFIED = (
    "Customer: Hi, I'm Sara. I live in Dublin, Ohio and my roof started leaking after last night's storm.\n"
    "Assistant: I'm sorry to hear that! Our team handles storm damage and can help.\n"
    "Customer: Great. My budget is around $12,000. You can call me at 614-555-0101 or email sara@example.com."
)

SAMPLE_NOT_QUALIFIED = (
    "Customer: Hello, I'm Rami from Cincinnati. Do you install solar panels on roofs?\n"
    "Assistant: Sorry, we don't install solar panels.\n"
    "Customer: OK, thanks anyway."
)

LEAD_FIELDS = [
    ("Name", "name"),
    ("Phone", "phone"),
    ("Email", "email"),
    ("Town", "town"),
    ("Service", "service"),
    ("Urgency", "urgency"),
    ("Budget", "budget"),
]


def show_sources(sources):
    with st.expander("Sources"):
        for i, source in enumerate(sources, start=1):
            st.write(f"[{i}] {source}")


def chat_as_text(messages):
    lines = []
    for message in messages:
        speaker = "Customer" if message["role"] == "user" else "Assistant"
        lines.append(f"{speaker}: {message['content']}")
    return "\n".join(lines)


def chat_page():
    # Welcome message (drawn on every run, not saved)
    with st.chat_message("assistant"):
        st.write("Hi! 👋 I'm the Cedar Ridge assistant. Ask me about our roofing and renovation services, prices, service areas, financing or warranties. I answer only from our company documents and show my sources.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message.get("sources"):
                show_sources(message["sources"])
            if message.get("handoff"):
                st.info(HANDOFF_NOTE)

    # Clear chat (only when there are messages)
    if st.session_state.messages:
        if st.button("🗑️ Clear chat"):
            st.session_state.messages = []
            st.rerun()

    # Example question buttons (only before the first question)
    clicked = None
    if not st.session_state.messages:
        for example in EXAMPLES:
            if st.button(example):
                clicked = example

    # New question (typed or clicked)
    question = st.chat_input("Ask a question...", max_chars=1000) or clicked
    if question:
        with st.chat_message("user"):
            st.write(question)
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking... the first answer can take up to a minute."):
                    response = requests.post(f"{API_URL}/chat", json={"question": question}, timeout=120)
                    response.raise_for_status()
                    data = response.json()
                st.write(data["answer"])
                if data["sources"]:
                    show_sources(data["sources"])
                if data["handoff"]:
                    st.info(HANDOFF_NOTE)
                st.session_state.messages.append({"role": "assistant", "content": data["answer"], "sources": data["sources"], "handoff": data["handoff"]})
                st.rerun()
            except requests.exceptions.RequestException:
                st.error("Sorry, the assistant is not available right now. Please try again in a minute.")


def lead_page():
    st.subheader("From chat to qualified lead")
    st.info(
        "🔒 Demo of an internal tool. In production, this runs automatically after each chat "
        "(via an n8n workflow), and only the sales team sees the result."
    )
    st.write(
        "Pick a sample, use your own chat from the Chat assistant page, or paste a conversation. "
        "Claude extracts the lead details with a forced tool call, "
        "Pydantic validates them, and plain Python rules decide if the lead is qualified."
    )

    col1, col2, col3 = st.columns(3)
    if col1.button("Sample: qualified lead"):
        st.session_state.conversation = SAMPLE_QUALIFIED
    if col2.button("Sample: not qualified"):
        st.session_state.conversation = SAMPLE_NOT_QUALIFIED
    if col3.button("💬 Use my chat"):
        if st.session_state.messages:
            st.session_state.conversation = chat_as_text(st.session_state.messages)[-5000:]
        else:
            st.warning("Your chat is empty. Ask a few questions in 💬 Chat assistant first.")

    conversation = st.text_area("Customer conversation", key="conversation", height=180, max_chars=5000)

    if not st.button("🎯 Qualify lead", type="primary"):
        return
    if not conversation.strip():
        st.warning("Please paste a conversation or pick a sample first.")
        return

    try:
        with st.spinner("Extracting the lead... the first request can take up to a minute."):
            response = requests.post(f"{API_URL}/qualify-lead", json={"conversation": conversation}, timeout=120)
            response.raise_for_status()
            result = response.json()
    except requests.exceptions.RequestException:
        st.error("Sorry, the lead qualifier is not available right now. Please try again in a minute.")
        return

    if result["qualified"]:
        st.success("✅ Qualified lead: ready for the sales team")
    else:
        st.error("❌ Not qualified: " + ", ".join(result["reasons"]))

    lead = result["lead"]
    left, right = st.columns(2)
    for i, (label, key) in enumerate(LEAD_FIELDS):
        value = lead.get(key) or "—"
        column = left if i % 2 == 0 else right
        column.markdown(f"**{label}:** {str(value).replace('_', ' ')}")
    st.markdown(f"**Summary:** {lead['summary']}")

    with st.expander("Raw JSON (what the n8n workflow receives)"):
        st.json(result)


st.set_page_config(page_title="Cedar Ridge AI Assistant", page_icon="🏠")

st.title("Cedar Ridge AI Assistant")
st.caption("Ask about our roofing and renovation services, or see how a chat becomes a qualified lead.")

with st.sidebar:
    st.header("About this demo")
    st.markdown(
        "An AI assistant for a home-improvement company. "
        "It answers **only from company documents**, cites its sources, "
        "and hands over to a human when it doesn't know."
    )
    st.markdown(
        "**How it works**\n"
        "- Your question is turned into a vector (OpenAI embeddings)\n"
        "- The 5 most relevant document sections are found in Supabase (pgvector)\n"
        "- Claude Haiku answers from those sections, with citations [n]\n"
        "- Off-topic or unknown questions are handed to the team\n"
        "- Sales team view: a forced tool call fills a Pydantic schema, then Python rules decide"
    )
    st.markdown(
        "**Links**\n"
        "- [Source code on GitHub](https://github.com/mohamadsfares/ai-lead-assistant)\n"
        f"- [API docs]({API_URL}/docs)"
    )
    st.caption("Cedar Ridge Roofing & Renovation is a fictional company used as demo data. The first answer can take up to a minute while the server wakes up.")

# Wake up the server once per visitor
if "woke_up" not in st.session_state:
    try:
        requests.get(f"{API_URL}/health", timeout=2)
    except requests.exceptions.RequestException:
        pass
    st.session_state.woke_up = True

# Chat history (survives reruns)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Pages (menu in the top bar)
pages = [
    st.Page(chat_page, title="Chat assistant", icon="💬"),
    st.Page(lead_page, title="Sales team view", icon="🔒"),
]
page = st.navigation(pages, position="top")
page.run()