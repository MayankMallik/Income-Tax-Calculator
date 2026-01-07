// Format numbers with Indian commas (from your original HTML)
function formatNumber(input) {
    let value = input.value.replace(/,/g, '');
    value = value.replace(/[^0-9]/g, '');
    
    if (value.length > 3) {
        let lastThree = value.slice(-3);
        let otherNumbers = value.slice(0, -3);
        
        if (otherNumbers) {
            otherNumbers = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",");
        }
        
        value = otherNumbers + "," + lastThree;
    }
    
    input.value = value;
}

// Add input formatting to all text inputs
document.querySelectorAll('input[type="text"]').forEach(input => {
    input.addEventListener('input', function() {
        formatNumber(this);
    });
});

// Tax calculation functions (converted from your Python)
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
    
    return tax * 1.04; // Add 4% cess
}

function calculateTax(grossSalaryCalc, pensionCalc, homeloanIntCalc, sec80cCalc, npsCalc) {
    let salary = grossSalaryCalc + pensionCalc;
    let deductions = homeloanIntCalc + sec80cCalc + npsCalc;

    // Old Regime
    let taxableIncomeOld = Math.max(salary - deductions - 50000, 0);
    let oldTax = computeTax(taxableIncomeOld, 500001, [
        [250000, 0.00], [250000, 0.05], [500000, 0.20], [null, 0.30]
    ]);

    // New Regime
    let taxableIncomeNew = Math.max(salary - 75000, 0);
    let newTax = computeTax(taxableIncomeNew, 700001, [
        [300000, 0.00], [400000, 0.05], [300000, 0.10], 
        [200000, 0.15], [300000, 0.20], [null, 0.30]
    ]);

    // Proposed Regime
    let taxableIncomeProposed = Math.max(salary - 75000, 0);
    let proposedTaxNormal = computeTax(taxableIncomeProposed, 1200001, [
        [400000, 0.00], [400000, 0.05], [400000, 0.10],
        [400000, 0.15], [400000, 0.20], [400000, 0.25], [null, 0.30]
    ]);
    
    let proposedTax = (salary > 1275000) 
        ? Math.min(salary - 1275000, proposedTaxNormal) 
        : proposedTaxNormal;

    return { oldTax, newTax, proposedTax };
}

// Handle form submission
document.getElementById('taxForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get values and convert to numbers
    const getNumber = id => {
        const value = document.getElementById(id).value.replace(/,/g, '');
        return value ? parseFloat(value) : 0;
    };

    const results = calculateTax(
        getNumber('gross_salary'),
        getNumber('pension'),
        getNumber('homeloan_int'),
        getNumber('sec_80c'),
        getNumber('nps')
    );

    // Format results with Indian number format
    const formatIndian = num => {
        num = num.toFixed(2); // Keep 2 decimal places
        let [integer, decimal] = num.split('.');
        
        if (integer.length > 3) {
            let lastThree = integer.slice(-3);
            let otherNumbers = integer.slice(0, -3);
            if (otherNumbers) {
                otherNumbers = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",");
            }
            integer = otherNumbers ? otherNumbers + "," + lastThree : lastThree;
        }
        
        return integer + (decimal ? `.${decimal}` : '');
    };

    // Display results
    document.getElementById('old_tax_result').textContent = '₹' + formatIndian(results.oldTax);
    document.getElementById('new_tax_result').textContent = '₹' + formatIndian(results.newTax);
    document.getElementById('proposed_tax_result').textContent = '₹' + formatIndian(results.proposedTax);
    document.getElementById('results').style.display = 'block';
});