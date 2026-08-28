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
<img width="653" height="545" alt="스크린샷 2026-08-28 131526" src="https://github.com/user-attachments/assets/97795c5d-76e8-4de9-8a6c-195cdcdbb697" />
<img width="554" height="593" alt="스크린샷 2026-08-28 131424" src="https://github.com/user-attachments/assets/c4793448-4c49-4382-854f-3c1a3066e699" />
<img width="528" height="557" alt="스크린샷 2026-08-28 131416" src="https://github.com/user-attachments/assets/3657b8b5-2961-440c-b133-3cbf80174485" />
<img width="595" height="575" alt="스크린샷 2026-08-28 131410" src="https://github.com/user-attachments/assets/c97bc110-3b45-4c5a-8dc0-b02091c06562" />
<img width="569" height="570" alt="스크린샷 2026-08-28 131343" src="https://github.com/user-attachments/assets/1d724eb0-c40b-4bb3-9739-335dae8bcdcc" />
<img width="629" height="554" alt="스크린샷 2026-08-28 131335" src="https://github.com/user-attachments/assets/a8dbe5cd-2329-4426-8117-f969d2fb5893" />
<img width="523" height="564" alt="스크린샷 2026-08-28 131739" src="https://github.com/user-attachments/assets/54592fbe-3165-46b0-adec-30f5a04642c0" />
<img width="499" height="579" alt="스크린샷 2026-08-28 131735" src="https://github.com/user-attachments/assets/3a0f2060-0ee2-4bb7-9580-40752a0ab796" />
<img width="479" height="575" alt="스크린샷 2026-08-28 131730" src="https://github.com/user-attachments/assets/d69033a6-fbe9-4d03-b525-d91dca7a83ba" />
<img width="488" height="563" alt="스크린샷 2026-08-28 131723" src="https://github.com/user-attachments/assets/b9470a0b-154c-487d-956d-6595aae0f8d3" />
<img width="500" height="596" alt="스크린샷 2026-08-28 131656" src="https://github.com/user-attachments/assets/e125991d-dec2-438d-b36f-92f015e0d8a8" />
<img width="515" height="542" alt="스크린샷 2026-08-28 131650" src="https://github.com/user-attachments/assets/254bff5d-c2ad-4a59-a20d-8fc74713a0bf" />
<img width="406" height="591" alt="스크린샷 2026-08-28 131645" src="https://github.com/user-attachments/assets/09c044f5-456a-452d-9951-103a5dd53f8a" />
<img width="450" height="585" alt="스크린샷 2026-08-28 131640" src="https://github.com/user-attachments/assets/1bc8ed1f-31e1-4158-b07a-b9f4008a45e5" />
<img width="574" height="580" alt="스크린샷 2026-08-28 131613" src="https://github.com/user-attachments/assets/c9383605-a00a-4220-bab0-ca57734e3ffd" />
<img width="556" height="589" alt="스크린샷 2026-08-28 131607" src="https://github.com/user-attachments/assets/8596db76-35b8-484d-8884-f50dc06cc6b3" />
<img width="533" height="591" alt="스크린샷 2026-08-28 131558" src="https://github.com/user-attachments/assets/d2ff5150-c5a2-4113-a81e-2fc9df73e457" />
<img width="556" height="588" alt="스크린샷 2026-08-28 131552" src="https://github.com/user-attachments/assets/b82f84d4-7df3-46e8-aab1-2b9d8d5fc5cc" />
<img width="545" height="583" alt="스크린샷 2026-08-28 131546" src="https://github.com/user-attachments/assets/62e1ad08-82ca-4f93-a090-ca491101cf55" />
<img width="559" height="587" alt="스크린샷 2026-08-28 131540" src="https://github.com/user-attachments/assets/35441c9a-beed-4ba0-88c8-e530aadc3d85" />
<img width="382" height="586" alt="스크린샷 2026-08-28 131534" src="https://github.com/user-attachments/assets/3f9793ba-cc63-434e-a488-43fba2c92655" />

