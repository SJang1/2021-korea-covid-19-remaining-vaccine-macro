# 잔여백신 본인정보 확인 API 문제 해결

- [잔여백신 본인정보 확인 API](https://vaccine.kakao.com/api/v1/user)를 요청했을 때 브라우저에 `"error":"error occurred"` 메세지가 반환되는 계정이 있습니다.
카카오 잔여백신 서비스에서 정보제공 동의를 한 적이 없는 계정에서 발생하는 문제입니다.
- 브라우저 환경이나 프로그램의 상태와 상관이 없습니다. 
- 이 단계는 모바일에서 실행하는 것을 권장합니다.


## 해결 방법

1. 카카오 잔여백신 조회화면에서 아무 병원이나 선택해주세요.


![iCIHXeInxvOpUpmyzgbdRbjylMSPTfxC](https://user-images.githubusercontent.com/55320997/128977256-7bb9a93b-a43a-44d4-8e58-41f8987e073c.png)
[^1]


2. 알림 신청을 선택하고 정보제공 동의를 진행해주세요.


![ZRfLnyaLEjLagMoFvEulUkQKtuEuyHoK](https://user-images.githubusercontent.com/55320997/128977375-f7a61260-f46c-4983-a822-f11e69c0b389.png)
[^2]


3. 여기까지 완료하셨으면 [잔여백신 본인정보 확인 API](https://vaccine.kakao.com/api/v1/user) 화면에서 정보 조회가 잘 되는 것을 확인해주세요. 문제가 없으면 다음 단계를 진행해주세요.


---
[^1] 이미지 출처: https://mediahub.seoul.go.kr/archives/2001761

[^2] 이미지 출처: https://mediahub.seoul.go.kr/archives/2001761