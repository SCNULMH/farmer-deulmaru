// ✅ 드롭다운 및 검색 이벤트 등록

document.addEventListener("DOMContentLoaded", function(){
  console.log("✅ deulmaru_dictionary_search.js 로드 완료");

  // 드롭다운 메뉴 항목 클릭 시 선택값 업데이트
  var dropdownItems = document.querySelectorAll('#searchTypeDropdown + .dropdown-menu .dropdown-item');
  dropdownItems.forEach(function(item){
    item.addEventListener("click", function(e){
      e.preventDefault();
      var selectedValue = this.getAttribute("data-value");
      var selectedText = this.textContent;
      var dropdownButton = document.getElementById("searchTypeDropdown");
      dropdownButton.textContent = selectedText;
      dropdownButton.setAttribute("data-value", selectedValue);
    });
  });

  // 검색창 Enter 키 이벤트
  const searchQueryElem = document.getElementById("searchQuery");
  if (searchQueryElem) {
    searchQueryElem.addEventListener("keypress", function(event) {
      if (event.key === "Enter") {
        fetchSearchData();
      }
    });
  }
});

// ✅ 초기 상태 세팅

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("searchQuery").value = "";
  document.getElementById("searchQuery").placeholder = "검색어를 입력하세요!";
  document.getElementById("searchTypeDropdown").setAttribute("data-value", "crop");
  document.getElementById("searchTypeDropdown").textContent = "작물명";
  fetchSearchData("벼");
});

// ✅ 병해충 검색
window.fetchSearchData = function (customQuery) {
  let query = customQuery || document.getElementById("searchQuery").value;
  let searchType = document.getElementById("searchTypeDropdown").getAttribute("data-value") || "sick";
  if (!query) {
    alert("검색어를 입력하세요!");
    return;
  }
  let url = `http://localhost:8082/ncpms/search?query=${encodeURIComponent(query)}&type=${searchType}`;
  console.log("🔍 병해충 검색 요청 URL:", url);

  fetch(url)
    .then(response => response.text())
    .then(str => new window.DOMParser().parseFromString(str, "application/xml"))
    .then(data => {
      let resultContainer = document.getElementById("resultTable");
      resultContainer.innerHTML = "";
      let items = data.getElementsByTagName("item");
      for (let item of items) {
        let cropName = item.getElementsByTagName("cropName")[0]?.textContent || "정보 없음";
        let sickNameKor = item.getElementsByTagName("sickNameKor")[0]?.textContent || "정보 없음";
        let sickNameEng = item.getElementsByTagName("sickNameEng")[0]?.textContent || "정보 없음";
        let sickNameChn = item.getElementsByTagName("sickNameChn")[0]?.textContent || "정보 없음";
        let thumbImg = item.getElementsByTagName("thumbImg")[0]?.textContent || "";
        let sickKey = item.getElementsByTagName("sickKey")[0]?.textContent || "";

        let cardHtml = `
          <a href="#" class="col-md-4 col-sm-6 mb-4" onclick="fetchSickDetail('${sickKey}')">
            <div class="card dictionary-card">
              <img src="${thumbImg}" class="card-img-top" alt="${sickNameKor}">
              <div class="card-body">
                  <h3 class="insect-ttl">${sickNameKor}</h3>
                  <h4 class="crop-type">${cropName}</h4>
                  <p class="insect-ttl-eng">${sickNameEng}</p>
                  <p class="insect-ttl-chn">${sickNameChn}</p>
              </div>
            </div>
          </a>`;
        resultContainer.innerHTML += cardHtml;
      }
      document.getElementById("dictionary").classList.remove("hidden");
    })
    .catch(error => {
      console.error("🔴 병해충 검색 에러:", error);
    });
};

// ✅ 상세보기 모달 열기
window.fetchSickDetail = function(sickKey) {
  if (!sickKey || sickKey.trim() === "") return;
  let url = `http://localhost:8082/ncpms/sick_detail?sick_key=${encodeURIComponent(sickKey)}`;
  console.log("🔍 병해충 상세보기 요청 URL:", url);

  fetch(url)
    .then(response => response.text())
    .then(xmlText => {
      let xmlDoc = new window.DOMParser().parseFromString(xmlText, "application/xml");
      let cropName = xmlDoc.getElementsByTagName("cropName")[0]?.textContent || "정보 없음";
      let sickNameKor = xmlDoc.getElementsByTagName("sickNameKor")[0]?.textContent || "정보 없음";
      let sickNameChn = xmlDoc.getElementsByTagName("sickNameChn")[0]?.textContent || "정보 없음";
      let preventionMethod = xmlDoc.getElementsByTagName("preventionMethod")[0]?.textContent || "정보 없음";
      let developmentCondition = xmlDoc.getElementsByTagName("developmentCondition")[0]?.textContent || "정보 없음";
      let symptoms = xmlDoc.getElementsByTagName("symptoms")[0]?.textContent || "정보 없음";

      let virusImgList = xmlDoc.getElementsByTagName("imageList")[0];
      let virusImagesHtml = "";
      if (virusImgList) {
        let items = virusImgList.getElementsByTagName("item");
        for (let i = 0; i < items.length; i++) {
          let rawImageUrl = items[i].getElementsByTagName("image")[0]?.textContent || "";
          let imageTitle = items[i].getElementsByTagName("imageTitle")[0]?.textContent || "";
          let imageUrl = rawImageUrl;
          virusImagesHtml += `
            <div style="display:inline-block; margin:10px; text-align:center;">
              <img src="${imageUrl}" alt="${imageTitle}" style="max-width:200px; cursor:pointer; border-radius:8px;"
                   onclick="openImageModal('${imageUrl}')" onerror="this.src='/image/noimage.png'">
              <div style="margin-top:5px;">${imageTitle}</div>
            </div>`;
        }
      }

      let detailHtml = `
        <h3>${sickNameKor} (${sickNameChn})</h3>
        <p><strong>작물명:</strong> ${cropName}</p>
        <p><strong>예방 방법:</strong> ${preventionMethod}</p>
        <p><strong>발병 조건:</strong> ${developmentCondition}</p>
        <p><strong>증상:</strong> ${symptoms}</p>
        <div><strong>관련 이미지:</strong><br>${virusImagesHtml}</div>`;

      document.getElementById("sickDetailContainer").innerHTML = detailHtml;
      document.getElementById("sickDetailModal").style.display = "block";
    })
    .catch(error => {
      console.error("🔴 상세보기 에러:", error);
    });
};

// ✅ 상세 모달 닫기
function closeSickDetailModal() {
  document.getElementById("sickDetailModal").style.display = "none";
}

/// ✅ 이미지 확대 모달 열기 (CSS 확대만 적용)
window.openImageModal = function (src) {
  const modal = document.getElementById("imageModal");
  const modalImg = document.getElementById("modalImage");
  modalImg.src = src;
  modal.style.display = "flex";
};

document.addEventListener("DOMContentLoaded", function () {
  const imageModal = document.getElementById("imageModal");
  const sickDetailModal = document.getElementById("sickDetailModal");

  // ✅ 이미지 모달 닫기 (클릭 시)
  if (imageModal) {
    imageModal.addEventListener("click", function () {
      imageModal.style.display = "none";
    });
  }

  // ✅ ESC 누르면 순서대로 모달 닫기
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      if (imageModal && imageModal.style.display === "flex") {
        imageModal.style.display = "none";
      } else if (sickDetailModal && sickDetailModal.style.display === "block") {
        sickDetailModal.style.display = "none";
      }
    }
  });
});

