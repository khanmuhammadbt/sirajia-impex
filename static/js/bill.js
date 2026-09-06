document.addEventListener('DOMContentLoaded', () => {
    const d = new Date();
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
    const year = d.getFullYear();

    const formattedDate = `${day}-${month}-${year}`;
    console.log(formattedDate); // "09-01-2026"
    document.getElementById("date").value = formattedDate;

    // Keyboard Navigation Logic
    document.addEventListener('keydown', function(e) {
        if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
            const active = document.activeElement;
            
            // Check if we are inside an input field
            if (active.tagName === 'INPUT' || active.tagName === 'SELECT') {
                const inputs = Array.from(document.querySelectorAll('input:not([readonly]), select'));
                const index = inputs.indexOf(active);

                if (e.key === "ArrowRight" && index < inputs.length - 1) {
                    inputs[index + 1].focus();
                    e.preventDefault(); // Default scrolling behavior ko rokne ke liye
                } else if (e.key === "ArrowLeft" && index > 0) {
                    inputs[index - 1].focus();
                    e.preventDefault();
                }
            }
        }

        // Bonus: Enter key se naya row add karne ke liye (Optional)
        if (e.key === "Enter" && e.target.classList.contains('rate')) {
            e.preventDefault();
            addRow();
            // Naye row ke pehle description box par focus karein
            setTimeout(() => {
                const allRows = document.querySelectorAll('.item-row');
                const lastRow = allRows[allRows.length - 1];
                lastRow.querySelector('input[name="description[]"]').focus();
            }, 50);
        }
    });
});

function addRow() {
    const container = document.getElementById("items-container");
    const row = document.createElement("tr");
    row.className = "item-row";

    row.innerHTML = `
        <td><input type="text" name="description[]" required></td>
        <td><input type="number" name="quantity[]" class="qty" oninput="calculate()" required></td>
        <td><input type="number" step="0.01" name="rate[]" class="rate" oninput="calculate()" required></td>
        <td><input type="text" class="amount" readonly></td>
        <td><button type="button" class="btn-delete" onclick="removeRow(this)">✕</button></td>
    `;
    container.appendChild(row);
}

function removeRow(btn) {
    btn.closest('tr').remove();
    calculate();
}

function calculate() {
    let grandTotal = 0;
    const rows = document.querySelectorAll('.item-row');

    rows.forEach(row => {
        const qty = parseFloat(row.querySelector('.qty').value) || 0;
        const rate = parseFloat(row.querySelector('.rate').value) || 0;
        const amount = qty * rate;
        
        row.querySelector('.amount').value = amount.toFixed(2);
        grandTotal += amount;
    });
    const sales_tax = parseFloat(document.getElementById("sales-tax-rate").value) || 0;
    const tax = grandTotal * (sales_tax / 100);
    const finalTotal = grandTotal + tax;

    document.getElementById("grand-total").value = grandTotal.toFixed(2);
    document.getElementById("sales-tax").value = tax.toFixed(2);
    document.getElementById("final-total").value = finalTotal.toFixed(2);
}