document.getElementById("registerForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData();
  formData.append("username", document.getElementById("username").value);
  formData.append("password", document.getElementById("password").value);

  try {
    const response = await fetch("/register", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (response.ok) {
      document.getElementById("registerMessage").innerText =
        "Registration successful! Redirecting to login...";
      setTimeout(() => {
        window.location.href = "/login";
      }, 1500);
    } else {
      document.getElementById("registerMessage").innerText =
        result.error || "Registration failed!";
    }
  } catch (err) {
    document.getElementById("registerMessage").innerText =
      "Server error. Try again.";
  }
});
