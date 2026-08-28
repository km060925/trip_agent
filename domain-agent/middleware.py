import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Any
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage, HumanMessage
from langchain.agents.middleware import before_agent, after_agent, wrap_tool_call, AgentState
from langgraph.runtime import Runtime


@before_agent
def travel_context_middleware(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Travel Context Middleware

    에이전트 시작 시 오늘 날짜와 현재 계절 정보를 state에 주입합니다.

    이를 통해 LLM은 "다음 달", "이번 가을" 같은 상대적인 시기 표현이 나와도
    실제 연/월을 스스로 계산해 도구를 올바른 파라미터로 호출할 수 있습니다.
    """
    print("\n[Travel Context] 오늘 날짜 및 계절 정보 주입...")

    today = datetime.now()
    month = today.month
    season = {
        (12, 1, 2): "겨울",
        (3, 4, 5): "봄",
        (6, 7, 8): "여름",
        (9, 10, 11): "가을",
    }
    current_season = next(name for months, name in season.items() if month in months)

    context_info = (
        f"[여행 컨텍스트]\n"
        f"오늘 날짜: {today.strftime('%Y-%m-%d')} ({current_season})\n\n"
        "사용자가 '다음 달', '이번 여름' 처럼 상대적인 시기로 여행 시기를 말하면, "
        "위 오늘 날짜를 기준으로 실제 연/월/일을 계산하여 도구의 날짜 파라미터로 사용하세요."
    )

    print("[Travel Context] ✅ 컨텍스트 주입 완료")

    system_message = SystemMessage(content=context_info)

    return {"messages": [system_message]}


@wrap_tool_call
async def search_log_middleware(request, handler):
    """Search Log Middleware

    항공권/호텔/관광지 검색 도구가 호출될 때마다 검색 이력을 남깁니다.
    검색 로그는 search_history/ 디렉터리에 "YYYYMMDD.jsonl" 형식으로 누적 저장됩니다.

    이를 통해 사용자가 이전에 어떤 조건으로 검색했는지 추적하거나,
    반복 질문에 대해 참고 자료로 활용할 수 있습니다.
    """
    tool_name = request.tool_call["name"]
    tool_args = request.tool_call.get("args", {})

    # 여행 검색 도구만 기록
    if tool_name not in ("search_flights", "search_hotels", "get_tourist_attractions"):
        return await handler(request)

    # 실제 도구 실행
    result = await handler(request)

    try:
        # 검색 이력 디렉터리 생성
        history_dir = Path("search_history")
        history_dir.mkdir(exist_ok=True)

        # 오늘 날짜 파일에 한 줄씩 누적 기록
        log_filename = f"{datetime.now().strftime('%Y%m%d')}.jsonl"
        log_path = history_dir / log_filename

        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tool": tool_name,
            "args": tool_args,
        }

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        print(f"\n[Search Log] 📝 검색 기록 저장: {log_path} ({tool_name})")

    except Exception as e:
        print(f"[Search Log] ⚠️ 기록 실패: {e}")
        # 기록 실패해도 원본 검색 결과는 그대로 반환

    return result


@wrap_tool_call
async def holiday_notice_middleware(request, handler):
    """Holiday Notice Middleware

    get_tourist_attractions 결과에 포함된 장소들의 정기 휴무일을 확인하여,
    오늘이 휴무일인 장소가 있으면 결과 상단에 경고 문구를 추가합니다.

    get_tourist_attractions가 각 장소를
    "- 장소명 | 설명 | 운영시간: ... | 휴무일: 매주 O요일" 형식으로 반환한다는 점을 이용해
    별도 데이터 없이 결과 텍스트만으로 오늘 휴무 여부를 판단합니다.
    """
    tool_name = request.tool_call["name"]

    result = await handler(request)

    if tool_name != "get_tourist_attractions":
        return result

    if not isinstance(result, ToolMessage) or not isinstance(result.content, str):
        return result

    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
    today_weekday = weekday_names[datetime.now().weekday()]

    closed_today = []
    for line in result.content.splitlines():
        match = re.match(r"- (.+?) \|.*\| 휴무일: (.+)", line)
        if not match:
            continue
        place_name, closed_day = match.group(1), match.group(2)
        if f"매주 {today_weekday}요일" in closed_day:
            closed_today.append(place_name)

    if not closed_today:
        return result

    print(f"\n[Holiday Notice] ⚠️ 오늘({today_weekday}요일) 휴무 장소 {len(closed_today)}곳 안내 추가")

    notice = (
        f"⚠️ 휴무일 안내: 오늘은 {today_weekday}요일로, "
        f"다음 장소는 정기 휴무일일 수 있습니다 → {', '.join(closed_today)}\n\n"
    )

    return result.model_copy(update={"content": notice + result.content})


@after_agent
def trip_summary_middleware(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Trip Summary Middleware

    이번 턴에 confirm_booking이 완료됐다면(항공권/호텔 예약 확정 및 예약 사이트 안내),
    여행 계획이 확정된 것으로 보고 이번 턴의 confirm_booking 결과들을 모아
    최종 여행 계획 요약 메시지를 추가합니다.
    """
    messages = state["messages"]

    # 이번 턴에 새로 추가된 메시지만 추출 (가장 최근 HumanMessage 이후)
    current_turn = []
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            break
        current_turn.append(message)
    current_turn.reverse()

    booking_messages = [
        m for m in current_turn
        if isinstance(m, ToolMessage) and m.name == "confirm_booking" and m.status != "error"
    ]

    if not booking_messages:
        return None

    print("\n[Trip Summary] ✅ 예약 확정 감지 - 여행 계획 요약 메시지 추가")

    summary_lines = ["📋 [여행 계획 요약]", ""]
    for m in booking_messages:
        summary_lines.append(str(m.content))
        summary_lines.append("")
    summary_lines.append("✅ 안내해드린 사이트에서 예약을 완료하시면 여행 계획이 확정됩니다. 즐거운 여행 되세요!")

    summary_message = AIMessage(content="\n".join(summary_lines))

    return {"messages": [summary_message]}
