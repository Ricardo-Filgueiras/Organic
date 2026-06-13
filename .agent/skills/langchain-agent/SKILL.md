---
name: langchain-agent
description: Use when creating or editing a LangChain agent (tools, middleware, agent scripts/notebooks) in this repo, so the code follows the same conventions used across the course modules (Personal Chef, Wedding Planner, Email Assistant).
---

# LangChain Agent (course conventions)

Follow these conventions, taken from `notebooks/module-1/1.5_personal_chef.py` and `notebooks/module-3/3.5_email_agent.py`, when writing or modifying agent code in this repo.

## File setup

- Always start agent scripts/notebooks with:
  ```python
  from dotenv import load_dotenv
  load_dotenv()
  ```
- Default model is `"gpt-5-nano"` unless the lesson specifically compares providers (Module 1, Lesson 1 only).
- Build agents with `create_agent` from `langchain.agents`:
  ```python
  from langchain.agents import create_agent

  agent = create_agent(
      model="gpt-5-nano",
      tools=[...],
      system_prompt=system_prompt,
  )
  ```
- The module-level variable must be named `agent` — it is the entry point referenced by `langgraph.json` (`graphs.agent`).

## Tools

- Define tools with `@tool` from `langchain.tools`, and always give them a clear docstring (it becomes the tool description the model sees):
  ```python
  from langchain.tools import tool

  @tool
  def web_search(query: str) -> Dict[str, Any]:
      """Search the web for information"""
      return tavily_client.search(query)
  ```
- For tools that need to read shared/auth context, accept a `runtime: ToolRuntime` parameter and read `runtime.context`.
- For tools that need to update agent state (not just return a message), return a `langgraph.types.Command` with an `update` dict, including a `ToolMessage` keyed to `runtime.tool_call_id`:
  ```python
  from langgraph.types import Command
  from langchain.messages import ToolMessage

  @tool
  def authenticate(email: str, password: str, runtime: ToolRuntime) -> Command:
      """Authenticate the user with the given email and password"""
      if email == runtime.context.email_address and password == runtime.context.password:
          return Command(update={
              "authenticated": True,
              "messages": [ToolMessage("Successfully authenticated", tool_call_id=runtime.tool_call_id)],
          })
  ```

## State and context

- If the agent needs extra state fields, subclass `AgentState` from `langchain.agents` (e.g. `AuthenticatedState(AgentState)` with an `authenticated: bool` field) and pass it via `create_agent`'s state schema.
- If the agent needs runtime configuration (credentials, settings), define a `@dataclass` (e.g. `EmailContext`) and pass it as the runtime context.

## Middleware

- Use middleware from `langchain.agents.middleware` for cross-cutting behavior:
  - `wrap_model_call` — intercept/modify model requests and responses (`ModelRequest`, `ModelResponse`).
  - `dynamic_prompt` — compute the system prompt at runtime based on state/context.
  - `HumanInTheLoopMiddleware` — pause for human approval before sensitive tool calls.
- Keep middleware functions small and composable; pass them via the `middleware=[...]` argument to `create_agent`.

## System prompts

- Write system prompts as plain triple-quoted strings, describing the agent's role and how to use its tools (see `system_prompt` in `1.5_personal_chef.py`).

## Notebook vs. script versions

- Lessons with a Studio-runnable capstone (Module 1's Personal Chef, Module 3's Email Assistant) have both a `.ipynb` and a `.py` file. When changing the agent's behavior, update **both** so they stay in sync.
- The `.py` file is the one referenced by that module's `langgraph.json` (`./<name>.py:agent`) — `uv run langgraph dev` from inside `notebooks/module-1/` or `notebooks/module-3/` loads it.

## Environment

- Required keys come from the repo-root `.env` (copied from `example.env`): `OPENAI_API_KEY`, `TAVILY_API_KEY` for web search, plus optional `LANGSMITH_*` for tracing.
- `langgraph.json` files point `env` at `../../.env` — don't create per-module `.env` files.
