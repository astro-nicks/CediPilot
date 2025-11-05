const form = document.getElementById("loginForm");
const errorMsg = document.getElementById("errorMsg");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  try {
    const response = await fetch(`http://localhost:3000/users?email=${email}`);
    const data = await response.json();

    if (data.length > 0 && data[0].password === password) {
      // Store user session
      localStorage.setItem("user", JSON.stringify(data[0]));
      window.location.href = "dashboard.html";
    } else {
      errorMsg.style.display = "block";
    }
  } catch (error) {
    console.error("Login error:", error);
  }
});
