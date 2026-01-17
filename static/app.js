function toggleForm(id) {
  const forms = document.querySelectorAll(".forms .card");
  const current = document.getElementById(id);

  forms.forEach((form) => {
    if (form !== current) {
      form.classList.remove("show");
      form.classList.add("hidden");
    }
  });

  if (current.classList.contains("show")) {
    current.classList.remove("show");
    current.classList.add("hidden");
  } else {
    current.classList.remove("hidden");
    current.classList.add("show");
  }
}

/* ------------------
   Click outside to close
------------------ */
document.addEventListener("click", function (e) {
  const forms = document.querySelectorAll(".forms .card");
  const buttons = document.querySelectorAll(".actions button");

  let clickedButton = [...buttons].some((btn) => btn.contains(e.target));
  let clickedForm = [...forms].some((form) => form.contains(e.target));

  if (!clickedButton && !clickedForm) {
    forms.forEach((form) => {
      form.classList.remove("show");
      form.classList.add("hidden");
    });
  }
});
function openModal(id) {
  document.getElementById(id).classList.remove("hidden");
}

function closeModal(id) {
  document.getElementById(id).classList.add("hidden");
}