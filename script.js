let uploadedFile = null;

let allRecommendations = [];

window.addEventListener("DOMContentLoaded", () => {

  fetch("/dataset")
    .then(res => res.json())
    .then(data => renderDataset(data));

});

function renderDataset(items) {

  const grid = document.getElementById("dataset-grid");

  grid.innerHTML = "";

  items.forEach(item => {

    const card = document.createElement("div");

    card.className = "dataset-card";

    card.innerHTML = `
      <img class="ds-img" src="/images/${item.image_file}">

      <div class="ds-label">${item.name}</div>
    `;

    grid.appendChild(card);

  });
}

document.getElementById("file-input")
  .addEventListener("change", function () {

    const file = this.files[0];

    if (!file) return;

    uploadedFile = file;

    const reader = new FileReader();

    reader.onload = function (e) {

      document.getElementById("preview-img").src = e.target.result;

      document.getElementById("preview-name").textContent = file.name;

      document.getElementById("preview-area")
        .classList.add("visible");

      document.getElementById("recommend-btn").disabled = false;
    };

    reader.readAsDataURL(file);
  });

function clearUpload() {

  uploadedFile = null;

  document.getElementById("file-input").value = "";

  document.getElementById("preview-area")
    .classList.remove("visible");
}

function getRecommendations() {

  if (!uploadedFile) return;

  const formData = new FormData();

  formData.append("image", uploadedFile);

  fetch("/recommend", {
    method: "POST",
    body: formData
  })
    .then(res => res.json())
    .then(data => {

      allRecommendations = data.recommendations;

      renderResults(
        data.recommendations,
        data.detected_category,
        data.detected_texture
      );
    });
}

function renderResults(recommendations, category, texture) {

  document.getElementById("results-meta").innerHTML = `
    Category: <strong>${category}</strong>
    <br>
    Texture: <strong>${texture}</strong>
  `;

  applyFilters();

  document.getElementById("results-section")
    .classList.add("visible");
}

function applyFilters() {

  const search = document.getElementById("search-box")
    .value.toLowerCase();

  const category = document.getElementById("filter-category")
    .value;

  const grid = document.getElementById("results-grid");

  grid.innerHTML = "";

  const filtered = allRecommendations.filter(item => {

    const matchesSearch = item.name
      .toLowerCase()
      .includes(search);

    const matchesCategory =
      category === "all" ||
      item.category.includes(category);

    return matchesSearch && matchesCategory;
  });

  filtered.forEach(item => {

    const card = document.createElement("div");

    card.className = "result-card";

    card.innerHTML = `

      <img class="card-img" src="${item.image_url}">

      <div class="card-body">

        <div class="card-name">${item.name}</div>

        <div class="card-desc">
          ${item.category} · ${item.texture}
        </div>

        <div class="match-pct">
          ${item.similarity}% Match
        </div>

      </div>
    `;

    grid.appendChild(card);
  });
}

document.getElementById("search-box")
  .addEventListener("input", applyFilters);

document.getElementById("filter-category")
  .addEventListener("change", applyFilters);