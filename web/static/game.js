async function createPlayer() {
    const name = document.getElementById("playerName").value;
    const res = await fetch("/create_player", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    });
    const data = await res.json();
    document.getElementById("output").textContent = JSON.stringify(data.player, null, 2);
}

async function endMonth() {
    const res = await fetch("/end_month", { method: "POST" });
    const data = await res.json();
    document.getElementById("output").textContent = "Resources:\n" + JSON.stringify(data.resources, null, 2);
}