document.addEventListener("DOMContentLoaded", function() {
    const alarmIcon = document.getElementById("alarmIcon");
    const alarmList = document.getElementById("alarmList");
    const alarmCountBadge = document.getElementById("alarmCountBadge");

    // (1) 페이지 로딩 시, 미리 알림 건수를 업데이트하고 싶다면 여기서 fetch
    updateAlarmCount();

    if (alarmIcon && alarmList) {
        alarmIcon.addEventListener("click", function() {
            // (2) 아이콘 클릭 시에도 알림 목록을 가져오고, 건수/목록 표시
            fetch("/api/interest/list")
                .then(response => response.json())
                .then(data => {
                    const alarms = data.filter(item => item.notifyYn === true);
                    // 알림 개수 표시
                    updateAlarmBadge(alarms.length);
                    // 드롭다운 내용 렌더링
                    renderAlarmList(alarms);

                    // 드롭다운 토글
                    if (alarmList.style.display === "none" || alarmList.style.display === "") {
                        alarmList.style.display = "block";
                    } else {
                        alarmList.style.display = "none";
                    }
                })
                .catch(error => console.error("알림 목록 조회 오류:", error));
        });
    } else {
        console.log("알림 아이콘/목록 요소가 없을 수 있음(비로그인 상태 등)");
    }

    // 알림 목록 렌더링
    function renderAlarmList(alarms) {
        alarmList.innerHTML = "";
        if (alarms.length === 0) {
            alarmList.innerHTML = "<p style='padding:10px;'>새로운 알림이 없습니다.</p>";
            return;
        }
        alarms.forEach(alarm => {
            const item = document.createElement("div");
            item.style.padding = "10px";
            item.style.borderBottom = "1px solid #ccc";
            item.style.cursor = "pointer";
            item.textContent = `지원금(${alarm.title}) 마감이 임박했습니다.`;
            item.addEventListener("click", function() {
                window.location.href = `/supportApi/detail/${alarm.grantId}`;
            });
            alarmList.appendChild(item);
        });
    }

    // 알림 건수를 업데이트하는 함수
    function updateAlarmBadge(count) {
        if (!alarmCountBadge) return;
        if (count > 0) {
            alarmCountBadge.textContent = count;
            alarmCountBadge.style.display = "inline-block";
        } else {
            alarmCountBadge.style.display = "none";
        }
    }

    // (옵션) 페이지 로드 시 자동으로 알림 건수 갱신
    function updateAlarmCount() {
        fetch("/api/interest/list")
            .then(response => response.json())
            .then(data => {
                const alarms = data.filter(item => item.notifyYn === true);
                updateAlarmBadge(alarms.length);
            })
            .catch(err => console.error("초기 알림 건수 조회 오류:", err));
    }
});
