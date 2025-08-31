document.addEventListener("DOMContentLoaded", () => {
  const originalInput = document.getElementById("original");
  const testInput = document.getElementById("test");
  const previewOriginal = document.getElementById("preview-original");
  const previewTest = document.getElementById("preview-test");
  const verifyBtn = document.getElementById("verifyBtn");
  const spinner = document.getElementById("spinner");
  const resultContainer = document.querySelector(".result");
  const resultText = document.getElementById("resultText");
  const progress = document.getElementById("progress");
  const confidenceText = document.getElementById("confidenceText");
  const logoutBtn = document.getElementById("logoutBtn");

  function previewFile(input, previewEl) {
    const file = input?.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewEl.src = e.target.result;
        previewEl.classList.remove("hidden");
      };
      reader.readAsDataURL(file);
    }
  }

  if (originalInput) originalInput.addEventListener("change", () => previewFile(originalInput, previewOriginal));
  if (testInput) testInput.addEventListener("change", () => previewFile(testInput, previewTest));

  if (verifyBtn) {
    verifyBtn.addEventListener("click", async () => {
      const originalFile = originalInput.files[0];
      const testFile = testInput.files[0];

      if (!originalFile || !testFile) {
        alert("Please upload both signatures.");
        return;
      }

      const formData = new FormData();
      formData.append("original", originalFile);
      formData.append("test", testFile);

      spinner.classList.remove("hidden"); // Show spinner
      resultContainer.classList.add("hidden");

      try {
        const res = await fetch("/verify", { method: "POST", body: formData });
        const data = await res.json();

        spinner.classList.add("hidden"); // Hide spinner after response
        resultContainer.classList.remove("hidden");

        if (res.ok) {
          const confidence = data.confidence.toFixed(2);
          const isMatch = data.match;

          resultText.textContent = isMatch ? `✅ Signatures Match` : `❌ Signatures Do Not Match`;
          progress.style.width = `${confidence}%`;
          progress.classList.remove("bg-green-500", "bg-red-500");
          progress.classList.add(isMatch ? "bg-green-500" : "bg-red-500");

          confidenceText.textContent = `Confidence: ${confidence}% (Processed in ${data.time.toFixed(2)}s)`;
        } else {
          alert(data.error || "Verification failed.");
        }
      } catch (err) {
        spinner.classList.add("hidden");
        alert("An error occurred while verifying signatures.");
        console.error(err);
      }
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      await fetch("/logout", { method: "POST" });
      window.location.href = "/login";
    });
  }
});
