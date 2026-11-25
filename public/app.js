// Client-side Javascript for TaxVeda Pro
let currentCalculation = null;

document.addEventListener("DOMContentLoaded", () => {
  calculateTax();
});

function switchTab(tabId) {
  document.querySelectorAll(".pill-btn").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));

  event.currentTarget.classList.add("active");
  document.getElementById(tabId).classList.add("active");
}

function getProfileFromForm() {
  return {
    gross_income: parseFloat(document.getElementById("gross_income").value) || 0,
    basic_salary: parseFloat(document.getElementById("basic_salary").value) || 0,
    prof_tax: parseFloat(document.getElementById("prof_tax").value) || 0,
    hra_received: parseFloat(document.getElementById("hra_received").value) || 0,
    rent_paid: parseFloat(document.getElementById("rent_paid").value) || 0,
    is_metro: document.getElementById("is_metro").checked,
    
    // Loan Deductions & Chapter VI-A
    education_loan_interest: parseFloat(document.getElementById("education_loan_interest").value) || 0,
    ev_loan_interest: parseFloat(document.getElementById("ev_loan_interest").value) || 0,
    sec_80c: parseFloat(document.getElementById("sec_80c").value) || 0,
    sec_80d: parseFloat(document.getElementById("sec_80d").value) || 0,
    sec_80ccd_1b: parseFloat(document.getElementById("sec_80ccd_1b").value) || 0,
    employer_nps: parseFloat(document.getElementById("employer_nps").value) || 0,
    
    // ESOPs & Foreign Income
    rsu_esop_perquisite: parseFloat(document.getElementById("rsu_esop_perquisite").value) || 0,
    foreign_income: parseFloat(document.getElementById("foreign_income").value) || 0,
    foreign_tax_paid: parseFloat(document.getElementById("foreign_tax_paid").value) || 0,
    
    // Capital Gains & Exemptions
    stcg_equity: parseFloat(document.getElementById("stcg_equity").value) || 0,
    ltcg_equity: parseFloat(document.getElementById("ltcg_equity").value) || 0,
    ltcg_property: parseFloat(document.getElementById("ltcg_property").value) || 0,
    sec54_reinvestment: parseFloat(document.getElementById("sec54_reinvestment").value) || 0,
    sec54ec_bonds: parseFloat(document.getElementById("sec54ec_bonds").value) || 0
  };
}

async function calculateTax() {
  const profile = getProfileFromForm();

  try {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile)
    });

    const res = await response.json();
    if (res.status === "success") {
      currentCalculation = res.data;
      updateResultsUI(res.data);
    } else {
      console.error("Calculation error:", res.message);
    }
  } catch (err) {
    console.error("Network error calculating tax:", err);
  }
}

function updateResultsUI(data) {
  const newReg = data.new_regime;
  const oldReg = data.old_regime;
  const cg = data.capital_gains;
  const ftc = data.foreign_tax_credit;
  const rec = data.recommended_regime;
  const savings = data.savings_amount;

  const fmt = (num) => "₹" + Math.round(num || 0).toLocaleString("en-IN");

  // Summary Metrics
  document.getElementById("newTaxVal").innerText = fmt(data.final_new_tax);
  document.getElementById("newTaxableVal").innerText = fmt(newReg.taxable_income);
  document.getElementById("newSalaryTaxVal").innerText = fmt(newReg.total_tax);
  document.getElementById("newCgTaxVal").innerText = fmt(cg.total_cg_tax);
  document.getElementById("newFtcVal").innerText = "- " + fmt(ftc.dtaa_ftc_claim);

  document.getElementById("oldTaxVal").innerText = fmt(data.final_old_tax);
  document.getElementById("oldTaxableVal").innerText = fmt(oldReg.taxable_income);
  document.getElementById("oldSalaryTaxVal").innerText = fmt(oldReg.total_tax);
  document.getElementById("oldCgTaxVal").innerText = fmt(cg.total_cg_tax);
  document.getElementById("oldFtcVal").innerText = "- " + fmt(ftc.dtaa_ftc_claim);

  // Recommendation Badge
  const winnerBadge = document.getElementById("winnerBadge");
  const newBox = document.getElementById("newRegimeCard");
  const oldBox = document.getElementById("oldRegimeCard");

  if (rec === "New Tax Regime") {
    winnerBadge.innerHTML = `<i class="fa-solid fa-trophy"></i> New Regime saves ${fmt(savings)}`;
    newBox.classList.add("winner");
    oldBox.classList.remove("winner");
  } else {
    winnerBadge.innerHTML = `<i class="fa-solid fa-trophy"></i> Old Regime saves ${fmt(savings)}`;
    oldBox.classList.add("winner");
    newBox.classList.remove("winner");
  }

  // Strategy List
  const roadmapContainer = document.getElementById("roadmapList");
  roadmapContainer.innerHTML = "";

  if (data.investment_roadmap && data.investment_roadmap.length > 0) {
    data.investment_roadmap.forEach(step => {
      const item = document.createElement("div");
      item.className = "strategy-item";
      item.innerHTML = `
        <h5>${step.title}</h5>
        <p>${step.action}</p>
        <span class="tag-saving"><i class="fa-solid fa-lightbulb"></i> ${step.investment_tip}</span>
      `;
      roadmapContainer.appendChild(item);
    });
  }

  // Action Items List
  const recContainer = document.getElementById("recommendationsList");
  recContainer.innerHTML = "";

  if (data.recommendations && data.recommendations.length > 0) {
    data.recommendations.forEach(r => {
      const item = document.createElement("div");
      item.className = "action-item";
      item.innerHTML = `
        <h5>${r.title}</h5>
        <p>${r.description}</p>
        ${r.potential_saving > 0 ? `<span class="tag-saving">Save up to ${fmt(r.potential_saving)}</span>` : `<span class="tag-saving">Compliance Task</span>`}
      `;
      recContainer.appendChild(item);
    });
  } else {
    recContainer.innerHTML = `<div class="hint">Tax profile is fully optimized!</div>`;
  }
}

async function sendChatMessage() {
  const input = document.getElementById("chatInput");
  const query = input.value.trim();
  if (!query) return;

  const chatHistory = document.getElementById("chatHistory");

  const userBubble = document.createElement("div");
  userBubble.className = "chat-entry user";
  userBubble.innerHTML = `
    <div class="entry-avatar"><i class="fa-solid fa-user"></i></div>
    <div class="entry-text">${escapeHtml(query)}</div>
  `;
  chatHistory.appendChild(userBubble);
  input.value = "";
  chatHistory.scrollTop = chatHistory.scrollHeight;

  const botBubble = document.createElement("div");
  botBubble.className = "chat-entry bot";
  botBubble.innerHTML = `
    <div class="entry-avatar"><i class="fa-solid fa-shield-halved"></i></div>
    <div class="entry-text"><i class="fa-solid fa-spinner fa-spin"></i> Analyzing official tax laws and profile context...</div>
  `;
  chatHistory.appendChild(botBubble);
  chatHistory.scrollTop = chatHistory.scrollHeight;

  const profile = getProfileFromForm();

  try {
    const response = await fetch("/api/rag/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, profile: profile })
    });

    const res = await response.json();
    if (res.status === "success") {
      const markdownText = res.data.response;
      const citations = res.data.citations || [];

      let parsedHtml = typeof marked !== "undefined" ? marked.parse(markdownText) : markdownText;

      let citationsHtml = "";
      if (citations.length > 0) {
        citationsHtml = `<div class="citations-box"><strong>Official Citations:</strong><br>`;
        citations.forEach(c => {
          citationsHtml += `<a href="${c.url}" target="_blank" class="citation-chip"><i class="fa-solid fa-building-columns"></i> ${c.title}</a>`;
        });
        citationsHtml += `</div>`;
      }

      botBubble.querySelector(".entry-text").innerHTML = parsedHtml + citationsHtml;
    } else {
      botBubble.querySelector(".entry-text").innerText = "Error: " + res.message;
    }
  } catch (err) {
    botBubble.querySelector(".entry-text").innerText = "Unable to connect to tax server.";
  }

  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function askQuickQuery(text) {
  document.getElementById("chatInput").value = text;
  sendChatMessage();
}

function escapeHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
