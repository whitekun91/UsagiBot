# Usagi Bot

Usagi Main Image

FFXIV 정보·일상 커뮤니티·생성형 AI·음악 재생을 지향하는 Discord 봇입니다.  
(Usagi = 일본어로 토끼)

Python

## 요구 사항

- Python 3.10 이상
- [Discord 개발자 포털](https://discord.com/developers/applications)에서 봇 토큰 발급
- 음악 재생: **FFmpeg**가 시스템 PATH에 있어야 합니다 ([ffmpeg.org](https://ffmpeg.org/download.html))
- 슬래시 명령·메시지 읽기: Discord 포털에서 **Privileged Gateway Intents**에서 `MESSAGE CONTENT INTENT` 활성화

## 설치

```bash
cd UsagiBot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 설정

1. 프로젝트 루트에 `.env` 파일을 만들고 `.env.example`을 참고해 값을 넣습니다.
  - 최소 `**DISCORD_TOKEN**` (필수)
  - `**OPENAI_API_KEY**`: `/ai` 명령 사용 시
  - `**SYNC_GUILD_ID**`: 개발 중 한 서버에만 슬래시 명령을 빠르게 맞출 때 (선택)

또는 `config/config.json`에 `"token"`만 넣을 수 있습니다. (`.env`의 `DISCORD_TOKEN`이 우선합니다.)

## 실행

```bash
python -m usagibot
```

로그는 `logs/usagibot.log`에 기록됩니다.

## 명령 (슬래시)


| 명령                   | 설명                            |
| -------------------- | ----------------------------- |
| `/ping`              | 지연 시간 확인                      |
| `/about`             | 봇 소개                          |
| `/ff14`              | FFXIV 관련 바로가기 링크              |
| `/ai`                | 생성형 AI 질문 (API 키 필요)          |
| `/play`              | YouTube URL 또는 검색어로 재생·대기열 추가 |
| `/skip`              | 현재 곡 건너뛰기                     |
| `/queue`             | 대기열 보기                        |
| `/pause` / `/resume` | 일시정지 / 재개                     |
| `/leave`             | 음성 채널 퇴장·대기열 비우기              |


## 프로젝트 구조

```
UsagiBot/
  usagibot/           # 패키지 루트
    __main__.py       # 진입점
    bot.py            # 봇 클래스·확장 로드
    settings.py       # 환경/JSON 설정
    cogs/             # 기능 단위 (코그)
      general.py
      ff14.py
      generative.py
      music.py
    utils/
      logging.py
  config/             # (선택) JSON 설정 예시
  logs/               # 실행 시 생성
```

## 버전

- **v2.0.0** — `discord.ext.commands` + 슬래시 명령, 코그 구조, AI·음악 모듈 정리
- v1.0.1 — 초기 파일 구조 (2024-03-20)
- v1.0.0 — 최초 릴리스 (2024-03-19)

## 참고

- 음악 기능은 YouTube 정책·저작권을 준수해 사용하세요.
- 상시 실행은 Railway·Render·VPS 등 **항상 켜진 프로세스**가 가능한 호스트에 두는 것이 좋습니다.