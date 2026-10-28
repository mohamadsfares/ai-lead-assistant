# Cedar Ridge AI Assistant

An AI assistant for a home-improvement company that answers website visitors from the company's own documents, cites its sources, hands over to a human when it doesn't know, and turns each conversation into a structured lead record.

> Cedar Ridge Roofing & Renovation (Columbus, Ohio) is a fictional company used as demo data. The code is company-agnostic.

## Problem
Home-improvement companies get website visitors at all hours asking the same questions: service areas, price ranges, financing, warranties. Slow answers lose leads to competitors, and the sales team wastes time on visitors who are outside the service area or not ready to buy.

## Aim
- Answer visitor questions **only** from company documents, with **citations**
- **Refuse or hand over to a human** when the documents don't contain the answer
- Produce a **Pydantic-validated JSON lead summary** (service, location, budget, urgency, qualified)
- Log **tokens, cost and latency** for every request
- Measure quality with an **evaluation set** of ~40 questions
- Serve it as a **FastAPI** service (used by an n8n automation in project 4) with a **Streamlit** chat demo

## Status
🚧 In progress: session 1 (setup + knowledge base)