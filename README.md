# korea-covid-19-remaining-vaccine-macro
잔여백신 지도 API로 남은 백신 수를 확인하고, 잔여백신이 있는 경우 잔여백신 예약 페이지로 이동합니다.

## 카카오 잔여백신 예약
### 이용방법
1. Chrome 브라우저를 이용하여 모든 작업을 진행하므로, 크롬 브라우저를 실행해주세요.
2. [카카오 계정 로그인 페이지](https://accounts.kakao.com/login?continue=https%3A%2F%2Fvaccine-map.kakao.com%2Fmap2%3Fv%3D1) 에 접근하여 카카오 로그인을 합니다. [로그인 시 주의사항](https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro/issues/82)
3. [#2](https://github.com/SJang1/korea-covid-19-remaining-vaccine-macro/discussions/2)를 보고 잔여백신을 검색할 범위의 좌표값을 찾습니다.
4. Release 페이지에서 `vaccine-run-kakao-windows.zip`을 받아 압축해제하고, exe 파일을 실행합니다.
5. 사용자 권한 동의를 요청하면 승인해주세요. 자동으로 검색 및 예약시도를 진행합니다.
6. 예약 성공 시 빵빠레 소리와 함께 예약이 성공했음이 안내됩니다.

### 주의사항
- 예약 시도 후에는 자동 예약 프로그램은 정지됩니다.
- 예약 시도가 반드시 성공 한다는 보장이 없습니다.
- 예약 시도 후에는 다시 시도 할 경우 처음부터 다시 시작하셔야합니다.
- 프로그램을 한두개만 띄우시기 바랍니다. 과도하게 많이 실행하는 경우 카카오 계정이 정지될 수 있습니다.

### 다운로드 팁
- Actions 탭에서 master을 바로 실행 가능한 파일로 변환한 파일을 받을 수 있습니다. (Artifacts)
- Release 탭에서 문제 없음을 확인한 버전을 다운받을 수 있습니다.

## 네이버 잔여백신 예약
### 주의사항
- 네이버 서버의 문제로, 잔여백신이 발생할 때마다 잔여백신 지도 API가 작동을 하지 않습니다.

## Disclaimer
- 본 프로그램은 매크로를 이용한 백신 예약을 유도하는 내용이 아니며, 해당 프로그램을 사용함으로서 생기는 책임은 모두 이용자 본인에게 있습니다.
