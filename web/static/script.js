const form = document.getElementById("advisor-form");

let isSubmitting = false;

form.addEventListener('submit', async function(event) {
  event.preventDefault();

  if (isSubmitting) {
    return;
  }

  isSubmitting = true;

  const button = document.querySelector("button[type='submit']");
  button.disabled = true;
  button.innerText = "Analyzing...";
  
  try {
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
    
  } finally {
    isSubmitting = false;
    button.disabled = false;
    button.innerText = "Analyze Discount";
  }
  
});
