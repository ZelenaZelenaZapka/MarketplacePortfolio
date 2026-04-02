const chips = document.querySelectorAll(".chip");
const addToCartButtons = document.querySelectorAll(".add-to-cart");

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    chip.classList.toggle("active");
  });
});

addToCartButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const originalText = button.textContent;

    button.textContent = "Додано";
    button.disabled = true;

    setTimeout(() => {
      button.textContent = originalText;
      button.disabled = false;
    }, 900);
  });
});