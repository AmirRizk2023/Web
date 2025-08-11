document.addEventListener("DOMContentLoaded", function () {
    // مثال: البحث عن موظف داخل الصفحة
    const searchInput = document.getElementById("search");
    if (searchInput) {
        searchInput.addEventListener("keyup", function () {
            let filter = searchInput.value.toLowerCase();
            let employees = document.querySelectorAll(".employee-item");

            employees.forEach(function (emp) {
                let text = emp.textContent.toLowerCase();
                emp.style.display = text.includes(filter) ? "" : "none";
            });
        });
    }
});
