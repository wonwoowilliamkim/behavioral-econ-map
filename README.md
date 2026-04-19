# Behavioral Econ Map

**Behavioral Public Economics — Interactive Research Ontology**

행동공공경제학 분야의 연구 지형을 온톨로지 기반으로 정리해  
한눈에 탐색할 수 있는 인터랙티브 웹사이트.

## 핵심 아이디어

> Obsidian의 그래프 뷰처럼 — 토픽 → 서브토픽 → 논문 → 연구자가  
> 연결된 인터랙티브 맵으로, 브라우저에서 바로 탐색 가능.

"Internality taxation 쪽에 어떤 연구가 있지?"  
"Nudge + retirement savings 교차점은 누가 연구했지?"  
→ 클릭 몇 번으로 바로 확인.

## 온톨로지 구조

```
Behavioral Public Economics
│
├── Welfare Analysis with Biases
│   ├── Revealed vs. Stated Preference
│   ├── Paternalism & Libertarian Paternalism
│   └── Beyond Revealed Preference (Bernheim & Rangel)
│
├── Corrective Policy
│   ├── Internality Taxation (Allcott, Taubinsky)
│   ├── Sin Taxes (tobacco, sugar, alcohol)
│   └── Nudge vs. Tax tradeoffs
│
├── Nudges & Defaults
│   ├── Retirement Savings (401k defaults)
│   ├── Energy Efficiency
│   └── Health Behaviors
│
├── Sludge & Friction
│   ├── Program Take-up
│   └── Administrative Burden
│
└── Empirical Methods
    ├── Bias Measurement
    ├── Sufficient Statistics
    └── Structural vs. Reduced Form
```

## 기술 스택

- **데이터**: YAML 온톨로지 파일 (논문, 연구자, 토픽)
- **시각화**: D3.js force-directed graph
- **사이트**: 순수 HTML/CSS/JS — GitHub Pages 배포
- **검색**: 클라이언트 사이드 fuzzy search

## 주요 연구자 (초기 커버리지)

- Hunt Allcott, Dmitry Taubinsky — internality taxation
- Doug Bernheim, Antonio Rangel — behavioral welfare analysis
- Raj Chetty — sufficient statistics, tax salience
- David Laibson — present bias, retirement savings
- Elizabeth Linos — sludge, administrative burden
- Stefanie Stantcheva — tax complexity, survey methods

## 레퍼런스

- [Behavioral Public Economics Mini-Course](https://sites.google.com/view/behavioralpublic/home)
- NBER Behavioral Public Economics Working Group

## 프로젝트 구조

```
├── data/
│   ├── ontology/
│   │   ├── topics.yaml        # 토픽 계층 구조
│   │   ├── papers.yaml        # 논문 메타데이터
│   │   └── researchers.yaml   # 연구자 프로파일
│   └── graph.json             # D3 입력용 변환 데이터
├── site/
│   ├── index.html             # 메인 페이지
│   ├── graph.js               # D3 시각화
│   ├── search.js              # 검색 기능
│   └── style.css
├── scripts/
│   └── build_graph.py         # YAML → graph.json 변환
└── docs/                      # GitHub Pages 빌드 출력
```

## 마일스톤

| 단계 | 목표 |
|------|------|
| 1 | 온톨로지 YAML 초안 (핵심 토픽 + 논문 30편) |
| 2 | D3 그래프 뷰 첫 버전 (GitHub Pages) |
| 3 | 클릭 시 논문 정보 패널 표시 |
| 4 | 검색 + 필터 기능 |
| 5 | 논문 자동 추가 파이프라인 |
