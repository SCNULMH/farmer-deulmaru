const form = document.querySelector("#diagnosisForm");
const result = document.querySelector("#diagnosisResult");
const chatbotToggle = document.querySelector("[data-chatbot-toggle]");
const chatbotClose = document.querySelector("[data-chatbot-close]");
const chatbotPanel = document.querySelector("#chatbotPanel");

function setChatbotOpen(isOpen) {
  if (!chatbotPanel || !chatbotToggle) return;
  chatbotPanel.hidden = !isOpen;
  chatbotToggle.setAttribute("aria-expanded", String(isOpen));
}

if (chatbotToggle && chatbotPanel) {
  chatbotToggle.addEventListener("click", () => {
    setChatbotOpen(chatbotPanel.hidden);
  });
}

if (chatbotClose) {
  chatbotClose.addEventListener("click", () => setChatbotOpen(false));
}

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    setChatbotOpen(false);
  }
});

if (form && result) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    result.innerHTML = "<strong>진단 중입니다.</strong><p>이미지를 읽고 진단 모델에 전달하고 있습니다.</p>";

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

      const relatedPests = (data.related_pests || []).map((pest) => `
        <article class="related-pest-card">
          ${pest.image || pest.thumb ? `<img src="${pest.image || pest.thumb}" alt="${pest.name}" onerror="this.remove()">` : ""}
          <div>
            <strong>${pest.name || "병해충 정보"}</strong>
            <p>${pest.crop || data.crop}</p>
            ${pest.sick_key ? `<a href="/dictionary?query=${encodeURIComponent(pest.name)}&search_type=sick">병해충 사전에서 확인</a>` : ""}
          </div>
        </article>
      `).join("");

      result.innerHTML = `
        <strong>${data.disease}</strong>
        <p>${data.crop} 이미지 ${data.filename} (${data.size_kb}KB)</p>
        <p>신뢰도 ${data.confidence}%</p>
        <p>${data.next_action}</p>
        ${relatedPests ? `<div class="related-pest-list"><p><strong>관련 병해충 정보</strong></p>${relatedPests}</div>` : ""}
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
