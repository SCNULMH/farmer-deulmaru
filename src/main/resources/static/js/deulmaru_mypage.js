console.log("✅ deulmaru_mapage.js 로드 완료");
	
 // (1) 관심 지원금 목록을 불러와 각 지원금 상세 정보를 호출하고 카드 생성하는 함수
    function loadInterestGrants() {
        // 우선 benefitTab 내의 기존 UL을 찾거나 없으면 새로 생성
        var $ulContainer = $("#benefitTab ul.benefit-list");
        if ($ulContainer.length === 0) {
            $("#benefitTab").html('<ul class="benefit-list d-flex flex-wrap"></ul>');
            $ulContainer = $("#benefitTab ul.benefit-list");
        }
        
        // 로딩 메시지 표시 (UL 내부 내용 초기화)
        $ulContainer.html("<p>관심 지원금을 불러오는 중...</p>");
        
        // ① 관심 지원금 목록 API 호출
        $.ajax({
            url: "/api/interest/list",
            type: "GET",
            dataType: "json",
            success: function(interests) {
                // 관심 등록한 항목이 없으면 메시지 출력
                if (!interests || interests.length === 0) {
                    $ulContainer.html("<p>관심 등록된 지원금이 없습니다.</p>");
                    return;
                }
                // 컨테이너 초기화
                $ulContainer.empty();
                
                // ② 각 관심 항목에 대해 지원금 상세 정보를 호출
                interests.forEach(function(interest) {
                    var grantId = interest.grantId;
                    
                    $.ajax({
                        url: "/supportApi/api/detail/" + encodeURIComponent(grantId),
                        type: "GET",
                        dataType: "json",
                        data: {
                            typeDv: "json",
                            seq: grantId
                        },
                        success: function(response) {
                            // 외부 API의 응답에서 지원금 상세 정보를 추출
                            var grant = response.policy_result;
                            // 진행 상태 계산 (applEdDt를 기준으로 진행중/마감 판단)
                            var status = getStatus(grant.applEdDt);
                            
                            // 카드 템플릿 생성 (기존 HTML 구조와 동일하게 <li> 요소로 생성)
							var cardHtml = `
							    <li class="card benefit-card">
							        <div class="card-body">
							            <h3 class="card-title">${grant.title || "제목 없음"}</h3>
							            <p class="card-text"><strong>대상 :</strong> ${grant.eduTarget || "대상 정보 없음"}</p>
							            <p class="date-range"><strong>신청기간 :</strong> ${grant.applStDt || "기간 없음"} ~ ${grant.applEdDt || "기간 없음"}</p>
							            <p class="card-ongoing">
							                <strong>진행 상태 :</strong>
							                <span class="${status === '진행중' ? 'ongoing' : 'closed'}">${status}</span>
							            </p>
							            <button class="show-more" onclick="window.location.href='/supportApi/detail/${grant.seq}'">상세보기</button>
							            <button class="cancel-interest-btn" data-grant-id="${grant.seq}">관심 취소</button>
							        </div>
							    </li>
							`;

                            // UL 컨테이너에 카드 추가
                            $ulContainer.append(cardHtml);
                        },
                        error: function() {
                            console.error("지원금 상세 정보를 불러오지 못했습니다. (grantId: " + grantId + ")");
                        }
                    });
                });
            },
            error: function() {
                $ulContainer.html("<p>관심 지원금 목록을 불러오는 데 실패했습니다.</p>");
            }
        });
    }

    // 진행 상태를 계산하는 헬퍼 함수
    function getStatus(applEdDt) {
        if (!applEdDt) return "정보 없음";
        var today = new Date();
        var endDate = new Date(applEdDt);
        if (isNaN(endDate.getTime())) return "정보 없음";
        return today <= endDate ? "진행중" : "마감";
    }
	
    
    // 관심등록 취소 버튼 이벤트
    $(document).on("click", ".cancel-interest-btn", function() {
    var grantId = $(this).data("grant-id");
    var $btn = $(this);
    
    $.ajax({
        url: "/api/interest/cancel",
        type: "DELETE",
        data: { grantId: grantId },
        success: function(response) {
            alert(response); // 해제 성공 메시지 출력
            // 해당 카드 제거 또는 목록 재로딩
            $btn.closest("li.card").remove();
        },
        error: function(xhr) {
            alert("관심 취소 실패! (" + xhr.responseText + ")");
        }
    });
});

    
// 작물 매핑 데이터 (예시: 전체 데이터 대신 일부 예시만 기재)
    var cropMapping = {
    		  "가지": "30770", "갓": "30595", "결구상추": "30596", "고들빼기": "30597", "고사리": "30598", "고추(꽈리고추 반촉성)": "30599",
    		  "고추(보통재배)": "30600", "고추(촉성재배)": "30601", "곰취": "30602", "근대": "30603", "냉이": "30604", "당근": "30605",
    		  "두릅": "30606", "딸기(사계성여름재배)": "30609", "딸기(촉성재배)": "30610", "마늘": "30611", "마늘(잎마늘)": "30612", "멜론": "30613",
    		  "무": "30614", "무(고랭지재배)": "30615", "미나리": "30616", "배추": "30618", "배추(고랭지재배)": "30619", "부추": "30620",
    		  "브로콜리(녹색꽃양배추 고랭지재배)": "30621", "브로콜리(평야지재배)": "30622", "비트": "30623", "상추": "30624", "생강": "30625",
    		  "셀러리(양미나리)": "30626", "수박": "30627", "시금치": "30628", "신선초": "30629", "쑥갓": "30630", "아스파라거스": "30632",
    		  "아욱": "30631", "양배추": "30634", "양파": "30633", "연근": "30635", "오이": "30636", "적채": "30638", "쪽파": "30639",
    		  "참외": "30640", "참취": "30641", "청경채": "30643", "치커리(쌈용 잎치커리)": "258609", "치커리(치콘 뿌리치커리)": "30644",
    		  "컬리플라워(백색꽃양배추 고랭지재배)": "258607", "토란": "30645", "토마토(방울토마토)": "30646", "파": "30647", "파드득나물": "258611",
    		  "파슬리(향미나리)": "258608", "파프리카": "30649", "피망": "30650", "호박": "30651", "호박(늙은호박)": "30652",
    		  "호박(단호박)": "30653", "감귤(노지재배)": "30654", "감귤(시설재배)": "30655", "단감": "30656", "매실": "30658", "무화과(노지재배)": "30659",
    		  "무화과(무가온 시설재배)": "30660","배": "30661", "복숭아": "30662", "블루베리": "258549", "사과": "30663", "살구": "30664",
    		  "양앵두(체리)": "30665", "유자": "30666", "자두": "30667", "참다래": "30668", "포도(무가온)": "30669", "포도(표준가온)": "258613",
    		  "플럼코트": "258633", "한라봉(부지화)": "30670", "기계이앙재배": "30697", "직파재배": "30698", "감자": "30699", "강낭콩": "30700",
    		  "고구마": "30701", "녹두": "30702", "들깨(잎)": "30607", "들깨(종실)": "30703", "땅콩": "30704", "맥주보리": "30705", "메밀": "30706",
    		  "밀": "30707", "수수": "30708", "옥수수": "30709", "완두": "30710", "유채": "30711", "일반보리": "30712", "조": "30713", "참깨": "30714",
    		  "콩": "30715", "팥": "30716", "풋콩": "30717", "느타리버섯": "30733", "양송이": "30735", "영지버섯": "30734", "팽이": "30736",
    		  "구기자": "30739", "길경(도라지)": "30740", "더덕(양유)": "30741", "두충": "30743", "산약(마)": "30747", "오미자": "30749", "천마": "30756",
    		  "황기": "30761"
    };

    // Autocomplete에 사용할 작물명 목록 생성
    var cropNames = Object.keys(cropMapping);

    // jQuery UI Autocomplete 적용
	$(document).ready(function() {
	    $("#cropInput").autocomplete({
	        source: cropNames,
	        minLength: 1,
	        select: function(event, ui) {
	            // 사용자가 항목을 선택하면, 선택한 작물명을 입력 필드와 히든 필드에 설정
	            $("#cropInput").val(ui.item.value);
	            $("#userCrop").val(ui.item.value);
	            
	            // 재배작물 정보를 별도로 업데이트하기 위한 AJAX 호출
	            $.ajax({
	                url: "/mypage/update-crop",
	                type: "POST",
	                data: { userCrop: ui.item.value },
	                success: function(response) {
	                    console.log("재배작물 정보 업데이트 성공:", response);
	                },
	                error: function(xhr, status, error) {
	                    console.error("재배작물 정보 업데이트 실패:", error);
	                }
	            });
	            
	            // 작물 재배 일정 API 호출 (기존 기능)
	            loadCropScheduleAPI(ui.item.value);
	            return false;
	        }
	    });
	});

	

		// 업로드 이미지 확대
	function openImageModal(imageSrc) {
	    // 이미지 경로 설정
	    document.getElementById("modalImage").src = imageSrc;
	    // Bootstrap 모달 열기
	    const modal = new bootstrap.Modal(document.getElementById("imageModal"));
	    modal.show();
	}	
	
// 동적 컨텐츠에 권한 이임
	$(document).on("click", ".diagnosis-image", function () {
	    const src = $(this).attr("src");
	    openImageModal(src);
	});


	

		// 작물 매핑은 이미 프론트엔드에서 사용되고 있지만, CropSchedule API 호출에는 선택된 작물명을 이용합니다.
	 // function to load crop schedule using the selected cropName
	 function loadCropScheduleAPI(cropName) {
	     if (!cropName || cropName.trim() === "") {
	         $("#cropScheduleContent").html("<p>재배작물을 선택해 주세요.</p>");
	         return;
	     }
	     $.ajax({
	         url: "/api/crop-schedule",
	         type: "GET",
	         data: { cropName: cropName },
	         dataType: "html",
	         success: function(response) {
				const displayHtml = `
				                <div class="selected-crop-info">
				                    <p><strong>선택된 작물:</strong> ${cropName}</p>
				                </div>
				                ${response}
				            `;
				            $("#cropScheduleContent").html(displayHtml);
				        },
				        error: function() {
				            $("#cropScheduleContent").html("<p>농작업일정 정보를 불러오는 데 실패했습니다.</p>");
				        }
				    });
				}
	 
	 // 문서 로드 시, 이미 userCrop 값이 있다면 API 호출
	 $(document).ready(function() {
	     var userCrop = $("#userCrop").val();
	     if (userCrop && userCrop.trim() !== "") {
	         loadCropScheduleAPI(userCrop);
	     }
	     
	     // 만약 재배작물 입력값이 변경되면, 변경 이벤트에 따라 API를 재호출할 수도 있습니다.
	     $("#cropInput").on("autocompleteselect", function(event, ui) {
	         // 선택된 값이 히든 필드에 설정되므로, 그 값을 읽어 API 호출
	         var selectedCrop = $("#userCrop").val();
	         loadCropScheduleAPI(selectedCrop);
	     });
	 });
	 
	 
	 function loadDiagnosisHistory() {
	 	        console.log("📡 AI 진단 이력 불러오는 중...");

	 	        fetch("/api/ident/history")
	 	            .then(response => {
	 	                if (!response.ok) throw new Error("진단 이력 응답 실패");
	 	                return response.json();
	 	            })
	 	            .then(data => {
	 	                const tbody = document.querySelector("#diagHistoryTab tbody");
	 	                tbody.innerHTML = "";

	 	                if (!data || data.length === 0) {
	 	                    tbody.innerHTML = `<tr><td colspan="5">진단 이력이 없습니다.</td></tr>`;
	 	                    return;
	 	                }

	 	                data.forEach(history => {
	 	                    const row = document.createElement("tr");

	 	                    const date = new Date(history.identificationTime);
	 	                    const formattedDate = date.toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });

	 	                    const imgName = history.imagePath.split("/").pop();

							row.innerHTML = `
							    <td>${formattedDate}</td>
							    <td>${history.cropName}</td>
							    <td>${history.diseaseName}</td>
							    <td>${history.confidenceScore}%</td>
							    <td>
							        <img src="/uploads/${imgName}" 
							             class="img-thumbnail diagnosis-image"
							             style="width:100px; height:auto; cursor:pointer;">
							    </td>
							    <td><button class="btn btn-danger btn-sm" onclick="deleteHistory(${history.id})">삭제</button></td>
							`;


	 	                    tbody.appendChild(row);
	 	                });

	 	                console.log("✅ AI 진단 이력 불러오기 완료");
	 	            })
	 	            .catch(error => {
	 	                console.error("❌ 진단 이력 불러오기 실패:", error);
	 	                const tbody = document.querySelector("#diagHistoryTab tbody");
	 	                tbody.innerHTML = `<tr><td colspan="5">진단 이력 조회 중 오류 발생</td></tr>`;
	 	            });
	 	    }
	 		

	 		function deleteHistory(id) {
	 		    if (!confirm("정말 이 진단 이력을 삭제하시겠습니까?")) return;

	 		    fetch(`/api/ident/delete/${id}`, {
	 		        method: "DELETE"
	 		    })
	 		    .then(response => {
	 		        if (!response.ok) throw new Error("삭제 실패");
	 		        alert("✅ 진단 이력이 삭제되었습니다.");
	 		        location.reload(); // 또는 해당 행만 remove()
	 		    })
	 		    .catch(error => {
	 		        console.error("❌ 삭제 오류:", error);
	 		        alert("❌ 진단 이력 삭제 중 오류가 발생했습니다.");
	 		    });
	 		}
