from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# 이 파일 위치(domain-agent) 기준으로 상위(trip_agent)의 .env를 명시적으로 로드
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from langchain_core.messages import AIMessage, ToolMessage
from agent import agent


def init_session_state():
    """세션 상태 초기화"""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def display_message(role: str, content: str, tool_calls: list | None = None):
    """메시지 표시"""
    with st.chat_message(role):
        st.markdown(content)

        if role == "assistant" and tool_calls:
            display_tool_calls(tool_calls)


def display_tool_calls(tool_calls: list):
    """이번 턴에 사용된 도구 호출 정보 표시"""
    with st.expander(f"🔧 사용된 도구 ({len(tool_calls)}개)"):
        for call in tool_calls:
            st.markdown(f"**{call['name']}**")
            if call.get("args"):
                st.caption("입력값")
                st.json(call["args"])
            st.caption("결과")
            st.text(call.get("result", "(결과 없음)")[:1500])
            st.divider()


def extract_tool_calls(messages: list) -> list:
    """이번 턴에 새로 생긴 메시지에서 도구 호출(이름/입력/결과)을 추출"""
    tool_results = {m.tool_call_id: m.content for m in messages if isinstance(m, ToolMessage)}

    calls = []
    for m in messages:
        if isinstance(m, AIMessage) and m.tool_calls:
            for tc in m.tool_calls:
                calls.append({
                    "name": tc["name"],
                    "args": tc.get("args", {}),
                    "result": str(tool_results.get(tc["id"], "")),
                })
    return calls


def main():
    """메인 함수"""
    st.set_page_config(
        page_title="여행 계획 AI 에이전트",
        page_icon="✈️",
        layout="wide"
    )

    st.title("✈️ 여행 계획 AI 에이전트")
    st.markdown("---")

    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정 확인")

        import os
        required_vars = {
            "OPENAI_API_KEY": "OpenAI API",
            "TAVILY_API_KEY": "Tavily(아고다 검색) API",
        }
        for var, name in required_vars.items():
            if os.getenv(var):
                st.success(f"✓ {name}")
            else:
                st.error(f"✗ {name}")

        st.markdown("---")
        st.header("📖 사용 방법")
        st.markdown("""
        **항공권 검색:**
        - "서울에서 도쿄 항공권 알려줘"
        - "출발지 모르는데 여행지 추천해줘"

        **호텔 검색:**
        - "부산 호텔 10월 5일부터 2박 알려줘"

        **관광지 정보:**
        - "경주 맛집 추천해줘"

        **여행 계획/일정:**
        - "다낭 4박 5일 계획 짜줘"

        **예약 확정:**
        - "그중에 첫 번째로 예약해줘"
        """)

        if st.button("대화 초기화", type="secondary"):
            st.session_state.messages = []
            st.rerun()

    # 세션 상태 초기화
    init_session_state()

    # 이전 메시지 표시
    for message in st.session_state.messages:
        display_message(
            message["role"],
            message["content"],
            message.get("tool_calls")
        )

    # 사용자 입력
    if prompt := st.chat_input("여행 계획을 물어보세요..."):
        display_message("user", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                try:
                    # 지금까지의 대화 이력을 함께 전달
                    history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                    result = agent.invoke({"messages": history})

                    all_messages = result.get("messages", [])

                    # 이번 턴에 새로 추가된 메시지만 추출 (마지막 사용자 메시지 이후)
                    last_human_idx = max(
                        i for i, m in enumerate(all_messages)
                        if m.__class__.__name__ == "HumanMessage"
                    )
                    turn_messages = all_messages[last_human_idx + 1:]

                    tool_calls = extract_tool_calls(turn_messages)

                    # 최종 답변 텍스트(마지막 AIMessage들의 content를 이어붙임)
                    answer_parts = [
                        m.content for m in turn_messages
                        if isinstance(m, AIMessage) and m.content
                    ]
                    answer = "\n\n".join(answer_parts) if answer_parts else "죄송합니다. 답변을 생성할 수 없습니다."

                    st.markdown(answer)
                    if tool_calls:
                        display_tool_calls(tool_calls)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "tool_calls": tool_calls,
                    })

                except Exception as e:
                    error_msg = f"오류가 발생했습니다: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


if __name__ == "__main__":
    main()
