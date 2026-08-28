from langchain.agents import create_agent

from tools import TOOLS
from middleware import SkillMiddleware


def create_skill_agent():
    system_prompt=(
        "당신은 여행자를 돕는 에이전트입니다. "
        "현지 문화/매너, 일정·예산 계획, 응급 상황 대처처럼 전문 지식이 필요한 질문에는 "
        "먼저 사용 가능한 스킬 목록에서 관련 스킬을 찾아 로드한 뒤, "
        "그 스킬에 정의된 절차를 따라 답변하세요."
    )

    # 스킬 미들웨어 초기화
    skill_middleware = SkillMiddleware()

    agent_executor = create_agent(
        model="gpt-5.4-mini",
        tools=TOOLS,
        system_prompt=system_prompt,
        middleware=[skill_middleware],
    )

    return agent_executor


agent = create_skill_agent()
