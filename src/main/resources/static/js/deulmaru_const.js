document.addEventListener("DOMContentLoaded", function() {
    console.log("✅ deulmaru_const.js 로드 완료");

    function showTab(tabName) {
        // 모든 탭 콘텐츠 숨기기
        document.querySelectorAll(".tab-content").forEach(tab => tab.style.display = "none");

        // 선택한 탭 보이기
        const targetTab = document.getElementById(tabName);
        if (targetTab) {
            targetTab.style.display = "block";

            // 모든 버튼에서 active 제거
            document.querySelectorAll(".tab-button").forEach(btn => btn.classList.remove("active"));

            // 클릭한 버튼에 active 추가
            document.querySelector(`.tab-button[data-tab="${tabName}"]`).classList.add("active");

            // 탭 상태 저장 (새로고침 후에도 유지)
            localStorage.setItem("currentTab", tabName);

            // 각 탭별 데이터 로드
            if (tabName === "benefitTab") {
                loadInterestGrants();
            }
            if (tabName === "diagHistoryTab") {
                loadDiagnosisHistory();
            }
            if (tabName === "CalendarTab") {
                // CalendarTab 활성화 시, userCrop 값 확인 후 일정 로드
                var userCropElem = document.getElementById("userCrop");
                if (userCropElem) {
                    var userCrop = userCropElem.value;
                    if (userCrop && userCrop.trim() !== "") {
                        loadCropScheduleAPI(userCrop);
                    } else {
                        document.getElementById("cropScheduleContent").innerHTML = "<p>재배작물을 선택하면 일정이 표시됩니다.</p>";
                    }
                }
            }
        }
    }

    window.showTab = showTab;

    // 기본 탭을 "benefitTab"으로 설정
    if (document.getElementById("benefitTab")) {
        showTab('benefitTab');
    }
});




