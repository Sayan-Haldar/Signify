document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData();
  formData.append("username", document.getElementById("username").value);
  formData.append("password", document.getElementById("password").value);
  formData.append("role", document.getElementById("role").value);

  try {
    const response = await fetch("/login", {
      method: "POST",
      body: formData,
    });

    if (response.redirected) {
      window.location.href = response.url;
    } else {
      const result = await response.json();
      document.getElementById("loginMessage").innerText =
        result.error || "Login failed!";
    }
  } catch (err) {
    document.getElementById("loginMessage").innerText =
      "Server error. Try again.";
  }
});
