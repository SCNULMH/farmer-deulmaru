const form = document.querySelector("#diagnosisForm");
const result = document.querySelector("#diagnosisResult");

if (form && result) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    result.innerHTML = "<strong>진단 중입니다.</strong><p>이미지를 읽고 데모 진단 모델에 전달하고 있습니다.</p>";

    try {
      const response = await fetch("/api/diagnosis", {
        method: "POST",
        body: new FormData(form),
      });
      const data = await response.json();

      if (!data.ok) {
        result.innerHTML = `<strong>진단 실패</strong><p>${data.message}</p>`;
        return;
      }

      result.innerHTML = `
        <strong>${data.disease}</strong>
        <p>${data.crop} 이미지 ${data.filename} (${data.size_kb}KB)</p>
        <p>신뢰도 ${data.confidence}% · ${data.model_mode} mode</p>
        <p>${data.next_action}</p>
        <p class="muted">분석 결과는 최근 진단 기록에 저장됩니다.</p>
      `;
    } catch (error) {
      result.innerHTML = "<strong>진단 실패</strong><p>서버 응답을 확인해 주세요.</p>";
    }
  });
}

document.querySelectorAll(".interest-button").forEach((button) => {
  button.addEventListener("click", async () => {
    const grantId = button.dataset.grantId;
    button.disabled = true;
    const response = await fetch(`/api/interests/${grantId}`, { method: "POST" });
    if (response.ok) {
      button.textContent = "저장됨";
    } else {
      button.textContent = "저장 실패";
      button.disabled = false;
    }
  });
});
