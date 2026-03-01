"""
Exa MCP HTTP research tools for live company/news intelligence.

Uses Exa MCP Streamable HTTP endpoint and calls only selected tools:
- web_search_exa
- crawling_exa
- company_research_exa
- deep_researcher_start
- deep_researcher_check
"""

import json
import time
from datetime import datetime
from typing import Any

import requests

from openai_sdk import function_tool
from config import (
    EXA_MCP_HTTP_URL,
    EXA_HTTP_TIMEOUT_SECONDS,
    EXA_DEEP_RESEARCH_TIMEOUT_SECONDS,
    EXA_DEEP_RESEARCH_POLL_INTERVAL_SECONDS,
)


def _normalize_symbol(symbol: str) -> str:
    symbol = symbol.upper().strip()
    for suffix in (".NS", ".BO"):
        if symbol.endswith(suffix):
            return symbol[:-3]
    return symbol


def _to_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False)


class _ExaMcpClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session_id = None

    def _post(self, payload: dict, include_session: bool = True) -> tuple[int, dict, dict]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if include_session and self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        response = self.session.post(
            self.base_url,
            json=payload,
            headers=headers,
            timeout=EXA_HTTP_TIMEOUT_SECONDS,
        )
        raw_headers = dict(response.headers)
        mcp_session = raw_headers.get("Mcp-Session-Id") or raw_headers.get("mcp-session-id")
        if mcp_session:
            self.session_id = mcp_session

        try:
            data = response.json()
        except Exception:
            parsed_event = None
            content_type = response.headers.get("Content-Type", "")
            text_body = response.text or ""
            if "text/event-stream" in content_type or "data:" in text_body:
                events = []
                current_data_lines = []

                def flush_event():
                    nonlocal current_data_lines, events
                    if not current_data_lines:
                        return
                    payload_text = "\n".join(current_data_lines).strip()
                    current_data_lines = []
                    if not payload_text or payload_text == "[DONE]":
                        return
                    try:
                        events.append(json.loads(payload_text))
                    except Exception:
                        pass

                for raw_line in text_body.splitlines():
                    line = raw_line.rstrip("\r")
                    if not line:
                        flush_event()
                        continue
                    if line.startswith("data:"):
                        current_data_lines.append(line[5:].lstrip())

                flush_event()
                if events:
                    parsed_event = events[-1]

            if parsed_event is not None:
                data = parsed_event
            else:
                # Fallback: keep event-stream payload as raw text content instead of hard-failing.
                raw_data_lines = []
                for raw_line in text_body.splitlines():
                    line = raw_line.rstrip("\r")
                    if line.startswith("data:"):
                        payload = line[5:].lstrip()
                        if payload and payload != "[DONE]":
                            raw_data_lines.append(payload)
                if raw_data_lines:
                    data = {
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "\n".join(raw_data_lines)[:50000],
                                }
                            ]
                        }
                    }
                else:
                    data = {
                        "error": {
                            "message": f"Non-JSON response from Exa MCP (status={response.status_code})",
                            "body_preview": text_body[:500],
                        }
                    }
        return response.status_code, data, raw_headers

    def _initialize(self) -> dict:
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "indian-stock-ai-agent", "version": "1.0"},
            },
        }
        status, data, _ = self._post(init_payload, include_session=False)
        if status >= 400 or "error" in data:
            return {"ok": False, "error": data.get("error", {"message": f"initialize failed: {status}"})}

        # Best-effort initialized notification
        notif_payload = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        try:
            self._post(notif_payload, include_session=True)
        except Exception:
            pass
        return {"ok": True}

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        # Attempt direct call first
        status, data, _ = self._post(payload, include_session=True)
        if status < 400 and "error" not in data:
            return {"ok": True, "data": data}

        # Retry once with MCP initialize handshake
        init = self._initialize()
        if not init.get("ok"):
            return {"ok": False, "error": init.get("error")}

        status2, data2, _ = self._post(payload, include_session=True)
        if status2 >= 400 or "error" in data2:
            return {"ok": False, "error": data2.get("error", {"message": f"tools/call failed: {status2}"})}
        return {"ok": True, "data": data2}


def _extract_mcp_result(payload: dict) -> Any:
    """
    Exa MCP can return content as text blocks or structured content.
    This function normalizes the result for downstream parsing.
    """
    result = payload.get("result", {})

    if "structuredContent" in result:
        return result["structuredContent"]

    content = result.get("content")
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text" and "text" in item:
                    text_parts.append(item["text"])
                elif "text" in item:
                    text_parts.append(item["text"])
        if text_parts:
            joined = "\n".join(text_parts).strip()
            try:
                return json.loads(joined)
            except Exception:
                return {"text": joined}
    return result


def _exa_call(tool_name: str, arguments: dict) -> dict:
    client = _ExaMcpClient(EXA_MCP_HTTP_URL)
    outcome = client.call_tool(tool_name, arguments)
    if not outcome.get("ok"):
        return {
            "success": False,
            "tool": tool_name,
            "error": outcome.get("error", {"message": "unknown Exa MCP error"}),
        }

    parsed = _extract_mcp_result(outcome["data"])
    return {"success": True, "tool": tool_name, "result": parsed}


@function_tool
def exa_web_search_stock_news(symbol: str, company_name: str = "", num_results: int = 8) -> str:
    """
    Fetch live, web-searched stock/company news using Exa MCP.
    """
    normalized = _normalize_symbol(symbol)
    name_part = f" {company_name}" if company_name else ""
    query = (
        f"{normalized}{name_part} NSE stock latest news earnings guidance "
        f"regulatory update management commentary analyst rating India"
    )
    response = _exa_call(
        "web_search_exa",
        {
            "query": query,
            "numResults": max(3, min(num_results, 12)),
            "livecrawl": "preferred",
            "type": "auto",
            "contextMaxCharacters": 14000,
        },
    )
    response["query"] = query
    response["as_of"] = datetime.utcnow().isoformat()
    return _to_json(response)


@function_tool
def exa_company_snapshot(company_name: str, num_results: int = 3) -> str:
    """
    Fetch company-level profile/intelligence using Exa MCP.
    """
    response = _exa_call(
        "company_research_exa",
        {"companyName": company_name, "numResults": max(1, min(num_results, 8))},
    )
    response["company_name"] = company_name
    response["as_of"] = datetime.utcnow().isoformat()
    return _to_json(response)


@function_tool
def exa_deep_stock_research(
    symbol: str,
    company_name: str = "",
    focus: str = "investment risks, catalysts, valuation context, and near-term triggers",
    model: str = "exa-research",
) -> str:
    """
    Run Exa deep research and poll for completion.
    """
    normalized = _normalize_symbol(symbol)
    display = company_name or normalized
    instructions = (
        f"Create an investor-ready research brief for {display} ({normalized}, India/NSE). "
        f"Focus on: {focus}. Use latest available public sources, cite source links, "
        "and end with a practical BUY/SELL/HOLD view with key assumptions."
    )

    start = _exa_call("deep_researcher_start", {"instructions": instructions, "model": model})
    if not start.get("success"):
        return _to_json(start)

    start_result = start.get("result", {})
    research_id = (
        start_result.get("researchId")
        or start_result.get("research_id")
        or start_result.get("id")
    )
    if not research_id:
        return _to_json(
            {
                "success": False,
                "tool": "deep_researcher_start",
                "error": {"message": "deep_researcher_start did not return researchId"},
                "raw_start_result": start_result,
            }
        )

    deadline = time.time() + EXA_DEEP_RESEARCH_TIMEOUT_SECONDS
    last_check = None
    while time.time() < deadline:
        check = _exa_call("deep_researcher_check", {"researchId": research_id})
        last_check = check
        if not check.get("success"):
            break
        result = check.get("result", {})
        status = result.get("status", "")
        if str(status).lower() == "completed":
            return _to_json(
                {
                    "success": True,
                    "tool": "deep_researcher",
                    "research_id": research_id,
                    "result": result,
                    "as_of": datetime.utcnow().isoformat(),
                }
            )
        time.sleep(EXA_DEEP_RESEARCH_POLL_INTERVAL_SECONDS)

    return _to_json(
        {
            "success": False,
            "tool": "deep_researcher",
            "research_id": research_id,
            "error": {"message": "Deep research did not complete within timeout"},
            "last_check": last_check,
        }
    )


@function_tool
def exa_live_company_intelligence(
    symbol: str,
    company_name: str = "",
    include_deep_research: bool = False,
) -> str:
    """
    Combined Exa tool for live stock intelligence.
    """
    normalized = _normalize_symbol(symbol)
    name = company_name or normalized

    web = json.loads(exa_web_search_stock_news(normalized, name, 8))
    snapshot = json.loads(exa_company_snapshot(name, 3))

    response = {
        "success": bool(web.get("success") or snapshot.get("success")),
        "symbol": normalized,
        "company_name": name,
        "as_of": datetime.utcnow().isoformat(),
        "web_search": web,
        "company_snapshot": snapshot,
    }

    if include_deep_research:
        response["deep_research"] = json.loads(
            exa_deep_stock_research(
                symbol=normalized,
                company_name=name,
                focus="latest business developments, sector context, risks, catalysts, and investment stance",
                model="exa-research-fast",
            )
        )

    return _to_json(response)
