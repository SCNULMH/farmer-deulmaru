const form = document.querySelector("#diagnosisForm");
const result = document.querySelector("#diagnosisResult");
const chatbotToggle = document.querySelector("[data-chatbot-toggle]");
const chatbotClose = document.querySelector("[data-chatbot-close]");
const chatbotPanel = document.querySelector("#chatbotPanel");
const manualToggle = document.querySelector("[data-manual-toggle]");
const usageModal = document.querySelector("#usageModal");
const usageModalClose = document.querySelector("[data-usage-modal-close]");
let latestDiagnosis = null;

function setChatbotOpen(isOpen) {
  if (!chatbotPanel || !chatbotToggle) return;
  chatbotPanel.hidden = !isOpen;
  chatbotToggle.setAttribute("aria-expanded", String(isOpen));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
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
    closeUsageModal();
  }
});

function closeUsageModal() {
  if (!usageModal) return;
  usageModal.hidden = true;
  if (manualToggle) {
    manualToggle.setAttribute("aria-expanded", "false");
  }
}

function openUsageModal() {
  if (!usageModal) return;
  usageModal.hidden = false;
  if (manualToggle) {
    manualToggle.setAttribute("aria-expanded", "true");
  }
}

if (manualToggle) {
  manualToggle.addEventListener("click", openUsageModal);
}

if (usageModal) {
  usageModal.addEventListener("click", (event) => {
    if (event.target === usageModal) {
      closeUsageModal();
    }
  });
}

if (usageModalClose) {
  usageModalClose.addEventListener("click", closeUsageModal);
}

if (form && result) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    latestDiagnosis = null;
    result.innerHTML = "<strong>진단 중입니다.</strong><p>이미지를 읽고 진단 모델에 전달하고 있습니다.</p>";

    try {
      const response = await fetch("/api/diagnosis", {
        method: "POST",
        body: new FormData(form),
      });
      const data = await response.json();

      if (!data.ok) {
        result.innerHTML = `<strong>진단 실패</strong><p>${escapeHtml(data.message)}</p>`;
        return;
      }

      latestDiagnosis = {
        crop: data.crop,
        disease: data.disease,
        confidence: data.confidence,
        filename: data.filename,
      };

      const relatedPests = (data.related_pests || []).map((pest) => `
        <article class="related-pest-card">
          ${pest.image || pest.thumb ? `<img src="${escapeHtml(pest.image || pest.thumb)}" alt="${escapeHtml(pest.name)}" onerror="this.remove()">` : ""}
          <div>
            <strong>${escapeHtml(pest.name || "병해충 정보")}</strong>
            <p>${escapeHtml(pest.crop || data.crop)}</p>
            ${pest.sick_key ? `<a href="/dictionary?query=${encodeURIComponent(pest.name)}&search_type=sick">병해충 사전에서 확인</a>` : ""}
          </div>
        </article>
      `).join("");

      result.innerHTML = `
        <strong>${escapeHtml(data.disease)}</strong>
        <p>${escapeHtml(data.crop)} 이미지 ${escapeHtml(data.filename)} (${escapeHtml(data.size_kb)}KB)</p>
        <p>신뢰도 ${escapeHtml(data.confidence)}%</p>
        <p>${escapeHtml(data.next_action)}</p>
        <p class="muted">분석 모드: ${escapeHtml(data.model_mode || "서버 응답 확인 필요")}</p>
        ${data.model_note ? `<p class="muted">${escapeHtml(data.model_note)}</p>` : ""}
        <button type="button" class="diagnosis-save-button" data-diagnosis-save>진단 이력 저장</button>
        ${relatedPests ? `<div class="related-pest-list"><p><strong>관련 병해충 정보</strong></p>${relatedPests}</div>` : ""}
        <p class="muted">저장 버튼을 누르면 마이페이지 진단 이력에 보관됩니다.</p>
      `;
    } catch (error) {
      result.innerHTML = `
        <strong>추론 모델 예시 결과</strong>
        <p>현재 배포 서버는 무료 임시 환경이라 PyTorch 추론 과정에서 응답이 지연되거나 중단될 수 있습니다.</p>
        <p>서비스 구조는 업로드 이미지 기반 추론 모델을 호출하도록 구성되어 있으며, 아래 결과는 시연용 예시입니다.</p>
        <p class="muted">분석 모드: inference-demo</p>
      `;
    }
  });
}

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-diagnosis-save]");
  if (!button || !latestDiagnosis) return;

  button.disabled = true;
  button.textContent = "저장 중";

  try {
    const response = await fetch("/api/diagnosis/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(latestDiagnosis),
    });

    if (!response.ok) {
      throw new Error("save failed");
    }

    button.textContent = "저장됨";
    latestDiagnosis = null;
  } catch (error) {
    button.textContent = "저장 실패";
    button.disabled = false;
  }
});

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
