"""Build ko/en two-page CV PDFs from one template."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1])

CSS = """
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Noto Sans CJK KR','Noto Sans KR',sans-serif;color:#1E2422;font-size:9.2pt;line-height:1.5;width:210mm;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.sheet{display:grid;grid-template-columns:66mm 1fr;height:297mm;overflow:hidden;break-after:page;page-break-after:always}
.sheet:last-child{break-after:auto;page-break-after:auto}
aside{background:#00462A;color:#fff;padding:0 7mm 8mm}
.mono{background:none;color:#fff;width:34mm;height:22mm;margin:0 auto;display:grid;place-items:center;font-size:24pt;font-weight:900;letter-spacing:.02em}
.mono.sm{width:20mm;height:13mm;font-size:14pt;margin:0}
aside h3{font-size:11.5pt;font-weight:700;margin:9mm 0 2.5mm;letter-spacing:.04em}
aside p,aside li{font-size:8.7pt;line-height:1.6;color:#E6F0EA}
aside ul{list-style:none}
aside li{margin:.9mm 0}
aside li b{color:#fff;font-weight:700}
aside .k{display:block;font-weight:700;color:#fff;margin-top:2mm;font-size:8.7pt}
aside a{color:#fff;text-decoration:none}
main{padding:11mm 10mm 0 9mm}
.name{font-size:26pt;font-weight:900;letter-spacing:-.01em;line-height:1.15}
.role{font-size:12pt;margin-top:1mm;padding-bottom:3mm;border-bottom:1.5px solid #00462A;width:80%}
.cont{font-size:9pt;color:#5A6472;padding-bottom:3mm;border-bottom:1.5px solid #00462A;width:80%;letter-spacing:.04em}
.cont b{color:#1E2422;font-size:12pt;letter-spacing:0;margin-right:6px}
h2{font-size:12.5pt;font-weight:900;margin:6mm 0 2mm;letter-spacing:.02em}
.summary{font-size:9.3pt}
.item{margin-top:2.6mm}
.item .t{font-weight:700;font-size:9.6pt}
.item .t span{font-weight:400;color:#5A6472;font-size:9pt}
.item .st{font-size:8.6pt;color:#5A6472;margin-top:.3mm}
ul.b{margin:.8mm 0 0 7mm}
ul.b li{margin:.45mm 0}
.awards div{display:grid;grid-template-columns:11mm 1fr;gap:2mm;padding:.6mm 0}
.awards b{font-weight:700}
.awards span:first-child{font-weight:700}
.other{margin-top:1mm}
.other div{display:grid;grid-template-columns:22mm 1fr;gap:3mm;padding:1.6mm 0;border-bottom:1px solid #E6EAF0}
.other b{font-weight:700}
.other small{display:block;color:#5A6472;font-size:8.4pt}
"""


def items(lst):
    return "".join(
        f'<div class="item"><div class="t">{p[0]} <span>| {p[1]} · {p[2]}</span></div>'
        f'<div class="st">{p[3]}</div>'
        f'<ul class="b">{"".join(f"<li>{b}</li>" for b in p[4])}</ul></div>' for p in lst)


def page(d):
    awards = "".join(f"<div><span>{a[0]}</span><span>{a[1]} <b>({a[2]})</b></span></div>" for a in d["awards"])
    skills = "".join(f'<span class="k">{k}</span><p>{v}</p>' for k, v in d["skills"])
    other = "".join(f"<div><b>{o[0]}</b><span>{o[1]}<small>{o[2]}</small></span></div>" for o in d["other"])
    links = "".join(f"<li><b>{n}</b><br>{u}</li>" for n, u in d["links"])
    return f"""<!doctype html><html lang="{d['lang']}"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="sheet"><aside>
<div class="mono"><svg viewBox="0 0 64 36" style="width:78%;height:auto;display:block"><g transform="matrix(-1 0 0 1 36 0)"><path fill="#fff" d="M10.478 22.439s.702 2.281-.337 7.993c-.186 1.025-.46 2.072-.599 2.93-1.757 0-1.851 2.002-1.478 2.002h2.094c1.337 0 2.971-3.334 3.854-7.961s-3.534-4.964-3.534-4.964zm13.042 3.702s2.272 1.22 2.188 4.081c-.033 1.131-.249 2.091-.355 3.024-1.832 0-1.839 1.985-1.305 1.985h1.856c.923 0 3.001-3.158 3.379-7.281.379-4.122-5.763-1.809-5.763-1.809z M36 8.447C36 3.525 31.859 1 27 1a1 1 0 1 0 0 2c1.804 0 6.717.934 6.717 5.447 0 2.881-1.567 5.462-3.77 5.982-.164-.073-.345-.104-.509-.192-7.239-3.917-13.457.902-15.226-.29-1.752-1.182-.539-3.255-2.824-5.243-.33-1.841-1.073-4.477-1.794-4.477-.549 0-1.265 1.825-1.74 3.656-.591-1.381-1.363-2.756-1.86-2.756-.64 0-1.278 2.273-1.594 4.235-1.68 1.147-2.906 2.809-2.906 4.765 0 2.7 4.05 3.357 5.4 3.411 1.35.054 3.023 3.562 3.585 5.072 1.242 4.367 2.051 8.699 2.698 11.183-1.649 0-1.804 2.111-1.348 2.111.713 0 1.953-.003 2.225 0 1.381.014 2.026-4.706 2.026-8.849 0-.212-.011-.627-.011-.627s1.93.505 6.038-.208c2.444-.424 5.03.849 5.746 3.163.527 1.704 1.399 3.305 1.868 4.484-1.589 0-1.545 2.037-1.084 2.037.787 0 1.801.014 2.183 0 1.468-.055.643-7.574 1.03-10.097s1.267-5.578-.229-8.797C34.857 15.236 36 11.505 36 8.447z M7.854 7.881s.372-.039.859.033c.217-.46.585-.887.585-.887s.281.668.386 1.179c.025.12.218.117.322.189 0 0 .038-3.463-.863-3.836.001-.002-.755 1.124-1.289 3.322zM4.399 9.36s.384-.267.883-.574c.217-.624.568-1.333.568-1.333s.307.602.345.81c.21-.114.21-.106.403-.19 0 0-.114-2.286-1.099-2.527 0 0-.732 1.372-1.1 3.814z"/></g><g transform="matrix(-.72 0 0 .72 64 10.08)"><path fill="#fff" d="M10.478 22.439s.702 2.281-.337 7.993c-.186 1.025-.46 2.072-.599 2.93-1.757 0-1.851 2.002-1.478 2.002h2.094c1.337 0 2.971-3.334 3.854-7.961s-3.534-4.964-3.534-4.964zm13.042 3.702s2.272 1.22 2.188 4.081c-.033 1.131-.249 2.091-.355 3.024-1.832 0-1.839 1.985-1.305 1.985h1.856c.923 0 3.001-3.158 3.379-7.281.379-4.122-5.763-1.809-5.763-1.809z M36 8.447C36 3.525 31.859 1 27 1a1 1 0 1 0 0 2c1.804 0 6.717.934 6.717 5.447 0 2.881-1.567 5.462-3.77 5.982-.164-.073-.345-.104-.509-.192-7.239-3.917-13.457.902-15.226-.29-1.752-1.182-.539-3.255-2.824-5.243-.33-1.841-1.073-4.477-1.794-4.477-.549 0-1.265 1.825-1.74 3.656-.591-1.381-1.363-2.756-1.86-2.756-.64 0-1.278 2.273-1.594 4.235-1.68 1.147-2.906 2.809-2.906 4.765 0 2.7 4.05 3.357 5.4 3.411 1.35.054 3.023 3.562 3.585 5.072 1.242 4.367 2.051 8.699 2.698 11.183-1.649 0-1.804 2.111-1.348 2.111.713 0 1.953-.003 2.225 0 1.381.014 2.026-4.706 2.026-8.849 0-.212-.011-.627-.011-.627s1.93.505 6.038-.208c2.444-.424 5.03.849 5.746 3.163.527 1.704 1.399 3.305 1.868 4.484-1.589 0-1.545 2.037-1.084 2.037.787 0 1.801.014 2.183 0 1.468-.055.643-7.574 1.03-10.097s1.267-5.578-.229-8.797C34.857 15.236 36 11.505 36 8.447z M7.854 7.881s.372-.039.859.033c.217-.46.585-.887.585-.887s.281.668.386 1.179c.025.12.218.117.322.189 0 0 .038-3.463-.863-3.836.001-.002-.755 1.124-1.289 3.322zM4.399 9.36s.384-.267.883-.574c.217-.624.568-1.333.568-1.333s.307.602.345.81c.21-.114.21-.106.403-.19 0 0-.114-2.286-1.099-2.527 0 0-.732 1.372-1.1 3.814z"/></g></svg></div>
<h3>{d['side'][0]}</h3>
<p>se1106@jbnu.ac.kr</p><p><a href="https://github.com/zohijin-k">github.com/zohijin-k</a></p><p><a href="https://zohijin-k.github.io">zohijin-k.github.io</a></p><p>{d['loc']}</p>
<h3>{d['side'][1]}</h3>{skills}
<h3>{d['side'][2]}</h3><p>{d['edu'][0]}</p><p>{d['edu'][1]}</p>
</aside>
<main>
<div class="name">{d['name']}</div>
<div class="role">{d['role']}</div>
<h2>{d['h'][0]}</h2><p class="summary">{d['profile']}</p>
<h2>{d['h'][1]}</h2><div class="awards">{awards}</div>
<h2>{d['h'][2]}</h2>{items(d['projects'][:d['split']])}
</main></div>
<div class="sheet"><aside>
<div style="height:11mm"></div>
<div class="mono sm"><svg viewBox="0 0 64 36" style="width:78%;height:auto;display:block"><g transform="matrix(-1 0 0 1 36 0)"><path fill="#fff" d="M10.478 22.439s.702 2.281-.337 7.993c-.186 1.025-.46 2.072-.599 2.93-1.757 0-1.851 2.002-1.478 2.002h2.094c1.337 0 2.971-3.334 3.854-7.961s-3.534-4.964-3.534-4.964zm13.042 3.702s2.272 1.22 2.188 4.081c-.033 1.131-.249 2.091-.355 3.024-1.832 0-1.839 1.985-1.305 1.985h1.856c.923 0 3.001-3.158 3.379-7.281.379-4.122-5.763-1.809-5.763-1.809z M36 8.447C36 3.525 31.859 1 27 1a1 1 0 1 0 0 2c1.804 0 6.717.934 6.717 5.447 0 2.881-1.567 5.462-3.77 5.982-.164-.073-.345-.104-.509-.192-7.239-3.917-13.457.902-15.226-.29-1.752-1.182-.539-3.255-2.824-5.243-.33-1.841-1.073-4.477-1.794-4.477-.549 0-1.265 1.825-1.74 3.656-.591-1.381-1.363-2.756-1.86-2.756-.64 0-1.278 2.273-1.594 4.235-1.68 1.147-2.906 2.809-2.906 4.765 0 2.7 4.05 3.357 5.4 3.411 1.35.054 3.023 3.562 3.585 5.072 1.242 4.367 2.051 8.699 2.698 11.183-1.649 0-1.804 2.111-1.348 2.111.713 0 1.953-.003 2.225 0 1.381.014 2.026-4.706 2.026-8.849 0-.212-.011-.627-.011-.627s1.93.505 6.038-.208c2.444-.424 5.03.849 5.746 3.163.527 1.704 1.399 3.305 1.868 4.484-1.589 0-1.545 2.037-1.084 2.037.787 0 1.801.014 2.183 0 1.468-.055.643-7.574 1.03-10.097s1.267-5.578-.229-8.797C34.857 15.236 36 11.505 36 8.447z M7.854 7.881s.372-.039.859.033c.217-.46.585-.887.585-.887s.281.668.386 1.179c.025.12.218.117.322.189 0 0 .038-3.463-.863-3.836.001-.002-.755 1.124-1.289 3.322zM4.399 9.36s.384-.267.883-.574c.217-.624.568-1.333.568-1.333s.307.602.345.81c.21-.114.21-.106.403-.19 0 0-.114-2.286-1.099-2.527 0 0-.732 1.372-1.1 3.814z"/></g><g transform="matrix(-.72 0 0 .72 64 10.08)"><path fill="#fff" d="M10.478 22.439s.702 2.281-.337 7.993c-.186 1.025-.46 2.072-.599 2.93-1.757 0-1.851 2.002-1.478 2.002h2.094c1.337 0 2.971-3.334 3.854-7.961s-3.534-4.964-3.534-4.964zm13.042 3.702s2.272 1.22 2.188 4.081c-.033 1.131-.249 2.091-.355 3.024-1.832 0-1.839 1.985-1.305 1.985h1.856c.923 0 3.001-3.158 3.379-7.281.379-4.122-5.763-1.809-5.763-1.809z M36 8.447C36 3.525 31.859 1 27 1a1 1 0 1 0 0 2c1.804 0 6.717.934 6.717 5.447 0 2.881-1.567 5.462-3.77 5.982-.164-.073-.345-.104-.509-.192-7.239-3.917-13.457.902-15.226-.29-1.752-1.182-.539-3.255-2.824-5.243-.33-1.841-1.073-4.477-1.794-4.477-.549 0-1.265 1.825-1.74 3.656-.591-1.381-1.363-2.756-1.86-2.756-.64 0-1.278 2.273-1.594 4.235-1.68 1.147-2.906 2.809-2.906 4.765 0 2.7 4.05 3.357 5.4 3.411 1.35.054 3.023 3.562 3.585 5.072 1.242 4.367 2.051 8.699 2.698 11.183-1.649 0-1.804 2.111-1.348 2.111.713 0 1.953-.003 2.225 0 1.381.014 2.026-4.706 2.026-8.849 0-.212-.011-.627-.011-.627s1.93.505 6.038-.208c2.444-.424 5.03.849 5.746 3.163.527 1.704 1.399 3.305 1.868 4.484-1.589 0-1.545 2.037-1.084 2.037.787 0 1.801.014 2.183 0 1.468-.055.643-7.574 1.03-10.097s1.267-5.578-.229-8.797C34.857 15.236 36 11.505 36 8.447z M7.854 7.881s.372-.039.859.033c.217-.46.585-.887.585-.887s.281.668.386 1.179c.025.12.218.117.322.189 0 0 .038-3.463-.863-3.836.001-.002-.755 1.124-1.289 3.322zM4.399 9.36s.384-.267.883-.574c.217-.624.568-1.333.568-1.333s.307.602.345.81c.21-.114.21-.106.403-.19 0 0-.114-2.286-1.099-2.527 0 0-.732 1.372-1.1 3.814z"/></g></svg></div>
<h3>{d['side'][3]}</h3><ul>{links}</ul>
</aside>
<main>
<div class="cont"><b>{d['name']}</b>{d['cont']}</div>
<h2>{d['h'][3]}</h2>{items(d['projects'][d['split']:])}
{f'<h2>{d["h"][4]}</h2><div class="other">{other}</div>' if d['other'] else ''}
</main></div>
</body></html>"""


KO = dict(split=3, lang="ko", name="조이진", role="서비스 개발자 · 기획자", loc="전주, 대한민국", cont="CV · 2 / 2",
 side=["연락처", "기술", "학력", "링크"],
 h=["프로필", "수상", "주요 프로젝트", "주요 프로젝트 (계속)", "기타 프로젝트"],
 profile="공공데이터와 AI를 활용해 서비스를 기획하고 구현하는 개발자입니다. 멀티 에이전트 분석 구조, 규칙 엔진과 생성형 AI를 결합한 판정 구조, 차량 신호 기반 실시간 오디오 엔진을 설계했으며, 서비스 기획부터 화면 설계, 구현, 배포까지 직접 수행했습니다.",
 edu=("전북대학교 컴퓨터인공지능학부 학사과정", "2024 입학 · 재학 중"),
 awards=[("2026", "2026 오픈소스 SW 아이디어 해커톤 캠프 최우수상 (전북대학교 AI대학장상)", "채움"),
         ("2026", "제14회 산업통상부 공공데이터 활용 아이디어 공모전 (제품 및 서비스 개발 부문) 우수상 (한국무역보험공사 사장상)", "EAAI"),
         ("2026", "2026 JBNU AI·SW 경진대회 (SW부문) 동상", "SpeakUp"),
         ("2026", "제3회 호남권 SW창업 아이디어 경진대회 장려상", "J:ON"),
         ("2025", "2025 오픈소스 SW 아이디어 해커톤 캠프 우수상", "Toss-Talk")],
 projects=[
  ("EAAI — 수출 의사결정 멀티 에이전트 플랫폼", "1인 개발", "2026",
   "React, Vite, TypeScript, FastAPI, OpenRouter, Vercel, Railway", [
    "기업·시장·위험·규제·점수·전략·검토 에이전트를 순차 실행하고, 생성된 전략을 별도 에이전트가 재검토하는 이중 검토 구조 설계",
    "K-SURE 국가·업종 위험지수 OpenAPI를 수출 적합도 산식에 연동, 30분 TTL 캐시와 백그라운드 갱신 적용",
    "공공데이터는 LIVE·CACHED·DEMO 상태로, AI 생성 결과는 별도 라벨로 구분해 출처를 명시",
    "strict JSON 스키마로 응답 형식을 고정하고 오류 시 대체 전략으로 자동 전환",
    "추천 국가 랭킹, 근거, 5단계 실행 로드맵을 한 화면에 제공하고 PDF 보고서로 내보내기"]),
  ("SYNE — 주행 실시간 작곡 차량용 앱", "1인 개발", "2026",
   "Kotlin, Jetpack Compose, Coroutines/Flow, Pleos Connect SDK(AAOS), AudioTrack, Room", [
    "속도·조향·브레이크·내비 정보를 악기 편성과 멜로디로 바꾸는 실시간 작곡 엔진 설계, 1024프레임 블록 단위 처리(오디오 스레드 약 3%/코어)",
    "웨이브테이블·polyBLEP 오실레이터와 SVF 필터로 드럼을 포함한 모든 소리를 직접 합성",
    "과속을 보상하지 않는 편성, 주행 중 숫자·버튼 없는 정지 화면 등 운전 안전 중심 UX 설계",
    "출발·도착 지점을 반경 300m로 묶어 같은 코스의 주행을 한 앨범의 Vol.로 누적",
    "오프라인 렌더 테스트(급제동 1초 내 −66dB 등)와 단위 테스트 55개로 반응 검증"]),
  ("TRIPICK — GPS 기반 여행 코스 검증 플랫폼", "팀 · 기획·프론트엔드", "2026",
   "React Native(Expo), React, NestJS, PostgreSQL, TourAPI 4.0", [
    "완주율·만족도·수행자 수 기반 TRIPICK Score 설계, 저완주 리뷰 가중치 1/3 적용",
    "지점 50m 이내 자동 체크인과 이동 속도 기반 위치 조작 탐지",
    "웹과 앱의 TourAPI 호출 차이(CORS, 키 형식)를 캐싱 프록시로 통일",
    "서비스 기획, 화면 설계, React Native 앱과 웹 프론트엔드 구현, 웹·베타 API 배포"]),
  ("J:ON — 전북 청년 취업 내비게이션", "팀 · 기획·개발 전체", "2026",
   "JavaScript, Python, scikit-learn, 국민연금·교육부 공공데이터", [
    "지원 불가 조건을 역산해 단독·조합 차단 요인을 구분하고, 조건 하나로 열리는 공고 수 계산",
    "채용공고를 국민연금 가입 데이터와 교차 검증해 실제 직원 수와 고용 증감 표시",
    "민간 크롤링 없이 공공데이터만 사용, 논리 정합성 11개 항목 자동 검증",
    "기획, 데이터 처리, 디자인, 개발, 제안서 작성 전체 담당 (팀원은 자료조사)"]),
  ("채움 — 원도심 공실 상가 진단·매칭 플랫폼", "팀 · UI·에이전트 설계", "2026",
   "Next.js, TypeScript, Tailwind CSS, FastAPI, LangGraph", [
    "건물주·창업자·팝업 브랜드·지자체별 진입 화면부터 매물 지도, 대시보드까지 서비스 전체 UI 설계·구현",
    "LangGraph 기반 멀티 에이전트 구조 설계"]),
  ("SpeakUp — 실시간 말하기 코칭 서비스", "팀 · 웹 프론트엔드", "2026",
   "MediaPipe, faster-whisper, FastAPI, TypeScript", [
    "실시간 연습 화면, 코칭 지표 표시, 세션 리포트, 성장 대시보드 등 웹 프론트엔드 구현"]),
  ("복지대로 — 복지 내비게이션", "1인 개발", "2026",
   "Next.js 16, React 19, TypeScript, Tailwind CSS 4, OpenAI API, Vitest", [
    "자격 판정은 규칙 엔진, 근거 설명은 생성형 AI로 분리하고 AI가 판정 상태를 바꿀 수 없도록 응답 형식 고정",
    "사용자 조건으로 제도별 지금 가능·상담 필요·N개월 후·막힌 길을 구분하고, 조건 변경 시 경로 재계산",
    "SVG 복지지도와 목록을 양방향 연동해 지도 없이 목록만으로도 탐색 가능",
    "사회보장정보원 복지서비스 CSV를 461개 제도로 정규화해 공식 카탈로그 검색 제공"])],
 other=[],
 links=[("포트폴리오", "zohijin-k.github.io"), ("GitHub", "github.com/zohijin-k"),
        ("EAAI 데모", "eaai-one.vercel.app"), ("TRIPICK 데모", "tripick.vercel.app")],
 skills=[("언어", "TypeScript, JavaScript, Python, Kotlin"),
         ("프론트엔드", "Next.js, React, Tailwind CSS"),
         ("모바일", "React Native(Expo), Kotlin, Jetpack Compose, Android Automotive OS"),
         ("백엔드·배포", "FastAPI, Supabase, PostgreSQL, Vercel, Railway"),
         ("AI", "OpenAI·Claude API, LangGraph, 멀티 에이전트, 규칙 엔진, MediaPipe")])

EN = dict(split=2, lang="en", name="Ijin Jo", role="Service Developer & Product Planner", loc="Jeonju, South Korea", cont="CV · 2 / 2",
 side=["CONTACT", "SKILLS", "EDUCATION", "LINKS"],
 h=["SUMMARY", "AWARDS", "PROJECTS", "PROJECTS (CONTINUED)", "OTHER PROJECTS"],
 profile="Service developer who plans and builds products with public data and AI. Designed a multi-agent analysis pipeline, a rule-engine plus LLM decision flow, and a real-time audio engine driven by vehicle signals, and owned each from planning and UI design to implementation and deployment.",
 edu=("Jeonbuk National University, B.S. in Computer Science and Artificial Intelligence", "2024 – Present"),
 awards=[("2026", "Grand Prize, 2026 Open Source SW Idea Hackathon Camp (JBNU College of AI Dean's Award)", "CHAEUM"),
         ("2026", "Excellence Award, 14th MOTIE Public Data Idea Contest, Product & Service Development Track (K-SURE CEO Award)", "EAAI"),
         ("2026", "Bronze Prize, 2026 JBNU AI·SW Competition (SW Track)", "SpeakUp"),
         ("2026", "Encouragement Prize, 3rd Honam SW Startup Idea Competition", "J:ON"),
         ("2025", "Excellence Award, 2025 Open Source SW Idea Hackathon Camp", "Toss-Talk")],
 projects=[
  ("EAAI — Export Decision Multi-Agent Platform", "Solo", "2026",
   "React, Vite, TypeScript, FastAPI, OpenRouter, Vercel, Railway", [
    "Designed a seven-stage agent pipeline in which a separate reviewer agent validates the generated strategy.",
    "Linked K-SURE country and industry risk APIs to the export-fit score, with a 30-minute TTL cache and background refresh.",
    "Labeled public data as LIVE, CACHED or DEMO and marked AI-generated content separately.",
    "Locked responses to a strict JSON schema with automatic fallback on timeout or parse errors.",
    "Delivered country rankings, evidence and a five-step roadmap on one screen, with PDF export."]),
  ("SYNE — Real-Time Driving Music App for Cars", "Solo", "2026",
   "Kotlin, Jetpack Compose, Coroutines/Flow, Pleos Connect SDK (AAOS), AudioTrack, Room", [
    "Built a real-time composition engine that turns speed, steering, braking and navigation data into arrangement and melody, processed in 1,024-frame blocks (about 3% of one core).",
    "Synthesized every sound, drums included, with wavetable and polyBLEP oscillators and SVF filters.",
    "Designed safety-first UX: speeding is never rewarded, and the driving screen shows a static graphic with no numbers or buttons.",
    "Grouped trips by start and end points within 300 m so repeat drives stack as volumes of one album.",
    "Verified responses with offline render tests (e.g. -66 dB within 1 s of hard braking) and 55 unit tests."]),
  ("TRIPICK — GPS-Verified Travel Course Platform", "Team · Planning, Frontend", "2026",
   "React Native (Expo), React, NestJS, PostgreSQL, TourAPI 4.0", [
    "Designed TRIPICK Score from completion rate, satisfaction and participant count; down-weighted low-completion reviews.",
    "Built automatic check-in within 50 m of each stop and speed-based location spoofing detection.",
    "Unified web and app TourAPI calls (CORS, key format) behind a caching proxy.",
    "Led service planning and UI design; built the React Native app and web client."]),
  ("J:ON — Youth Job Navigation for Jeonbuk", "Team · Planning, Development", "2026",
   "JavaScript, Python, scikit-learn, National Pension and education public data", [
    "Back-calculated blocking conditions to show how many postings one more qualification would unlock.",
    "Cross-checked postings with National Pension enrollment data to show real headcount and hiring trends.",
    "Used public data only, with 11 consistency checks run automatically.",
    "Owned planning, data processing, design, development and the proposal."]),
  ("CHAEUM — Vacant Storefront Diagnosis and Matching", "Team · UI, Agent Design", "2026",
   "Next.js, TypeScript, Tailwind CSS, FastAPI, LangGraph", [
    "Designed and built the full service UI, from role-based entry screens to the listing map and dashboard.",
    "Designed the LangGraph multi-agent structure."]),
  ("SpeakUp — Real-Time Speaking Coach", "Team · Web Frontend", "2026",
   "MediaPipe, faster-whisper, FastAPI, TypeScript", [
    "Built the web frontend: live practice screen, coaching indicators, session report and progress dashboard."]),
  ("Bokji-Daero — Welfare Navigation", "Solo", "2026",
   "Next.js 16, React 19, TypeScript, Tailwind CSS 4, OpenAI API, Vitest", [
    "Split eligibility decisions (rule engine) from plain-language explanations (LLM); the model cannot change a decision and its output schema is fixed.",
    "Classified each program as available now, needs consultation, available later or blocked, and recalculated routes when conditions change.",
    "Linked an SVG welfare map and a list in both directions, so the list alone is enough to explore.",
    "Normalized the national social security service CSV into 461 programs for official catalog search."])],
 other=[],
 links=[("Portfolio", "zohijin-k.github.io"), ("GitHub", "github.com/zohijin-k"),
        ("EAAI demo", "eaai-one.vercel.app"), ("TRIPICK demo", "tripick.vercel.app")],
 skills=[("LANGUAGES", "TypeScript, JavaScript, Python, Kotlin"),
         ("FRONTEND", "Next.js, React, Tailwind CSS"),
         ("MOBILE", "React Native (Expo), Kotlin, Jetpack Compose, Android Automotive OS"),
         ("BACKEND", "FastAPI, Supabase, PostgreSQL, Vercel, Railway"),
         ("AI", "OpenAI and Claude APIs, LangGraph, multi-agent systems, rule engines, MediaPipe")])

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, d in (("cv-ko", KO), ("cv-en", EN)):
        html = OUT / f"{name}.html"
        html.write_text(page(d), encoding="utf-8")
        pg = b.new_page()
        pg.goto(html.as_uri())
        pg.wait_for_timeout(300)
        bottoms = pg.evaluate("[...document.querySelectorAll('.sheet')].map(s=>{const m=s.querySelector('main');return Math.round(m.lastElementChild.getBoundingClientRect().bottom - s.getBoundingClientRect().top)})")
        print(name, "content bottom per page", bottoms, "(limit ≈ 1123)")
        pg.pdf(path=str(OUT / f"{name}.pdf"), format="A4", print_background=True)
    b.close()
