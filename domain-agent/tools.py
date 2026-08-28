from langchain.tools import tool
from langchain_tavily import TavilySearch
from typing import Optional
import subprocess
import sys
import os

# ============================================
# 여행지 추천 도메인 도구
# ============================================

# 도시 → (국가, 가격 산정용 권역, 영문 도시명) 매핑.
# - 국가명은 화면에 그대로 노출해서, 도시를 뭉뚱그린 권역 이름(아시아/유럽 등)이 아니라
#   사용자가 입력한 그 나라/도시가 명확히 보이도록 합니다. (권역은 내부 가격 산정에만 사용)
# - 영문 도시명은 아고다 실시간 검색 쿼리에 사용합니다. 아고다 페이지가 한글보다 영문 검색에
#   훨씬 정확하게 매칭되는 경우가 많기 때문입니다(예: '서울 로마 항공권'은 관련 없는 노선이
#   나오지만 'Seoul Rome flight'는 정확한 서울-로마 노선 페이지가 나옵니다).
CITY_INFO = {
    # 국내
    "서울": ("대한민국", "국내", "Seoul"), "인천": ("대한민국", "국내", "Incheon"), "부산": ("대한민국", "국내", "Busan"),
    "제주": ("대한민국", "국내", "Jeju"), "강릉": ("대한민국", "국내", "Gangneung"), "여수": ("대한민국", "국내", "Yeosu"),
    "대구": ("대한민국", "국내", "Daegu"), "광주": ("대한민국", "국내", "Gwangju"), "청주": ("대한민국", "국내", "Cheongju"),
    "전주": ("대한민국", "국내", "Jeonju"), "포항": ("대한민국", "국내", "Pohang"), "울산": ("대한민국", "국내", "Ulsan"),
    "목포": ("대한민국", "국내", "Mokpo"),
    "경주": ("대한민국", "국내", "Gyeongju"), "춘천": ("대한민국", "국내", "Chuncheon"),
    "안동": ("대한민국", "국내", "Andong"), "속초": ("대한민국", "국내", "Sokcho"),
    "통영": ("대한민국", "국내", "Tongyeong"), "거제": ("대한민국", "국내", "Geoje"),
    "남해": ("대한민국", "국내", "Namhae"), "태안": ("대한민국", "국내", "Taean"),
    "평창": ("대한민국", "국내", "Pyeongchang"), "가평": ("대한민국", "국내", "Gapyeong"),
    "수원": ("대한민국", "국내", "Suwon"), "천안": ("대한민국", "국내", "Cheonan"),
    "군산": ("대한민국", "국내", "Gunsan"), "순천": ("대한민국", "국내", "Suncheon"),
    "대전": ("대한민국", "국내", "Daejeon"), "창원": ("대한민국", "국내", "Changwon"),
    # 아시아
    "도쿄": ("일본", "아시아", "Tokyo"), "오사카": ("일본", "아시아", "Osaka"),
    "삿포로": ("일본", "아시아", "Sapporo"), "후쿠오카": ("일본", "아시아", "Fukuoka"),
    "나고야": ("일본", "아시아", "Nagoya"), "고베": ("일본", "아시아", "Kobe"), "나라": ("일본", "아시아", "Nara"),
    "오키나와": ("일본", "아시아", "Okinawa"),
    "방콕": ("태국", "아시아", "Bangkok"), "푸켓": ("태국", "아시아", "Phuket"), "치앙마이": ("태국", "아시아", "Chiang Mai"),
    "세부": ("필리핀", "아시아", "Cebu"), "마닐라": ("필리핀", "아시아", "Manila"), "보라카이": ("필리핀", "아시아", "Boracay"),
    "다낭": ("베트남", "아시아", "Da Nang"), "하노이": ("베트남", "아시아", "Hanoi"), "호치민": ("베트남", "아시아", "Ho Chi Minh"),
    "나트랑": ("베트남", "아시아", "Nha Trang"), "푸꾸옥": ("베트남", "아시아", "Phu Quoc"),
    "발리": ("인도네시아", "아시아", "Bali"), "자카르타": ("인도네시아", "아시아", "Jakarta"),
    "홍콩": ("홍콩", "아시아", "Hong Kong"), "마카오": ("마카오", "아시아", "Macau"),
    "타이베이": ("대만", "아시아", "Taipei"), "가오슝": ("대만", "아시아", "Kaohsiung"),
    "싱가포르": ("싱가포르", "아시아", "Singapore"),
    "괌": ("괌(미국령)", "아시아", "Guam"), "사이판": ("사이판(미국령)", "아시아", "Saipan"),
    "쿠알라룸푸르": ("말레이시아", "아시아", "Kuala Lumpur"), "페낭": ("말레이시아", "아시아", "Penang"),
    "씨엠립": ("캄보디아", "아시아", "Siem Reap"), "프놈펜": ("캄보디아", "아시아", "Phnom Penh"),
    "울란바토르": ("몽골", "아시아", "Ulaanbaatar"),
    "상하이": ("중국", "아시아", "Shanghai"), "베이징": ("중국", "아시아", "Beijing"),
    "광저우": ("중국", "아시아", "Guangzhou"), "선전": ("중국", "아시아", "Shenzhen"),
    "청두": ("중국", "아시아", "Chengdu"), "시안": ("중국", "아시아", "Xi'an"),
    "항저우": ("중국", "아시아", "Hangzhou"), "칭다오": ("중국", "아시아", "Qingdao"),
    "델리": ("인도", "아시아", "Delhi"), "뭄바이": ("인도", "아시아", "Mumbai"),
    # 유럽
    "파리": ("프랑스", "유럽", "Paris"), "니스": ("프랑스", "유럽", "Nice"),
    "런던": ("영국", "유럽", "London"), "에든버러": ("영국", "유럽", "Edinburgh"),
    "로마": ("이탈리아", "유럽", "Rome"), "밀라노": ("이탈리아", "유럽", "Milan"),
    "피렌체": ("이탈리아", "유럽", "Florence"), "베니스": ("이탈리아", "유럽", "Venice"), "베네치아": ("이탈리아", "유럽", "Venice"),
    "프랑크푸르트": ("독일", "유럽", "Frankfurt"), "뮌헨": ("독일", "유럽", "Munich"), "베를린": ("독일", "유럽", "Berlin"),
    "취리히": ("스위스", "유럽", "Zurich"), "인터라켄": ("스위스", "유럽", "Interlaken"),
    "암스테르담": ("네덜란드", "유럽", "Amsterdam"),
    "바르셀로나": ("스페인", "유럽", "Barcelona"), "마드리드": ("스페인", "유럽", "Madrid"),
    "프라하": ("체코", "유럽", "Prague"), "빈": ("오스트리아", "유럽", "Vienna"), "비엔나": ("오스트리아", "유럽", "Vienna"),
    "이스탄불": ("튀르키예", "유럽", "Istanbul"), "아테네": ("그리스", "유럽", "Athens"), "산토리니": ("그리스", "유럽", "Santorini"),
    "리스본": ("포르투갈", "유럽", "Lisbon"),
    "부다페스트": ("헝가리", "유럽", "Budapest"), "코펜하겐": ("덴마크", "유럽", "Copenhagen"),
    "스톡홀름": ("스웨덴", "유럽", "Stockholm"), "헬싱키": ("핀란드", "유럽", "Helsinki"),
    "더블린": ("아일랜드", "유럽", "Dublin"),
    # 미주
    "뉴욕": ("미국", "미주", "New York"), "로스앤젤레스": ("미국", "미주", "Los Angeles"), "LA": ("미국", "미주", "Los Angeles"),
    "샌프란시스코": ("미국", "미주", "San Francisco"), "시애틀": ("미국", "미주", "Seattle"), "시카고": ("미국", "미주", "Chicago"),
    "라스베가스": ("미국", "미주", "Las Vegas"), "마이애미": ("미국", "미주", "Miami"),
    "보스턴": ("미국", "미주", "Boston"), "워싱턴": ("미국", "미주", "Washington DC"), "호놀룰루": ("미국", "미주", "Honolulu"),
    "토론토": ("캐나다", "미주", "Toronto"), "밴쿠버": ("캐나다", "미주", "Vancouver"),
    "멕시코시티": ("멕시코", "미주", "Mexico City"), "칸쿤": ("멕시코", "미주", "Cancun"),
    "상파울루": ("브라질", "미주", "Sao Paulo"), "리우데자네이루": ("브라질", "미주", "Rio de Janeiro"),
    # 오세아니아
    "시드니": ("호주", "오세아니아", "Sydney"), "멜버른": ("호주", "오세아니아", "Melbourne"),
    "브리즈번": ("호주", "오세아니아", "Brisbane"), "골드코스트": ("호주", "오세아니아", "Gold Coast"),
    "퍼스": ("호주", "오세아니아", "Perth"),
    "오클랜드": ("뉴질랜드", "오세아니아", "Auckland"), "웰링턴": ("뉴질랜드", "오세아니아", "Wellington"),
    "퀸스타운": ("뉴질랜드", "오세아니아", "Queenstown"),
    # 중동/아프리카
    "두바이": ("아랍에미리트", "기타 해외", "Dubai"), "아부다비": ("아랍에미리트", "기타 해외", "Abu Dhabi"),
    "도하": ("카타르", "기타 해외", "Doha"),
    "카이로": ("이집트", "기타 해외", "Cairo"), "케이프타운": ("남아프리카공화국", "기타 해외", "Cape Town"),
    "마라케시": ("모로코", "기타 해외", "Marrakech"),
}

# 권역별 항공편/월별 가격 데이터 (실제로는 항공권 조회 API 연동)
REGION_FLIGHT_DATA = {
    "국내": {
        "flights": [
            {"airline": "대한항공", "price": 89000, "depart_time": "08:00", "arrive_time": "09:10", "duration": "1시간 10분"},
            {"airline": "제주항공", "price": 65000, "depart_time": "11:30", "arrive_time": "12:40", "duration": "1시간 10분"},
            {"airline": "아시아나항공", "price": 95000, "depart_time": "15:20", "arrive_time": "16:30", "duration": "1시간 10분"},
        ],
        "monthly": {
            "1월": 75000, "2월": 82000, "3월": 68000, "4월": 65000,
            "5월": 90000, "6월": 95000, "7월": 120000, "8월": 130000,
            "9월": 70000, "10월": 68000, "11월": 60000, "12월": 88000,
        },
    },
    "아시아": {
        "flights": [
            {"airline": "제주항공", "price": 259000, "depart_time": "07:30", "arrive_time": "09:50", "duration": "2시간 20분 (직항)"},
            {"airline": "대한항공", "price": 385000, "depart_time": "13:00", "arrive_time": "15:30", "duration": "2시간 30분 (직항)"},
            {"airline": "아시아나항공", "price": 340000, "depart_time": "19:10", "arrive_time": "21:40", "duration": "2시간 30분 (직항)"},
        ],
        "monthly": {
            # 동남아/일본은 겨울철(12~2월)이 건기 성수기라 오히려 비싸고,
            # 장마가 끝난 초가을(9월)이 대표적인 비수기
            "1월": 380000, "2월": 400000, "3월": 330000, "4월": 300000,
            "5월": 280000, "6월": 260000, "7월": 420000, "8월": 450000,
            "9월": 230000, "10월": 260000, "11월": 290000, "12월": 410000,
        },
    },
    "유럽": {
        "flights": [
            {"airline": "대한항공", "price": 1450000, "depart_time": "13:30", "arrive_time": "19:20", "duration": "12시간 50분 (직항)"},
            {"airline": "아시아나항공", "price": 1380000, "depart_time": "21:00", "arrive_time": "익일 03:10", "duration": "13시간 10분 (직항)"},
            {"airline": "루프트한자", "price": 1190000, "depart_time": "10:20", "arrive_time": "18:40", "duration": "15시간 20분 (경유 1회)"},
        ],
        "monthly": {
            # 유럽은 여름 성수기(6~8월)와 연말(12월)이 가장 비싸고,
            # 연말연시가 지난 직후인 2월이 대표적인 비수기
            "1월": 1300000, "2월": 1050000, "3월": 1220000, "4월": 1280000,
            "5월": 1400000, "6월": 1650000, "7월": 1900000, "8월": 1950000,
            "9월": 1350000, "10월": 1200000, "11월": 1150000, "12월": 1700000,
        },
    },
    "미주": {
        "flights": [
            {"airline": "대한항공", "price": 1350000, "depart_time": "10:20", "arrive_time": "익일 08:40", "duration": "13시간 20분 (직항)"},
            {"airline": "아시아나항공", "price": 1280000, "depart_time": "22:00", "arrive_time": "익일 05:30", "duration": "14시간 10분 (직항)"},
            {"airline": "델타항공", "price": 990000, "depart_time": "14:50", "arrive_time": "익일 16:15", "duration": "17시간 50분 (경유 1회)"},
        ],
        "monthly": {
            # 미주는 여름 성수기(6~8월)와 추수감사절/연말(11~12월)이 비싸고,
            # 봄방학 전인 3월이 대표적인 비수기
            "1월": 1150000, "2월": 1180000, "3월": 920000, "4월": 1150000,
            "5월": 1080000, "6월": 1250000, "7월": 1550000, "8월": 1620000,
            "9월": 980000, "10월": 1050000, "11월": 1300000, "12월": 1500000,
        },
    },
    "오세아니아": {
        "flights": [
            {"airline": "대한항공", "price": 1050000, "depart_time": "20:30", "arrive_time": "익일 07:40", "duration": "10시간 10분 (직항)"},
            {"airline": "콴타스항공", "price": 980000, "depart_time": "23:10", "arrive_time": "익일 09:30", "duration": "9시간 20분 (직항)"},
        ],
        "monthly": {
            "1월": 950000, "2월": 900000, "3월": 850000, "4월": 820000,
            "5월": 800000, "6월": 780000, "7월": 950000, "8월": 900000,
            "9월": 830000, "10월": 850000, "11월": 900000, "12월": 1250000,
        },
    },
    # 위 목록에 없는 해외 도시(예: 중동, 아프리카 등)를 위한 대략치
    "기타 해외": {
        "flights": [
            {"airline": "대한항공", "price": 1200000, "depart_time": "10:20", "arrive_time": "익일 08:40", "duration": "약 13시간 (직항 기준, 목적지에 따라 변동)"},
            {"airline": "아시아나항공", "price": 1150000, "depart_time": "22:00", "arrive_time": "익일 05:30", "duration": "약 14시간 (직항 기준, 목적지에 따라 변동)"},
        ],
        "monthly": {
            # 상세 데이터가 없는 지역이라 뚜렷한 성수기 없이 완만하게 변동, 초가을(10월)이 최저
            "1월": 1050000, "2월": 1080000, "3월": 1000000, "4월": 980000,
            "5월": 1030000, "6월": 1150000, "7월": 1350000, "8월": 1400000,
            "9월": 1020000, "10월": 880000, "11월": 950000, "12월": 1250000,
        },
    },
}


# 권역별 호텔 데이터 (실제로는 숙박 예약 API 연동). 국내는 한국식 숙소 스타일/가격대를 쓰고,
# 해외는 권역별 물가 수준과 위치 표현(해변가 가정 없이 범용적으로)을 다르게 적용합니다.
REGION_HOTEL_DATA = {
    "국내": [
        {"name": "오션뷰 호텔", "price": 120000, "rating": 4.5, "location_suffix": "해변가"},
        {"name": "시티 비즈니스 호텔", "price": 78000, "rating": 4.1, "location_suffix": "시내 중심가"},
        {"name": "게스트하우스 온기", "price": 45000, "rating": 4.3, "location_suffix": "구시가지"},
    ],
    "아시아": [
        {"name": "그랜드 아시아 호텔", "price": 95000, "rating": 4.4, "location_suffix": "시내 중심가"},
        {"name": "리버사이드 부티크 호텔", "price": 130000, "rating": 4.6, "location_suffix": "강변"},
        {"name": "백패커스 인", "price": 55000, "rating": 4.0, "location_suffix": "올드타운"},
    ],
    "유럽": [
        {"name": "그랜드 플라자 호텔", "price": 320000, "rating": 4.6, "location_suffix": "구시가지"},
        {"name": "부티크 헤리티지 호텔", "price": 280000, "rating": 4.4, "location_suffix": "시내 중심가"},
        {"name": "시티 호스텔", "price": 130000, "rating": 4.0, "location_suffix": "중앙역 근처"},
    ],
    "미주": [
        {"name": "다운타운 그랜드 호텔", "price": 350000, "rating": 4.5, "location_suffix": "다운타운"},
        {"name": "리버티 인", "price": 260000, "rating": 4.2, "location_suffix": "시내 중심가"},
        {"name": "버짓 스테이 호텔", "price": 150000, "rating": 3.9, "location_suffix": "공항 근처"},
    ],
    "오세아니아": [
        {"name": "하버뷰 호텔", "price": 300000, "rating": 4.5, "location_suffix": "항구 근처"},
        {"name": "시티 센트럴 호텔", "price": 240000, "rating": 4.3, "location_suffix": "시내 중심가"},
        {"name": "백패커스 로지", "price": 120000, "rating": 4.0, "location_suffix": "해변가"},
    ],
    "기타 해외": [
        {"name": "그랜드 시티 호텔", "price": 220000, "rating": 4.3, "location_suffix": "시내 중심가"},
        {"name": "부티크 인", "price": 170000, "rating": 4.1, "location_suffix": "구시가지"},
    ],
}


def _get_region(departure: Optional[str], destination: Optional[str]) -> str:
    """도착지를 우선으로, 없으면 출발지를 기준으로 가격 산정용 권역을 판단합니다.
    (화면에는 노출되지 않고, 어떤 항공/숙박 가격 데이터를 쓸지 결정하는 데만 사용됩니다.)"""
    for city in (destination, departure):
        if not city:
            continue
        info = CITY_INFO.get(city)
        if info:
            return info[1]

    # CITY_INFO에 없는 도시가 하나라도 주어졌다면 '기타 해외'로 취급
    if departure or destination:
        return "기타 해외"

    return "국내"


def _get_display_name(city: Optional[str]) -> Optional[str]:
    """도시 이름을 '국가 도시' 형태로 반환합니다. 알려진 도시가 아니면 도시 이름 그대로 반환합니다.
    괌처럼 국가 표기 자체에 도시 이름이 이미 포함된 경우(예: '괌(미국령)')는 중복 없이 그대로 반환합니다."""
    if not city:
        return None
    info = CITY_INFO.get(city)
    if not info:
        return city
    country = info[0]
    if city in country:
        return country
    return f"{country} {city}"


def _get_english_name(city: Optional[str]) -> Optional[str]:
    """아고다 검색 쿼리용 영문 도시명을 반환합니다. 알려진 도시가 아니면 원래 이름 그대로 반환합니다."""
    if not city:
        return None
    info = CITY_INFO.get(city)
    return info[2] if info else city


# 광고/사이트 메뉴/푸터/예약 위젯 UI에 흔히 등장하는 문구. 검색 결과 본문에서 이 지점 이후는 잘라냅니다.
_SEARCH_NOISE_MARKERS = [
    "Primary Logo", "Site secondary logo", "Image 1:",
    "도움말 센터", "자주 묻는 질문", "개인정보 처리방침", "이용 약관",
    "회사 소개", "채용 정보", "숙소 등록", "eSIM",
    "엔터 키를", "쿠키 및 기타 추적", "체크아웃\n\n성인",
]


def _clean_search_hits(
    hits: list, url_marker: Optional[str] = None, required_terms: Optional[list] = None
) -> list:
    """아고다/트립어드바이저 등 실시간 검색 결과 중 실제로 쓸만한 페이지만 남기고,
    사이트 홈/메뉴/검색창/푸터 같은 광고성·내비게이션 텍스트는 걸러냅니다.

    검색 엔진이 관련 페이지를 못 찾으면 URL 패턴은 맞지만 완전히 다른 도시의
    결과를 섞어서 줄 때가 있어(예: '토론토'를 검색했는데 도쿄/프랑스 호텔이 나옴),
    required_terms(사용자가 실제로 물어본 도시명의 한글/영문)가 제목이나 URL
    어디에도 없는 결과는 제외합니다. (페이지 언어가 한글/영문/기타 언어로 섞여
    나올 수 있어 제목과 URL 둘 다 확인합니다.)

    url_marker: 상세 페이지 URL에만 포함되는 경로 조각 (예: 호텔은 '/hotel/', 항공편은 '/flights/airport/').
        None이면 URL 패턴으로는 거르지 않습니다 (예: 트립어드바이저는 목록형 페이지도 유용한 정보를 담고 있음).
    required_terms: 제목 또는 URL에 하나라도 포함되어야 하는 문자열 목록 (예: [도착 도시명(한글), 도착 도시명(영문)])
    """
    cleaned = []
    for hit in hits:
        url = hit.get("url", "")
        if url_marker and url_marker not in url:
            continue

        title = (hit.get("title") or "").strip()
        content = (hit.get("content") or "").strip()

        # 실제로 검색한 도시/지역과 무관한 결과(엉뚱한 도시)는 제외
        if required_terms:
            haystack = f"{title} {url}".lower()
            if not any(term and term.lower() in haystack for term in required_terms):
                continue

        # content가 "Title: {제목}"으로 시작하며 제목을 그대로 반복하는 경우 정리
        prefix = f"Title: {title}"
        if title and content.startswith(prefix):
            content = content[len(prefix):].lstrip("\n# ").strip()

        # 메뉴/푸터성 문구가 나오는 지점부터는 잘라내서 광고/내비게이션 텍스트 제거
        for marker in _SEARCH_NOISE_MARKERS:
            idx = content.find(marker)
            if idx != -1:
                content = content[:idx].strip()

        cleaned.append({"title": title or "제목 없음", "url": url, "content": content})
    return cleaned


AGODA_SOURCE_NOTE = "\n출처: Agoda (agoda.com) 실시간 검색 결과\n"
TRIPADVISOR_SOURCE_NOTE = "\n출처: Tripadvisor (tripadvisor.com) 실시간 검색 결과\n"


def _fallback_flight_list(
    departure: Optional[str],
    departure_label: str,
    destination_label: str,
    departure_date: Optional[str],
    region: str,
) -> str:
    """아고다 실시간 검색이 실패했거나 결과가 없을 때 사용하는 예시 항공편 목록."""
    flights = REGION_FLIGHT_DATA[region]["flights"]

    date_label = f" ({departure_date})" if departure_date else ""
    result = f"[항공편 검색 결과 - 예시 데이터] {departure_label} → {destination_label}{date_label}\n\n"
    for f in flights:
        result += (
            f"- {f['airline']} | {f['price']:,}원 | "
            f"{f['depart_time']} 출발 → {f['arrive_time']} 도착 | 소요시간: {f['duration']}\n"
        )
    if not departure:
        result += "\n※ 출발지가 지정되지 않아 참고용 예시 항공편입니다. 출발지를 알려주시면 정확한 항공편을 안내해드릴 수 있습니다.\n"
    if region == "기타 해외":
        result += "\n※ 이 도시는 상세 데이터가 준비되어 있지 않아 대략적인 가격입니다. 실제 가격은 도시에 따라 달라질 수 있습니다.\n"
    result += "\n※ 아고다 실시간 검색 결과를 가져오지 못해 참고용 예시 데이터로 대체했습니다.\n"
    return result


@tool(parse_docstring=True)
def search_flights(
    departure: Optional[str] = None,
    destination: Optional[str] = None,
    departure_date: Optional[str] = None,
) -> str:
    """아고다(Agoda)에서 출발지, 도착지, 출발일을 기준으로 항공편을 검색합니다.
    출발지와 도착지가 둘 다 주어지지 않으면 인기 여행지를 추천합니다.
    둘 중 하나만 있어도 그 정보를 살려서 항공편을 검색합니다.
    아고다 검색 결과를 가져오지 못하면 참고용 예시 데이터로 대체합니다.
    과거 월별 가격 데이터를 비교하여 가장 저렴한 시기도 함께 안내합니다.

    Args:
        departure: 출발지 (예: '서울'). 모르면 비워두세요
        destination: 도착지 (예: '제주', '도쿄', '파리', '뉴욕'). 모르면 비워두세요
        departure_date: 출발일 (예: '2026-10-05'). 지정하지 않아도 됩니다

    Returns:
        아고다 검색 결과(항공편 요약/링크, 둘 다 없으면 인기 여행지 추천)와 월별 가격 비교를 통한 최저가 시기 안내
    """
    try:
        region = _get_region(departure, destination)
        monthly_price_history = REGION_FLIGHT_DATA[region]["monthly"]

        cheapest_month = min(monthly_price_history, key=monthly_price_history.get)
        cheapest_price = monthly_price_history[cheapest_month]

        price_trend = "[월별 평균 항공권 가격 비교]\n"
        for month, price in monthly_price_history.items():
            marker = " ← 최저가 시기" if month == cheapest_month else ""
            price_trend += f"- {month}: {price:,}원{marker}\n"
        price_trend += f"\n과거 가격을 비교했을 때 {cheapest_month}이 평균 {cheapest_price:,}원으로 가장 저렴합니다.\n"

        # 출발지, 도착지 둘 다 없을 때만 인기 여행지 추천으로 대체
        # (둘 중 하나라도 있으면 그 정보를 살려서 항공편을 검색해야 하므로 and로 판단)
        if not departure and not destination:
            popular_destinations = [
                {"destination": "제주", "reason": "국내 최고 인기 여행지, 사계절 다양한 명소", "avg_price": 68000},
                {"destination": "부산", "reason": "해운대, 감천문화마을 등 도심+바다 여행", "avg_price": 55000},
                {"destination": "강릉", "reason": "커피거리, 동해 바다 힐링 여행", "avg_price": 60000},
                {"destination": "여수", "reason": "야경 명소와 해상 케이블카", "avg_price": 58000},
            ]

            result = "[출발지/도착지 미입력] 인기 여행지를 추천해드립니다.\n\n"
            for p in popular_destinations:
                result += f"- {p['destination']} | {p['reason']} | 평균 항공권 가격: {p['avg_price']:,}원\n"
            result += f"\n{price_trend}"
            return result

        # 출발지 또는 도착지 중 하나라도 있으면, 아는 정보는 살리고 나머지는 '미정'으로 표시하여 항공편 검색
        departure_label = _get_display_name(departure) or "출발지 미정"
        destination_label = _get_display_name(destination) or "도착지 미정"
        date_label = f" ({departure_date})" if departure_date else ""

        # 아고다 페이지는 한글보다 영문 도시명 검색에 훨씬 정확하게 매칭되는 경우가 많음
        # (예: '서울 로마 항공권'은 관련 없는 노선이 나오지만 'Seoul Rome flight'는 정확히 나옴)
        departure_en = _get_english_name(departure) or ""
        destination_en = _get_english_name(destination) or ""

        # max_results를 넉넉히 주고 search_depth를 advanced로 해야 실제 상세 페이지가
        # 후보에 포함될 확률이 높아짐 (기본 검색은 도시 랜딩 페이지만 주는 경우가 많음)
        agoda_search = TavilySearch(
            max_results=10,
            search_depth="advanced",
            include_domains=["agoda.com"],
        )
        search_result = agoda_search.invoke(
            {"query": f"{departure_en} {destination_en} flight".strip()}
        )
        hits = search_result.get("results", []) if isinstance(search_result, dict) else []
        # 출발지는 대부분의 국내발 노선에 공통으로 등장해 변별력이 없으므로,
        # 도착지(있으면)를 우선 검증 기준으로 삼고, 도착지가 없을 때만 출발지로 검증
        primary_city = destination or departure
        primary_city_en = destination_en or departure_en
        cleaned = _clean_search_hits(
            hits, "/flights/airport/", required_terms=[primary_city, primary_city_en]
        )

        if not cleaned:
            result = _fallback_flight_list(departure, departure_label, destination_label, departure_date, region)
            result += f"\n{price_trend}"
            return result

        result = f"[항공편 검색 결과 - Agoda] {departure_label} → {destination_label}{date_label}\n\n"
        for hit in cleaned:
            snippet = hit["content"][:150]
            result += f"- {hit['title']}\n  {snippet}{'...' if snippet else ''}\n  🔗 {hit['url']}\n\n"
        result += AGODA_SOURCE_NOTE
        result += f"\n{price_trend}"
        return result
    except Exception as e:
        region = _get_region(departure, destination)
        departure_label = _get_display_name(departure) or "출발지 미정"
        destination_label = _get_display_name(destination) or "도착지 미정"
        fallback = _fallback_flight_list(departure, departure_label, destination_label, departure_date, region)
        return f"{fallback}\n(실시간 검색 오류: {str(e)})"


def _fallback_hotel_list(city: str, city_label: str, check_in: str, check_out: str, guests: int) -> str:
    """아고다 실시간 검색이 실패했거나 결과가 없을 때 사용하는 예시 숙소 목록."""
    region = _get_region(None, city)
    hotels = REGION_HOTEL_DATA[region]

    result = f"[호텔 검색 결과 - 예시 데이터] {city_label} | {check_in} ~ {check_out} | 인원: {guests}명\n\n"
    for h in hotels:
        result += f"- {h['name']} | 1박 {h['price']:,}원 | 평점 {h['rating']} | 위치: {city} {h['location_suffix']}\n"
    result += "\n※ 아고다 실시간 검색 결과를 가져오지 못해 참고용 예시 데이터로 대체했습니다.\n"
    return result


@tool(parse_docstring=True)
def search_hotels(city: str, check_in: str, check_out: str, guests: int) -> str:
    """아고다(Agoda)에서 도시와 체크인/체크아웃 날짜, 인원수에 맞는 실제 호텔을 검색합니다.
    사용자가 입력한 그 도시(와 국가) 기준으로 아고다 사이트만 검색해서 결과를 가져옵니다.
    검색 결과를 가져오지 못하면 참고용 예시 데이터로 대체합니다.

    Args:
        city: 숙소를 찾을 도시 (예: '부산', '로마')
        check_in: 체크인 날짜 (예: '2026-10-05')
        check_out: 체크아웃 날짜 (예: '2026-10-07')
        guests: 투숙 인원수

    Returns:
        아고다 검색 결과(호텔명, 요약, 링크) 목록 또는 예시 데이터, 오류 메시지
    """
    try:
        city_label = _get_display_name(city) or city
        city_en = _get_english_name(city) or city

        # 체크인 날짜/인원수 같은 부가 텍스트를 쿼리에 넣으면 오히려 관련 없는 결과가
        # 섞여서 나오는 경우가 많아, 검색어는 "영문 도시명 + hotel"로 단순하게 유지합니다.
        # max_results를 넉넉히 주고 search_depth를 advanced로 해야 실제 상세 페이지가
        # 후보에 포함될 확률이 높아짐 (기본 검색은 도시 랜딩 페이지만 주는 경우가 많음)
        agoda_search = TavilySearch(
            max_results=10,
            search_depth="advanced",
            include_domains=["agoda.com"],
        )
        search_result = agoda_search.invoke({"query": f"{city_en} hotel"})
        hits = search_result.get("results", []) if isinstance(search_result, dict) else []
        cleaned = _clean_search_hits(hits, "/hotel/", required_terms=[city, city_en])

        if not cleaned:
            return _fallback_hotel_list(city, city_label, check_in, check_out, guests)

        result = f"[호텔 검색 결과 - Agoda] {city_label} | {check_in} ~ {check_out} | 인원: {guests}명\n\n"
        for hit in cleaned:
            snippet = hit["content"][:150]
            result += f"- {hit['title']}\n  {snippet}{'...' if snippet else ''}\n  🔗 {hit['url']}\n\n"
        result += AGODA_SOURCE_NOTE
        return result
    except Exception as e:
        # 아고다 검색 자체가 실패해도(API 오류 등) 예시 데이터로 대체하여 흐름이 끊기지 않도록 함
        city_label = _get_display_name(city) or city
        fallback = _fallback_hotel_list(city, city_label, check_in, check_out, guests)
        return f"{fallback}\n(실시간 검색 오류: {str(e)})"


_ATTRACTION_CATEGORY_QUERY = {
    "맛집": "restaurants best",
    "명소": "attractions things to do",
    "액티비티": "activities things to do",
}


def _fallback_attractions_list(city: str, city_label: str, category: Optional[str]) -> str:
    """트립어드바이저 실시간 검색이 실패했거나 결과가 없을 때 사용하는 예시 관광지 목록."""
    attractions = {
        "맛집": [
            {"name": f"{city} 향토음식점", "desc": "현지인이 추천하는 전통 맛집", "hours": "10:00 - 21:00", "closed": "매주 월요일"},
        ],
        "명소": [
            {"name": f"{city} 전망대", "desc": "도시 전경을 한눈에 볼 수 있는 명소", "hours": "09:00 - 18:00", "closed": "매주 화요일"},
        ],
        "액티비티": [
            {"name": f"{city} 체험 마을", "desc": "지역 문화를 체험할 수 있는 액티비티", "hours": "10:00 - 17:00", "closed": "연중무휴"},
        ],
    }

    if category:
        places = attractions[category]
        result = f"[관광지 정보 - 예시 데이터] {city_label} | 카테고리: {category}\n\n"
    else:
        places = [p for items in attractions.values() for p in items]
        result = f"[관광지 정보 - 예시 데이터] {city_label} | 전체\n\n"

    for p in places:
        result += f"- {p['name']} | {p['desc']} | 운영시간: {p['hours']} | 휴무일: {p['closed']}\n"
    result += "\n※ 트립어드바이저 실시간 검색 결과를 가져오지 못해 참고용 예시 데이터로 대체했습니다.\n"
    return result


@tool(parse_docstring=True)
def get_tourist_attractions(city: str, category: Optional[str] = None) -> str:
    """트립어드바이저(Tripadvisor)에서 그 도시의 실제로 유명한 관광지/맛집/액티비티를 검색합니다.
    검색 결과를 가져오지 못하면 참고용 예시 데이터로 대체합니다.

    Args:
        city: 관광지를 조회할 도시 (예: '경주', '로마')
        category: 관심 카테고리 ('맛집', '명소', '액티비티'). 지정하지 않으면 명소 기준으로 검색

    Returns:
        트립어드바이저에서 찾은 실제 장소명/설명/링크 목록 또는 예시 데이터, 오류 메시지
    """
    try:
        city_label = _get_display_name(city) or city
        city_en = _get_english_name(city) or city

        if category and category not in _ATTRACTION_CATEGORY_QUERY:
            available = ", ".join(_ATTRACTION_CATEGORY_QUERY.keys())
            return f"오류: '{category}' 카테고리를 찾을 수 없습니다. 사용 가능한 카테고리: {available}"

        query_suffix = _ATTRACTION_CATEGORY_QUERY.get(category, _ATTRACTION_CATEGORY_QUERY["명소"])

        tripadvisor_search = TavilySearch(
            max_results=10,
            search_depth="advanced",
            include_domains=["tripadvisor.com"],
        )
        search_result = tripadvisor_search.invoke({"query": f"{city_en} {query_suffix}"})
        hits = search_result.get("results", []) if isinstance(search_result, dict) else []
        # 트립어드바이저는 개별 장소 리뷰 페이지뿐 아니라 "베스트 목록" 페이지의 요약문에도
        # 실제 유명 장소명이 여러 개 들어있어 유용하므로, URL 패턴으로는 거르지 않고
        # 도시명이 제목/URL에 있는지만 확인합니다.
        cleaned = _clean_search_hits(hits, required_terms=[city, city_en])

        if not cleaned:
            return _fallback_attractions_list(city, city_label, category)

        category_label = category or "명소"
        result = f"[관광지 검색 결과 - Tripadvisor] {city_label} | 카테고리: {category_label}\n\n"
        for hit in cleaned:
            snippet = hit["content"][:200]
            result += f"- {hit['title']}\n  {snippet}{'...' if snippet else ''}\n  🔗 {hit['url']}\n\n"
        result += TRIPADVISOR_SOURCE_NOTE
        return result
    except Exception as e:
        city_label = _get_display_name(city) or city
        fallback = _fallback_attractions_list(city, city_label, category)
        return f"{fallback}\n(실시간 검색 오류: {str(e)})"


# ============================================
# 파일 시스템 도구 (코딩 에이전트 예시)
# ============================================

@tool(parse_docstring=True)
def read_file(file_path: str) -> str:
    """파일의 내용을 읽어서 반환합니다.

    Args:
        file_path: 읽을 파일의 경로 (상대 경로 또는 절대 경로)

    Returns:
        파일 내용 또는 오류 메시지
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        line_count = len(content.split("\n"))
        return f"파일: {file_path}\n총 {line_count}줄\n\n{content}"
    except FileNotFoundError:
        return f"오류: 파일을 찾을 수 없습니다: {file_path}"
    except PermissionError:
        return f"오류: 파일에 대한 읽기 권한이 없습니다: {file_path}"
    except Exception as e:
        return f"오류: {str(e)}"


@tool(parse_docstring=True)
def write_file(file_path: str, content: str) -> str:
    """파일에 내용을 작성합니다. 파일이 없으면 생성하고, 있으면 덮어씁니다.

    Args:
        file_path: 작성할 파일의 경로
        content: 파일에 쓸 내용

    Returns:
        성공 메시지 또는 오류 메시지
    """
    try:
        # 디렉터리가 없으면 생성
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        line_count = len(content.split("\n"))
        return f"성공: 파일이 작성되었습니다: {file_path} (총 {line_count}줄)"
    except PermissionError:
        return f"오류: 파일에 대한 쓰기 권한이 없습니다: {file_path}"
    except Exception as e:
        return f"오류: {str(e)}"


@tool(parse_docstring=True)
def delete_file(file_path: str) -> str:
    """파일을 삭제합니다.

    Args:
        file_path: 삭제할 파일의 경로

    Returns:
        성공 메시지 또는 오류 메시지
    """
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            return f"성공: 파일이 삭제되었습니다: {file_path}"
        else:
            return f"오류: 파일을 찾을 수 없습니다: {file_path}"
    except PermissionError:
        return f"오류: 파일에 대한 삭제 권한이 없습니다: {file_path}"
    except Exception as e:
        return f"오류: {str(e)}"


@tool(parse_docstring=True)
def create_directory(dir_path: str) -> str:
    """새로운 디렉터리를 생성합니다.

    Args:
        dir_path: 생성할 디렉터리의 경로

    Returns:
        성공 메시지 또는 오류 메시지
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return f"성공: 디렉터리가 생성되었습니다: {dir_path}"
    except PermissionError:
        return f"오류: 디렉터리 생성 권한이 없습니다: {dir_path}"
    except Exception as e:
        return f"오류: {str(e)}"


@tool(parse_docstring=True)
def list_directory(dir_path: str = ".") -> str:
    """디렉터리의 파일과 폴더 목록을 반환합니다.

    Args:
        dir_path: 조회할 디렉터리 경로 (기본값: 현재 디렉터리)

    Returns:
        파일 및 폴더 목록 또는 오류 메시지
    """
    try:
        if not os.path.exists(dir_path):
            return f"오류: 디렉터리를 찾을 수 없습니다: {dir_path}"

        if not os.path.isdir(dir_path):
            return f"오류: {dir_path}는 디렉터리가 아닙니다"

        items = os.listdir(dir_path)

        if not items:
            return f"디렉터리가 비어있습니다: {dir_path}"

        # 파일과 폴더 분류
        folders = []
        files = []

        for item in sorted(items):
            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path):
                folders.append(f"[폴더] {item}/")
            else:
                size = os.path.getsize(item_path)
                files.append(f"[파일] {item} ({size} bytes)")

        result = f"디렉터리: {dir_path}\n\n"

        if folders:
            result += "폴더:\n" + "\n".join(folders) + "\n\n"

        if files:
            result += "파일:\n" + "\n".join(files)

        return result

    except PermissionError:
        return f"오류: 디렉터리에 대한 읽기 권한이 없습니다: {dir_path}"
    except Exception as e:
        return f"오류: {str(e)}"


@tool(parse_docstring=True)
def execute_python_code(code: str) -> str:
    """Python 코드를 실행하고 결과를 반환합니다.

    Args:
        code: 실행할 Python 코드 문자열

    Returns:
        코드 실행 결과 또는 오류 메시지
    """
    try:
        # 보안상의 이유로 제한된 환경에서 실행
        # 실제 프로덕션에서는 샌드박스 환경 사용 권장
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.getcwd()
        )

        output_parts = []

        if result.stdout:
            output_parts.append(f"출력:\n{result.stdout.strip()}")

        if result.stderr:
            output_parts.append(f"오류:\n{result.stderr.strip()}")

        if result.returncode == 0:
            if output_parts:
                return "실행 성공\n\n" + "\n\n".join(output_parts)
            else:
                return "실행 성공 (출력 없음)"
        else:
            return f"실행 실패 (종료 코드: {result.returncode})\n\n" + "\n\n".join(output_parts)

    except subprocess.TimeoutExpired:
        return "오류: 코드 실행 시간이 10초를 초과했습니다."
    except Exception as e:
        return f"오류: {str(e)}"


# 항공사별 예약 사이트 (실제 항공사 공식 홈페이지)
AIRLINE_BOOKING_SITES = {
    "대한항공": "https://www.koreanair.com",
    "제주항공": "https://www.jejuair.net",
    "아시아나항공": "https://flyasiana.com",
}


@tool(parse_docstring=True)
def confirm_booking(
    booking_type: str,
    item_name: str,
    date: str,
    price: int,
    booking_url: Optional[str] = None,
    check_out: Optional[str] = None,
    guests: Optional[int] = None,
) -> str:
    """항공권 또는 호텔 예약을 확정하고, 실제 예약을 진행할 수 있는 사이트를 안내합니다.
    이 도구는 결제를 대신 진행하지 않으며, 사용자가 직접 예약을 완료할 사이트만 안내합니다.
    호텔의 경우 search_hotels 결과에 있던 실제 아고다 호텔 페이지 URL을 booking_url로
    전달하면, 체크인/체크아웃 날짜와 인원수가 미리 채워진 링크를 만들어줍니다.

    Args:
        booking_type: 예약 종류 ('항공권' 또는 '호텔')
        item_name: 예약할 대상 이름 (예: '대한항공', 'Riu Plaza Toronto')
        date: 항공권은 출발일, 호텔은 체크인 날짜 (예: '2026-10-05')
        price: 예약 금액(원)
        booking_url: (호텔 전용) search_hotels 결과에 있던 그 호텔의 실제 아고다 URL을
            그대로 전달하세요. 지정하지 않으면 아고다 검색 링크로 대체합니다.
        check_out: (호텔 전용) 체크아웃 날짜 (예: '2026-10-08')
        guests: (호텔 전용) 투숙 인원수

    Returns:
        예약 안내 메시지(가능하면 날짜/인원이 미리 채워진 링크 포함) 또는 오류 메시지
    """
    try:
        from urllib.parse import quote, urlencode

        if booking_type == "항공권":
            url = AIRLINE_BOOKING_SITES.get(item_name)
            if not url:
                url = f"https://www.google.com/search?q={quote(item_name + ' 항공권 예약')}"
            date_range = date
        else:
            date_range = f"{date} ~ {check_out}" if check_out else date

            if booking_url:
                # 실제 호텔 페이지 URL에 체크인/체크아웃/인원 정보를 쿼리 파라미터로 덧붙여
                # 예약 페이지가 해당 조건으로 미리 채워진 채 열리도록 함
                params = {"checkIn": date}
                if check_out:
                    params["checkOut"] = check_out
                if guests:
                    params["adults"] = guests
                    params["rooms"] = 1
                separator = "&" if "?" in booking_url else "?"
                url = f"{booking_url}{separator}{urlencode(params)}"
            else:
                # 실제 호텔 페이지 URL이 없으면 검색 링크로 대체
                url = f"https://www.agoda.com/search?q={quote(item_name)}"

        result = (
            f"[예약 안내] {booking_type} - {item_name}\n"
            f"날짜: {date_range} | 예상 금액: {price:,}원\n\n"
            f"아래 사이트에서 예약을 완료해주세요:\n"
            f"🔗 {url}"
        )
        if booking_type != "항공권" and not booking_url:
            result += "\n\n※ 특정 호텔 페이지 링크가 없어 검색 링크로 대체했습니다. 원하시는 정확한 페이지는 직접 찾아 확인해주세요."
        return result
    except Exception as e:
        return f"오류: {str(e)}"


CUSTOM_TOOLS = [
    search_flights,
    search_hotels,
    get_tourist_attractions,
    confirm_booking,
]

FILE_TOOLS = [
    read_file,
    write_file,
    delete_file,
    create_directory,
    list_directory,
    execute_python_code
]
