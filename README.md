# 목적
- 여행지 추천 및 여행 관련 정보 제공 서비스
- https://appapppy-yqgazmvvwnr77wbydtn6on.streamlit.app/

# 해결하고자 하는 문제
- 항공, 숙소, 맛집, 교통, 현지 팁이 각각 다른 플랫폼에 흩어져 있어 사용자가 직접 취합하고 대조하는 비용이 크다.
- 검색 상위 결과나 블로그 글은 방문 장소의 영업시간이나 휴무 여부 등을 반영하지 않기 때문에 신뢰하기 어렵다.
- 사용자마다 경비, 날씨, 위치 등 상황이 다르기 때문에 일반화된 TOP 10 리스트는 적절하지 않다.

# 에이전트가 하는 일
- 탐색 단계: "어디로 갈지 모르겠다"는 사용자에게 취향 기반 목적지를 제안한다.
- 의사결정 단계: 후보 목적지 간 비교(비용, 계절, 접근성 등)를 통해 사용자의 선택에 도움을 준다.
- 실행 단계: 선택된 목적지에 대한 실질적인 예약 정보(항공권, 숙박)를 제공한다.

# ｢AI Travel Agent｣ 
사용자의 여행 목적과 요청을 자연어로 입력받으면 AI가 필요한 여행 정보를 분석하고, 상황에 맞는 Tool을 선택하여 정보를 제공하는 AI 기반 여행 Agent를 구현하였다. 항공권, 호텔, 관광지 등 여행에 필요한 정보를 검색할 수 있도록 여러 Tool을 구성하였으며, 사용자의 질문 유형에 따라 적절한 Tool을 자동으로 선택하여 실행하도록 Agent를 설계하였다.
또한 목적지에 따른 여행 일정과 현지 문화·매너, 여행 중 발생할 수 있는 긴급 상황 등의 정보까지 폭넓게 제공하도록 구성하였다. 현지 문화·매너를 다루는 local-etiquette Tool은 목적지의 인사, 식사, 팁, 복장, 금기 등 한국과 다른 점을 web_search로 조사하여 카테고리별로 정리해 제공하며, 여행 중 발생하기 쉬운 문화적 실수를 예방하는 것을 목적으로 모든 정보에 출처를 함께 제시한다. 일정 수립을 담당하는 itinerary-planning Tool은 목적지, 기간, 예산, 취향을 기반으로 예산 추정과 일자별 동선을 한 번에 제시하며, 정보가 부족한 경우에도 되묻지 않고 합리적인 추정으로 보완하여 답변을 완성하고, 마지막에는 emergency-info를 가볍게 참고하여 안전 팁을 1~2줄 덧붙인다. 응급 상황을 다루는 emergency-info Tool은 여권 분실, 사고, 질병 등 실제 위급 상황이 발생했을 때는 절차보다 현지·대사관 긴급 연락처를 먼저 안내하며, 사전에 안전 정보를 묻는 경우에는 해당 지역에서 흔히 발생하는 사고 유형과 예방법을 안내한다.
이를 통해 사용자가 여러 여행 정보를 직접 검색해야 하는 번거로움을 줄이고, 자연어 질문만으로 여행 계획에 필요한 정보를 한 번에 확인할 수 있도록 구현하였다.

# 예시 질문
- 상하이로 3박 4일 여행을 가려는데 항공권 가장 저렴한 시기 추천해줘
-  3박 4일 상하이 관광 일정 짜줘
- 10월에 도쿄로 3박 4일 여행 가려는데 항공편, 호텔 관광지 한번에 추천해줘
- 일본에서 지켜야하는 매너 수칙 알려줘
- 공항에서 여권 잃어버렸을때 어떻게 해야하는지 알려줘

<img width="417" height="575" alt="스크린샷 2026-08-28 141417" src="https://github.com/user-attachments/assets/b75c748b-b3ed-441e-86c9-03577e27c5c8" />
<img width="614" height="593" alt="스크린샷 2026-08-28 141340" src="https://github.com/user-attachments/assets/58bcb6da-5be0-4f83-8429-adf08b13716b" />
<img width="643" height="537" alt="스크린샷 2026-08-28 141336" src="https://github.com/user-attachments/assets/5b2a9631-96a4-4cf5-8c72-07d6a55ab5f8" />
<img width="410" height="557" alt="스크린샷 2026-08-28 141329" src="https://github.com/user-attachments/assets/22eef0e5-ace4-4424-a02f-369c6bd2a09a" />
<img width="474" height="557" alt="스크린샷 2026-08-28 141254" src="https://github.com/user-attachments/assets/787d96e6-690a-4332-8b82-f21c704f3a59" />
<img width="525" height="548" alt="스크린샷 2026-08-28 141250" src="https://github.com/user-attachments/assets/05666d8a-b18b-45f4-b4cc-ba188e1bee80" />
<img width="308" height="584" alt="스크린샷 2026-08-28 141420" src="https://github.com/user-attachments/assets/c9f5b342-7845-498e-86a6-8dfd332b2fbb" />
<img width="596" height="597" alt="스크린샷 2026-08-28 141609" src="https://github.com/user-attachments/assets/52d14cbb-29b0-4a58-8ea0-26afe674cbc3" />
<img width="576" height="584" alt="스크린샷 2026-08-28 141605" src="https://github.com/user-attachments/assets/3ccb0f2d-b819-421c-b082-6e07ede841c2" />
<img width="593" height="589" alt="스크린샷 2026-08-28 141601" src="https://github.com/user-attachments/assets/d056bcc3-4221-4678-af36-a3cd70d88316" />
<img width="539" height="575" alt="스크린샷 2026-08-28 141557" src="https://github.com/user-attachments/assets/a66ff5e0-a5de-48a0-b490-05a2fc4182bc" />
<img width="579" height="574" alt="스크린샷 2026-08-28 141527" src="https://github.com/user-attachments/assets/50c26469-3130-4d6f-845b-9f16bc56776c" />
<img width="506" height="587" alt="스크린샷 2026-08-28 141523" src="https://github.com/user-attachments/assets/fb94667a-c909-4fd5-9a35-3c9acc71648c" />
<img width="404" height="581" alt="스크린샷 2026-08-28 141519" src="https://github.com/user-attachments/assets/4aa39829-2c34-4c63-9fc4-e9d3d9494403" />
<img width="409" height="537" alt="스크린샷 2026-08-28 141514" src="https://github.com/user-attachments/assets/9f2e059c-dc07-4129-815e-89fdfa35a989" />
<img width="624" height="570" alt="스크린샷 2026-08-28 141442" src="https://github.com/user-attachments/assets/83854a2d-a5b6-45d6-9845-6f4ab3d1764d" />
<img width="566" height="591" alt="스크린샷 2026-08-28 141438" src="https://github.com/user-attachments/assets/e4cc602a-6945-4495-947c-b62746372913" />
<img width="625" height="589" alt="스크린샷 2026-08-28 141433" src="https://github.com/user-attachments/assets/afffaf56-d70a-4952-82e5-22080ac60cff" />
<img width="568" height="592" alt="스크린샷 2026-08-28 141429" src="https://github.com/user-attachments/assets/08da6242-b5ee-4d69-8f55-8507735d30a4" />
<img width="591" height="564" alt="스크린샷 2026-08-28 141425" src="https://github.com/user-attachments/assets/28f0736b-80b4-404c-9deb-d5669cc98298" />
