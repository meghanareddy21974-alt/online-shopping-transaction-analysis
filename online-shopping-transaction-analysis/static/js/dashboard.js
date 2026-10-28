const charts = {};
const fmt = n => Number(n).toLocaleString(undefined, { maximumFractionDigits: 2 });

function draw(id, type, labels, data, label) {
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart(document.getElementById(id), {
    type,
    data: { labels, datasets: [{ label, data, borderColor: "#2563eb", backgroundColor: type === "line" ? "rgba(37,99,235,.15)" : undefined, fill: type === "line", tension: .3 }] },
    options: { plugins: { legend: { display: type === "doughnut" } } }
  });
}

function table(id, headers, rows) {
  document.getElementById(id).innerHTML =
    "<tr>" + headers.map(h => `<th>${h}</th>`).join("") + "</tr>" +
    rows.map(r => "<tr>" + r.map(c => `<td>${c}</td>`).join("") + "</tr>").join("");
}

async function load() {
  const p = new URLSearchParams();
  const s = document.getElementById("start").value, e = document.getElementById("end").value;
  if (s) p.set("start", s);
  if (e) p.set("end", e);
  const d = await (await fetch("/api/report?" + p)).json();
  const k = d.kpis;

  document.getElementById("empty").hidden = k.orders > 0 || d.status.length > 0;
  document.getElementById("kpis").innerHTML = [
    ["Revenue", fmt(k.revenue)], ["Orders", fmt(k.orders)], ["Customers", fmt(k.customers)],
    ["Avg order value", fmt(k.avg_order_value)], ["Repeat customers", k.repeat_rate + "%"],
    ["Return rate", k.return_rate + "%"], ["Cancel rate", k.cancel_rate + "%"]
  ].map(([t, v]) => `<div class="card"><span>${t}</span><b>${v}</b></div>`).join("");

  draw("monthly", "line", d.monthly.map(x => x.month), d.monthly.map(x => x.revenue), "Revenue");
  draw("category", "bar", d.categories.map(x => x.category), d.categories.map(x => x.revenue), "Revenue");
  draw("payment", "doughnut", d.payments.map(x => x.payment_method), d.payments.map(x => x.count), "Orders");
  draw("status", "doughnut", d.status.map(x => x.status), d.status.map(x => x.count), "Orders");
  table("products", ["Product", "Units", "Revenue"], d.top_products.map(x => [x.product, fmt(x.units), fmt(x.revenue)]));
  table("customers", ["Customer", "Orders", "Spent"], d.top_customers.map(x => [x.customer_id, x.orders, fmt(x.spent)]));
}

document.getElementById("apply").onclick = load;
document.getElementById("reset").onclick = () => {
  document.getElementById("start").value = document.getElementById("end").value = "";
  load();
};
load();
