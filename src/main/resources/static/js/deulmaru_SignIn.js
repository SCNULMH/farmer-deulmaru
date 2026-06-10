document.addEventListener("DOMContentLoaded", function () {
    const domainSelect = document.getElementById("emailDomain");
    const customDomainContainer = document.getElementById("customDomainContainer");
    const customDomainInput = document.getElementById("customDomain");
    const form = document.querySelector("form");

    // 1) 도메인 <select> 변경 시: "직접 입력"이면 추가 입력란 보이기
    domainSelect.addEventListener("change", function() {
        if (domainSelect.value === "custom") {
            // '직접 입력' 선택 시, 숨겨진 도메인 입력란 노출
            customDomainContainer.style.display = "block";
            customDomainInput.value = "";  // 초기화
        } else {
            // 기존 도메인 선택 시, 숨김
            customDomainContainer.style.display = "none";
        }
    });

    // 2) 폼 전송 시점에 최종 이메일을 합쳐서 userEmail 필드에 세팅
    form.addEventListener("submit", function (event) {
        const userId = document.getElementById("userId").value;
        const userPw = document.getElementById("userPw").value;
        const userNickname = document.getElementById("userNickname").value;
        const userEmail = document.getElementById("userEmail").value;
        const userLocate = document.getElementById("userLocate").value;
        const userBirth = document.getElementById("userBirth").value;
        const userGender = document.getElementById("userGender").value;

        // 간단한 필드 빈 값 체크 (아이디, 비밀번호, 이메일 아이디 등)
        if (!userId || !userPw || !userNickname || !userEmail || !userLocate || !userBirth || !userGender) {
            alert("모든 필드를 입력해주세요!");
            event.preventDefault(); // 폼 제출 막기
            return;
        }

        // (A) 현재 선택된 도메인 가져오기
        let finalDomain = domainSelect.value;

        // (B) 만약 '직접 입력'을 선택했다면, customDomainInput에서 가져옴
        if (finalDomain === "custom") {
            finalDomain = customDomainInput.value;
            // 사용자가 '@'를 쓰지 않았으면 자동으로 붙이기 (원하는 로직에 따라 조정)
            if (!finalDomain.startsWith("@")) {
                finalDomain = "@" + finalDomain;
            }
        }

        // (C) 이메일 아이디 + 도메인 합치기 => 예: "test1@naver.com"
        const fullEmail = userEmail + finalDomain;

        // (D) userEmail 필드에 최종 이메일을 다시 세팅
        document.getElementById("userEmail").value = fullEmail;

        // 이후 폼은 정상적으로 제출 -> 서버에서 userEmail = "test1@naver.com" 형태로 받음
    });
});
