function formatNumber(input) {
    let value = input.value.replace(/,/g, '');
    value = value.replace(/[^0-9]/g, ''); 
    if (value.length > 3) {
        let lastThree = value.slice(-3);
        let otherNumbers = value.slice(0, -3);
        if (otherNumbers) {
            otherNumbers = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",");
            value = otherNumbers + "," + lastThree;
        }
    }
    input.value = value;
}

document.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', function() { 
        formatNumber(this); 
        this.classList.remove('error');
    });
});

function computeTax(taxableIncome, threshold, slabs) {
    if (taxableIncome < threshold) return 0;
    let tax = 0;
    let remaining = taxableIncome;
    for (let [slabAmount, rate] of slabs) {
        if (slabAmount === null) {
            tax += remaining * rate;
            break;
        } else {
            let amountInSlab = Math.min(remaining, slabAmount);
            tax += amountInSlab * rate;
            remaining -= amountInSlab;
            if (remaining <= 0) break;
        }
    }
    return tax * 1.04;
}

function handleCalculate() {
    const getVal = id => parseFloat(document.getElementById(id).value.replace(/,/g, '')) || 0;
    const grossInput = document.getElementById('gross_salary');

    if (grossInput.value.trim() === "") {
        grossInput.classList.add('error');
        return;
    }

    const totalIncome = getVal('gross_salary') + getVal('pension');
    const deductions = getVal('homeloan_int') + getVal('sec_80c') + getVal('nps');

    // Tax Logic[cite: 6]
    let taxableOld = Math.max(totalIncome - deductions - 50000, 0);
    let oldTax = computeTax(taxableOld, 500001, [[250000, 0], [250000, 0.05], [500000, 0.20], [null, 0.30]]);

    let taxableNew = Math.max(totalIncome - 75000, 0);
    let newTaxNormal = computeTax(taxableNew, 1200001, [[400000, 0], [400000, 0.05], [400000, 0.10], [400000, 0.15], [400000, 0.20], [400000, 0.25], [null, 0.30]]);
    let newTax = (totalIncome > 1275000) ? Math.min(totalIncome - 1275000, newTaxNormal) : newTaxNormal;

    // Standard Indian Comma Formatting[cite: 6]
    const formatIndian = num => {
        let integer = Math.ceil(num).toString();
        if (integer.length > 3) {
            let lastThree = integer.slice(-3);
            let otherNumbers = integer.slice(0, -3);
            otherNumbers = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",");
            return "₹" + otherNumbers + "," + lastThree;
        }
        return "₹" + integer;
    };

    document.getElementById('old_tax_result').innerText = formatIndian(oldTax);
    document.getElementById('new_tax_result').innerText = formatIndian(newTax);
    document.getElementById('results').style.display = 'block';
}