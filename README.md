# korea-covid-19-remaining-vaccine-macro [![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FSJang1%2Fkorea-covid-19-remaining-vaccine-macro&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=README_HITS&edge_flat=false)](https://hits.seeyoufarm.com) [![Python package](https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro/actions/workflows/package.yml/badge.svg)](https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro/actions/workflows/package.yml) [![CodeQL](https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro/actions/workflows/codeql-analysis.yml)
잔여백신 지도 API로 남은 백신 수를 확인하고, 잔여백신이 있는 경우 잔여백신 예약 페이지로 이동하거나 예약을 시도합니다.

### 자세한 내용은 [공지사항](https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro/discussions/468)을 참고하세요.
## 카카오 잔여백신 예약
### 이용방법
1. Chrome 브라우저를 이용하여 모든 작업을 진행하므로, 크롬 브라우저를 실행해주세요.
2. [쿠키값 추출 방법](./docs/login.md)을 따라 쿠키값을 추출 후 복사해둡니다.
3. [좌표범위 설정방법](./docs/coordinates.md)을 따라 잔여백신을 검색할 범위의 좌표값을 찾습니다.
4. [Release 페이지](https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro/releases/latest)에서 본인의 운영체제에 맞는 파일을 다운로드 받고 실행합니다.
5. 사용자 권한 동의를 요청하면 승인해주세요. 좌표값을 입력하고 나면 자동으로 검색 및 예약시도를 진행합니다.
6. 예약 성공 시 빵빠레 소리와 함께 예약이 성공했음이 안내됩니다.

### 주의사항
- 예약 시도 후에는 자동 예약 프로그램은 정지됩니다.
- 예약 시도가 반드시 성공 한다는 보장이 없습니다.
- 예약 시도 후에는 다시 시도 할 경우 프로그램을 실행한 경로에 존재하는 `cookie.ini` 파일 삭제 후 처음부터 다시 시작하셔야합니다.
- 프로그램을 한두개만 띄우시기 바랍니다. 과도하게 많이 실행하는 경우 카카오 계정이 정지될 수 있습니다.
- tmux, screen과 같은 터미널 멀티플렉싱 프로그램이 자동으로 실행되지 않게 해 주셔야 합니다.

### 다운로드 팁
- Actions 탭에서 main을 바로 실행 가능한 파일로 변환한 파일을 받을 수 있습니다. (Artifacts)
- Release 탭에서 문제 없음을 확인한 버전을 다운받을 수 있습니다.

## 네이버 잔여백신 예약
### 주의사항
- 네이버 서버의 문제로, 잔여백신이 발생할 때마다 잔여백신 지도 API가 작동을 하지 않습니다.

## Disclaimer
- 본 프로그램은 매크로를 이용한 백신 예약을 유도하는 내용이 아니며, 해당 프로그램을 사용함으로서 생기는 책임은 모두 이용자 본인에게 있습니다.
