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
<img width="1274" height="696" alt="스크린샷 2026-08-28 114032" src="https://github.com/user-attachments/assets/3a17c9ca-c6f9-4981-853d-5854e8710134" />
<img width="1267" height="605" alt="스크린샷 2026-08-28 114136" src="https://github.com/user-attachments/assets/1103d31a-8ab3-4b52-a514-a405ff9b3ce1" />
<img width="1271" height="600" alt="스크린샷 2026-08-28 114142" src="https://github.com/user-attachments/assets/cc25e861-896a-4777-be95-625c59360867" />
<img width="1270" height="604" alt="스크린샷 2026-08-28 114101" src="https://github.com/user-attachments/assets/250b8b96-aa55-45d2-be8a-b4a8bc68446a" />
<img width="1265" height="599" alt="스크린샷 2026-08-28 114108" src="https://github.com/user-attachments/assets/d0f712f5-adbc-42cf-bada-2da06d16da3d" />
<img width="1267" height="595" alt="스크린샷 2026-08-28 114545" src="https://github.com/user-attachments/assets/09976d9f-806a-4adb-889d-97f35645a76a" />
<img width="1258" height="594" alt="스크린샷 2026-08-28 114539" src="https://github.com/user-attachments/assets/cea30ee2-d466-49e7-9869-371a11c6486c" />
<img width="1268" height="596" alt="스크린샷 2026-08-28 114532" src="https://github.com/user-attachments/assets/ce8de3cb-883d-49d4-918b-7b8ff487b580" />
<img width="1267" height="604" alt="스크린샷 2026-08-28 114235" src="https://github.com/user-attachments/assets/435af615-7258-4efb-8723-0b97c7070560" />
<img width="1265" height="597" alt="스크린샷 2026-08-28 114227" src="https://github.com/user-attachments/assets/b36ffc94-57a5-4134-9d5b-245a680dbdd6" />
<img width="1268" height="601" alt="스크린샷 2026-08-28 114216" src="https://github.com/user-attachments/assets/d087eadf-c718-4bd3-bbe9-ce95ab01dd83" />
<img width="1264" height="602" alt="스크린샷 2026-08-28 114154" src="https://github.com/user-attachments/assets/2c5022bd-3d7b-4bbb-b33f-057c77677d7e" />
<img width="1272" height="598" alt="스크린샷 2026-08-28 114149" src="https://github.com/user-attachments/assets/21630198-7322-4018-8cf9-cdb3917d26f9" />
