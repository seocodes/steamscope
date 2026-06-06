const form = document.getElementById("advisor-form");

form.addEventListener('submit', async function(event) {
    event.preventDefault();
    const game_title = document.getElementById("title").value;
    const proposed_price = Number(document.getElementById("proposed_price").value);

    const response = await fetch("/api/advise", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title: game_title, proposed_price: proposed_price }),
    });

  const data = await response.json();
  document.getElementById("result").innerText = JSON.stringify(data, null, 2)
});
