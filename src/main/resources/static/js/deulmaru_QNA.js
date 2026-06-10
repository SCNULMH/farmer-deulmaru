
document.addEventListener("DOMContentLoaded", function () {
  console.log("✅ deulmaru_QNA.js 로드 완료");

  const dropdownItems = document.querySelectorAll(".dropdown-menu .dropdown-item");
  dropdownItems.forEach(item => {
    item.addEventListener("click", function (e) {
      e.preventDefault();
      const selectedValue = this.getAttribute("data-value");
      const selectedText = this.textContent;

      const button = document.getElementById("dropdownMenuButton");
      button.textContent = selectedText;
      button.setAttribute("data-search-type", selectedValue);
    });
  });

  const dropdownButton = document.getElementById("dropdownMenuButton");
  dropdownButton.textContent = "제목";
  dropdownButton.setAttribute("data-search-type", "dgnssReqSj");

  const consultQuery = document.getElementById("consultQuery");
  consultQuery.value = "";
  consultQuery.placeholder = "검색어를 입력하세요!";

  fetchAllPagesUntilEmpty("벼", "dgnssReqSj");

  consultQuery.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      pageResultCache = {};
      fetchAllPagesUntilEmpty(consultQuery.value, dropdownButton.getAttribute("data-search-type"));
    }
  });
});

let currentPage = 1;
const resultsPerPage = 10;
let totalResults = 0;
let cachedItems = [];
let pageResultCache = {};
let currentQuery = "";
let currentSearchType = "";
let lastLoadedPage = 0;

function fetchAllPagesUntilEmpty(query, type, page = 1) {
  currentQuery = query;
  currentSearchType = type;

  const url = `http://localhost:8082/ncpms/consult?query=${encodeURIComponent(query)}&type=${type}&page=${page}`;

  fetch(url)
    .then(response => response.text())
    .then(str => new window.DOMParser().parseFromString(str, "application/xml"))
    .then(data => {
      const items = data.getElementsByTagName("item");
      const itemArray = Array.from(items);

      if (itemArray.length === 0) {
        currentPage = 1;
        cachedItems = pageResultCache[1] || [];
        totalResults = Object.values(pageResultCache).reduce((acc, arr) => acc + arr.length, 0);
        displayCurrentPage();
        return;
      }

      pageResultCache[page] = itemArray;
      lastLoadedPage = page;

      fetchAllPagesUntilEmpty(query, type, page + 1);
    })
    .catch(error => {
      console.error("🔴 자동 페이징 에러:", error);
    });
}

function displayCurrentPage() {
  const tableBody = document.querySelector("#consultResultTable tbody");
  tableBody.innerHTML = "";

  cachedItems = pageResultCache[currentPage] || [];
  const pageItems = cachedItems.slice(0, resultsPerPage);

  pageItems.forEach(item => {
    const title = item.getElementsByTagName("dgnssReqSj")[0]?.textContent || "정보 없음";
    const consultId = item.getElementsByTagName("dgnssReqNo")[0]?.textContent || "";
    const requestDate = item.getElementsByTagName("registDatetm")[0]?.textContent || "정보 없음";

    const row = `
      <tr>
        <td>${title}</td>
        <td>${consultId}</td>
        <td>${requestDate}</td>
        <td><button onclick="fetchConsultDetail('${consultId}')">상세보기</button></td>
      </tr>`;
    tableBody.innerHTML += row;
  });

  updatePagination();
}

function updatePagination() {
  const pageInfo = document.getElementById("pageInfo");
  const pageNumbers = document.getElementById("pageNumbers");

  const totalPages = lastLoadedPage;
  // pageInfo.textContent = `페이지 ${currentPage}`; // 디버깅용 코드
  pageNumbers.innerHTML = "";

  let startPage = Math.max(1, currentPage - 2);
  let endPage = Math.min(totalPages, currentPage + 2);

  if (endPage - startPage < 4) {
    if (startPage === 1) {
      endPage = Math.min(startPage + 4, totalPages);
    } else if (endPage === totalPages) {
      startPage = Math.max(endPage - 4, 1);
    }
  }

  for (let i = startPage; i <= endPage; i++) {
    const btn = document.createElement("button");
    btn.textContent = i;
    btn.className = "btn btn-sm btn-outline-dark mx-1" + (i === currentPage ? " active" : "");
    btn.onclick = () => {
      currentPage = i;
      displayCurrentPage();
    };
    pageNumbers.appendChild(btn);
  }
}

window.changePage = function (delta) {
  const newPage = currentPage + delta;
  if (newPage >= 1 && newPage <= lastLoadedPage) {
    currentPage = newPage;
    displayCurrentPage();
  }
};


window.fetchConsultDetail = function (consultId) {
  if (!consultId || consultId.trim() === "") return;
  let url = `http://localhost:8082/ncpms/consult_detail?consult_id=${consultId}`;

  fetch(url)
    .then(response => response.text())
    .then(data => {
      let parser = new DOMParser();
      let xmlDoc = parser.parseFromString(data, "application/xml");
      let title = xmlDoc.getElementsByTagName("dgnssReqSj")[0]?.textContent || "정보 없음";
      let requestContent = xmlDoc.getElementsByTagName("reqestCn")[0]?.textContent || "상담 요청 내용 없음";
      let opinion = xmlDoc.getElementsByTagName("dgnssOpin")[0]?.textContent || "전문가 의견 없음";

      let imageItems = xmlDoc.getElementsByTagName("imageList")[0]?.getElementsByTagName("item");
      let imageHtml = "";
      if (imageItems) {
        for (let i = 0; i < imageItems.length; i++) {
          let imageUrl = imageItems[i].getElementsByTagName("image")[0]?.textContent || "";
          if (imageUrl) {
            imageHtml += `<img src="${imageUrl}" alt="상담 이미지" width="150" style="margin:5px;" onclick="showImageModal('${imageUrl}')">`;
          }
        }
      }

      let html = `
        <div class="consult-detail-container">
          <h2 class="consult-title">${title}</h2>
          <p><strong>상담 요청 내용:</strong> <span class="consult-content">${requestContent}</span></p>
          <p><strong>전문가 의견:</strong> <span class="consult-opinion">${opinion}</span></p>
          <div class="consult-images">${imageHtml}</div>
        </div>`;

      document.getElementById("consultDetailContainer").innerHTML = html;
      document.getElementById("consultDetailModal").style.display = "block";
    })
    .catch(error => {
      console.error("🔴 병해충 상담 상세보기 에러:", error);
    });
};

window.showImageModal = function (imageSrc) {
  const modal = document.getElementById("imageModal");
  const modalImage = document.getElementById("modalImage");
  modalImage.src = imageSrc;
  modal.style.display = "block";
};

function closeImageModal() {
  document.getElementById("imageModal").style.display = "none";
}

window.closeModal = function () {
  document.getElementById("consultDetailModal").style.display = "none";
};

window.addEventListener("keydown", function (e) {
  if (e.key === "Escape") {
    const imageModal = document.getElementById("imageModal");
    const detailModal = document.getElementById("consultDetailModal");
    if (imageModal && imageModal.style.display === "block") {
      closeImageModal();
    } else if (detailModal && detailModal.style.display === "block") {
      closeModal();
    }
  }
});

function toggleChatbot() {
  const chatbot = document.getElementById("chatbot");
  chatbot.style.display = (chatbot.style.display === "none" || chatbot.style.display === "") ? "block" : "none";
}
