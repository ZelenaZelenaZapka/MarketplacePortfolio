const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");

const showLoginBtn = document.getElementById("show-login");
const showRegisterBtn = document.getElementById("show-register");

const goRegisterBtn = document.getElementById("go-register");
const goLoginBtn = document.getElementById("go-login");

const switchIndicator = document.getElementById("switch-indicator");

const roleCards = document.querySelectorAll(".role-card");
const selectedRoleInput = document.getElementById("selected-role");

function showLogin() {
  loginForm.classList.add("active");
  registerForm.classList.remove("active");

  showLoginBtn.classList.add("active");
  showRegisterBtn.classList.remove("active");

  switchIndicator.classList.remove("to-register");
}

function showRegister() {
  registerForm.classList.add("active");
  loginForm.classList.remove("active");

  showRegisterBtn.classList.add("active");
  showLoginBtn.classList.remove("active");

  switchIndicator.classList.add("to-register");
}

showLoginBtn.addEventListener("click", showLogin);
showRegisterBtn.addEventListener("click", showRegister);
goRegisterBtn.addEventListener("click", showRegister);
goLoginBtn.addEventListener("click", showLogin);

roleCards.forEach((card) => {
  card.addEventListener("click", () => {
    roleCards.forEach((item) => item.classList.remove("active"));
    card.classList.add("active");
    selectedRoleInput.value = card.dataset.role;
  });
});