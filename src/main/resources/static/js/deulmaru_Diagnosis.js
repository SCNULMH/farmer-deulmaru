let uploadedFile = null; // 업로드된 파일 저장
let diagnosisStarted = false; // 진단 진행 여부
let predictionResult = ""; // 예측된 병 코드 및 이름 저장


// 파일 업로드 이벤트 핸들러
function handleFileUpload(files) {
	const resultText = document.getElementById("result-text");
	const diagnosisButton = document.getElementById("diagnosis-button");

	if (files.length === 0) {
		return;
	}

	const file = files[0]; // 하나의 파일만 처리
	const maxFileSize = 10 * 1024 * 1024; // 10MB 제한

	if (file.size > maxFileSize) {
		resultText.textContent = "🚨 파일 크기가 너무 큽니다. 10MB 이하로 업로드 해주세요.";
		return;
	}

	uploadedFile = file;
	resultText.textContent = "📂 파일이 업로드되었습니다. 작물명을 입력하고 '진단하기' 버튼을 눌러주세요.";
	diagnosisButton.disabled = false;

	// 파일 이름 표시
	updateFileList(file);

	// 업로드한 이미지의 썸네일로 대체
	const reader = new FileReader();
	reader.onload = function(e) {
		const dropFile = document.getElementById("drop-file");
		const imageElement = dropFile.querySelector("img");
		imageElement.src = e.target.result;
		const messageElement = dropFile.querySelector(".message");
		if (messageElement) {
			messageElement.style.display = "none";
		}
	};
	reader.readAsDataURL(file);
}

// 파일 목록 업데이트 함수
function updateFileList(file) {
	const fileList = document.getElementById("file-list");
	fileList.innerHTML = `<div class="file-item">📂 ${file.name}</div>`;
}

// 드래그 앤 드롭 기능 추가
function setUpDragAndDrop() {
	const dropZone = document.getElementById("drop-file");
	const fileInput = document.getElementById("chooseFile");

	// 드래그 앤 드롭 이벤트 등록
	dropZone.addEventListener("dragover", function (event) {
		event.preventDefault();
		dropZone.style.border = "3px solid #1e824c"; // 강조 효과
	});

	dropZone.addEventListener("dragleave", function () {
		dropZone.style.border = "3px dashed #dbdbdb"; // 원래대로
	});

	dropZone.addEventListener("drop", function (event) {
		event.preventDefault();
		dropZone.style.border = "3px dashed #dbdbdb"; // 원래대로

		const files = event.dataTransfer.files;
		fileInput.files = files; // input에도 반영
		handleFileUpload(files); // ✅ 여기서 기존 업로드 처리 함수 호출
	});
}

// 진단 버튼 클릭 시 실행될 함수
function startDiagnosis() {
	if (!uploadedFile) {
		alert("❌ 파일을 먼저 업로드하세요!");
		return;
	}

	const cropName = document.getElementById("cropNameInput").value.trim();
	if (!cropName) {
		alert("❌ 작물명을 입력하세요.");
		return;
	}

	const resultText = document.getElementById("result-text");
	const formData = new FormData();
	formData.append("file", uploadedFile);
	formData.append("cropName", cropName);

	resultText.textContent = "🔍 분석 중... 잠시만 기다려주세요.";

	// '/upload' 엔드포인트로 POST 요청 (FileUploadController에 대응)
	fetch('/upload', {
		method: 'POST',
		body: formData
	})
		.then(response => {
			if (!response.ok) {
				throw new Error(`🚨 서버 오류: ${response.status}`);
			}
			return response.json();
		})
		.then(data => {
			if (data.prediction) {
				// 예시: 예측 결과 문자열이 "병명1" 또는 "정상" 등으로 반환
				predictionResult = data.prediction;
				resultText.textContent = ` ${predictionResult}`;

				// 업로드한 이미지 표시
				const resultImage = document.getElementById("result-image");
				resultImage.src = data.imageUrl;
				resultImage.style.display = "none";

				// 진단 이력 저장 영역 표시
				document.getElementById("save-history-container").style.display = "block";
			} else if (data.message) {
				resultText.textContent = `❌ ${data.message}`;
			} else {
				resultText.textContent = "❌ 예측 실패: 서버에서 데이터를 받지 못했습니다.";
			}
		})
		.catch(error => {
			resultText.textContent = "❌ 진단 실패! 다시 시도해주세요.";
			console.error('Error:', error);
		});
}

// 진단 이력 저장 버튼 클릭 시 실행될 함수
async function saveDiagnosisHistory() {
	const userId = sessionStorage.getItem("userId");
	const resultText = document.getElementById("result-text").innerText.trim();
	const cropName = document.getElementById("cropNameInput").value.trim();
	const file = document.getElementById("chooseFile").files[0];

	if (!file || !cropName) {
		alert("❌ 작물명과 이미지를 입력해야 합니다.");
		return;
	}

	try {
		const resultText = document.getElementById("result-text").innerText.trim();

		// 예시 결과 텍스트: "병해충 진단 결과: 정상, 정확도: 98.5%"
		const match = resultText.match(/병해충 진단 결과:\s*(.+?),\s*정확도:\s*([\d.]+)%/);

		if (!match) {
			alert("❌ 결과를 파싱할 수 없습니다. 형식이 올바르지 않습니다.");
			return;
		}

		const diseaseName = match[1]; // "정상" 등
		const confidenceScore = parseFloat(match[2]); // 98.5 등

		const formData = new FormData();
		formData.append("userId", userId);
		formData.append("diseaseName", diseaseName);
		formData.append("confidenceScore", confidenceScore);
		formData.append("cropName", cropName);
		formData.append("file", file);

		const response = await fetch("/api/ident/save", {
			method: "POST",
			body: formData,
			credentials: "include",
		});

		if (response.ok) {
			console.log("진단 이력이 성공적으로 저장되었습니다.");
			alert("진단 이력이 성공적으로 저장되었습니다!")
		} else {
			const result = await response.json();
			document.getElementById("result-text").textContent = "❌ 진단 이력 저장 실패: " + result.error;
		}
	} catch (error) {
		console.error("🚨 서버 오류 발생:", error);
		document.getElementById("result-text").textContent = "🚨 서버 오류 발생: " + error;
	}
}

// 설명 토글
function toggleGuide() {
	let guideContent = document.getElementById("aiGuide");
	let button = document.querySelector(".btn-show-more");

	// `show` 클래스를 토글하여 max-height 변경
	guideContent.classList.toggle("show");

	if (guideContent.classList.contains("show")) {
		button.innerHTML = "▲"; // 버튼 아이콘 변경
	} else {
		button.innerHTML = "▼"; // 버튼 아이콘 변경
	}
}

// 이삭이
function toggleChatbot() {
	const chatbot = document.getElementById("chatbot");
	chatbot.style.display = (chatbot.style.display === "none" || chatbot.style.display === "") ? "block" : "none";
}



// 이벤트 리스너 등록
document.getElementById("chooseFile").addEventListener("change", function(event) {
	handleFileUpload(event.target.files);
});

document.getElementById("diagnosis-button").addEventListener("click", startDiagnosis);
document.getElementById("save-history-button").addEventListener("click", saveDiagnosisHistory);
document.addEventListener("DOMContentLoaded", setUpDragAndDrop);
