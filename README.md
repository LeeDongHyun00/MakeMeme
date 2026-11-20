# MakeMeme — 밈 트렌드 결합 마케팅 콘텐츠 스킬

마케팅 주제를 입력하면 현재 한국에서 유행 중인 밈을 웹에서 찾아 기준에 따라 판정하고, 그 유행과 주제를 결합한 **숏폼 영상 기획안**과 **SNS 게시물 문구**를 만들어 주는 AI 스킬입니다. Claude, ChatGPT, Gemini에 모두 적용할 수 있습니다.

## 구성

```
meme-marketing/
├── SKILL.md                    # 스킬 본문 (작업 절차)
├── references/
│   ├── trend-criteria.md       # 유행 판정 기준·점수표
│   ├── sources.md              # 수집 출처·검색어 패턴
│   ├── output-templates.md     # 산출물 양식
│   └── brand-safety.md         # 리스크 점검표
└── scripts/
    ├── youtube_trending.py     # (선택) YouTube 인기 급상승 수치 수집
    └── test_youtube_trending.py
```

## 동작 방식

1. 마케팅 주제 입력 (브랜드, 타깃, 톤, 채널은 선택)
2. 웹 검색으로 최근 7일 유행 후보 수집
3. 5개 지표로 채점 — 확산 속도(30), 참여도(20), 재생산(20), 교차 확산(15), 최신성(15)
4. 70점 이상을 유행으로 판정하고, 하락 단계는 제외
5. 주제와 자연스럽게 이어지는 유행 상위 3개 선정
6. 유행별 숏폼 기획안 + SNS 문구 작성, 리스크 점검 결과 첨부

## 적용 방법

세 플랫폼 모두 **웹 검색 기능이 켜져 있어야** 합니다. 검색이 없으면 스킬은 유행을 지어내지 않고 자료를 요청하도록 되어 있습니다.

### Claude

- **Claude 앱**: `meme-marketing` 폴더를 zip으로 압축해 설정의 스킬 메뉴에서 업로드합니다.
- **Claude Code**: 폴더를 프로젝트의 `.claude/skills/meme-marketing/` 또는 `~/.claude/skills/meme-marketing/`에 복사합니다.

### ChatGPT (Custom GPT)

1. GPT 만들기 → 구성(Configure)
2. **지침(Instructions)**: `SKILL.md`에서 맨 위 `---` 사이의 머리말을 뺀 본문 전체를 붙여 넣습니다. (지침란 글자 수 한도에 맞춰 작성되어 있습니다)
3. **지식(Knowledge)**: `references/` 폴더의 파일 4개를 업로드합니다.
4. **기능(Capabilities)**: 웹 검색을 켭니다. YouTube 수치 스크립트를 쓰려면 코드 실행도 켭니다.

### Gemini (Gem)

1. Gem 관리자 → 새 Gem
2. **요청 사항(Instructions)**: `SKILL.md` 본문을 붙여 넣습니다.
3. **지식(Knowledge)**: `references/` 폴더의 파일 4개를 추가합니다.
4. Google 검색을 사용할 수 있는 상태로 둡니다.

### 그 외 (프로젝트·일반 대화)

`SKILL.md`와 `references/` 파일을 대화에 첨부하고 "이 지침대로 진행해 줘"라고 요청해도 됩니다.

## 사용 예시

```
주제: 신제품 저당 그릭요거트 출시
타깃: 20~30대 직장인
채널: 인스타그램 릴스
```

```
우리 동네 필라테스 스튜디오 12월 신규 회원 모집, 요즘 유행하는 밈으로 릴스 기획해줘
```

주제만 입력해도 됩니다. 나머지는 스킬이 가정하고 결과 맨 위에 밝힙니다.

## YouTube 수치 스크립트 (선택)

YouTube Data API v3 키가 있으면 한국 인기 급상승 영상의 시간당 조회수와 좋아요율을 직접 계산할 수 있습니다. 외부 패키지가 필요 없습니다.

```bash
export YOUTUBE_API_KEY=발급받은_키
```

```bash
python meme-marketing/scripts/youtube_trending.py --region KR --max 50 --format table
```

테스트:

```bash
cd meme-marketing/scripts && python -m unittest test_youtube_trending -v
```

키가 없으면 스크립트는 안내 메시지를 내고 종료하며, 스킬은 웹 검색만으로 진행합니다.

## 한계

- **수치 정확도**: 웹 검색만으로는 조회수·좋아요 수를 직접 확인하지 못하는 경우가 많습니다. 그래서 판정마다 신뢰도(높음·중간·낮음)를 표기하고, 확인하지 못한 수치는 적지 않습니다.
- **Instagram·TikTok**: 공식 급상승 API가 없어 트렌드 정리 글과 공개 게시물 검색에 의존합니다.
- **유효 기간**: 결과는 조사한 날짜에만 유효합니다. 유행은 며칠 만에 바뀌므로 제작 직전에 다시 실행하세요.
- **법률·라이선스**: 음원의 상업적 사용, 초상권, 업종별 광고 규정은 스킬이 확인 필요 지점만 짚습니다. 게시 전에 담당자가 확인해야 합니다.
- **점수 기준값**: `trend-criteria.md`의 기준(24시간 10만 회, 좋아요율 4% 등)은 출발점입니다. 팀이 다루는 업종과 계정 규모에 맞게 조정해 쓰세요.
