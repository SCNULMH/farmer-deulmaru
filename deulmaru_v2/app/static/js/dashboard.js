const form = document.querySelector("#diagnosisForm");
const result = document.querySelector("#diagnosisResult");

if (form && result) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    result.innerHTML = "<strong>분석 중입니다.</strong><p>이미지와 작물 정보를 확인하고 있습니다.</p>";

    const response = await fetch("/api/diagnosis", {
      method: "POST",
      body: new FormData(form),
    });
    const data = await response.json();

    if (!data.ok) {
      result.innerHTML = `<strong>분석 실패</strong><p>${data.message}</p>`;
      return;
    }

    result.innerHTML = `
      <strong>${data.disease}</strong>
      <p>${data.crop} 이미지 ${data.filename} (${data.size_kb}KB)</p>
      <p>신뢰도 ${data.confidence}% · ${data.model_mode} mode</p>
      <p>${data.next_action}</p>
      <p class="muted">결과가 진단 이력에 저장되었습니다. 새로고침하면 이력 카드에서 확인할 수 있습니다.</p>
    `;
  });
}

document.querySelectorAll(".interest-button").forEach((button) => {
  button.addEventListener("click", async () => {
    const grantId = button.dataset.grantId;
    button.disabled = true;
    const response = await fetch(`/api/interests/${grantId}`, { method: "POST" });
    if (response.ok) {
      button.textContent = "등록 완료";
    } else {
      button.textContent = "다시 시도";
      button.disabled = false;
    }
  });
});
