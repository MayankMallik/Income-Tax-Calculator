from flask import Flask, render_template, request

app = Flask(__name__)

# Custom Jinja filter to format numbers with Indian commas
@app.template_filter('format_indian_number')
def format_indian_number(value):
    value = float(value)
    value = "{:.2f}".format(value)
    parts = value.split(".")
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else ""
    
    # Remove any existing commas
    number_str = str(integer_part).replace(",", "")
    
    # Handle numbers less than 1000
    if len(number_str) <= 3:
        return f"{number_str}.{decimal_part}" if decimal_part else number_str
    
    # Extract last 3 digits
    last_three = number_str[-3:]
    # Get remaining digits
    remaining = number_str[:-3]
    
    # Insert commas every 2 digits in the remaining part
    formatted_remaining = ""
    for i in range(len(remaining)-1, -1, -2):
        if i == 0:
            formatted_remaining = remaining[0] + "," + formatted_remaining
        else:
            formatted_remaining = remaining[max(i-1, 0):i+1] + "," + formatted_remaining
    
    # Remove trailing comma if present
    formatted_remaining = formatted_remaining.rstrip(",")
    
    # Combine parts
    result = formatted_remaining + "," + last_three
    return f"{result}.{decimal_part}" if decimal_part else result

def compute_tax(taxable_income, threshold, slabs):
    """
    Calculate tax if the taxable income exceeds a minimum threshold.
    
    Parameters:
      taxable_income (float): Income after standard deduction and other adjustments.
      threshold (float): Minimum taxable income required for any tax liability.
      slabs (list of tuples): Each tuple is (amount, rate). If amount is None, 
                              the slab is unbounded.
    
    Returns:
      float: The computed tax including a 4% cess, or 0 if taxable_income is below threshold.
    """
    # If taxable income is below the minimum threshold, no tax is levied.
    if taxable_income < threshold:
        return 0
    
    tax = 0
    remaining = taxable_income
    for slab_amount, rate in slabs:
        if slab_amount is None:
            # All remaining income falls into this slab.
            tax += remaining * rate
            remaining = 0
            break
        else:
            # Use the lesser of remaining income or the slab cap.
            amount_in_slab = min(remaining, slab_amount)
            tax += amount_in_slab * rate
            remaining -= amount_in_slab
            if remaining <= 0:
                break
    
    # Add a 4% cess to the computed tax.
    return tax * 1.04

def calculate_tax(gross_salary_calc, pension_calc, homeloan_int_calc, sec_80c_calc, nps_calc):
    """
    Calculate tax under three regimes:
      - Old Regime
      - New Regime
      - Proposed Regime
      
    The salary for all regimes is calculated as the sum of the gross salary and pension.
    The old regime considers additional deductions.
    """
    # Calculate total salary and deductions (only applicable in old regime)
    salary = gross_salary_calc + pension_calc
    deductions = homeloan_int_calc + sec_80c_calc + nps_calc

    # ----------------- Old Regime -----------------
    # Standard deduction: 50,000 and deductions available.
    taxable_income_old = max(salary - deductions - 50000, 0)
    # Tax is only applied if taxable income is at least 5,00,000.
    old_threshold = 500001
    old_slabs = [
        (250000, 0.00),   # First 2,50,000: 0%
        (250000, 0.05),   # Next 2,50,000: 5%
        (500000, 0.20),   # Next 5,00,000: 20%
        (None,   0.30)    # Remaining income: 30%
    ]
    old_tax = compute_tax(taxable_income_old, old_threshold, old_slabs)

    # ----------------- New Regime -----------------
    # Standard deduction: 75,000, no other deductions.
    taxable_income_new = max(salary - 75000, 0)
    # Tax is only applied if taxable income is at least 7,00,000.
    new_threshold = 700001
    new_slabs = [
        (300000, 0.00),   # Up to 3,00,000: 0%
        (400000, 0.05),   # Next 4,00,000: 5%
        (300000, 0.10),   # Next 3,00,000: 10%
        (200000, 0.15),   # Next 2,00,000: 15%
        (300000, 0.20),   # Next 3,00,000: 20%
        (None,   0.30)    # Remaining income: 30%
    ]
    new_tax = compute_tax(taxable_income_new, new_threshold, new_slabs)

    # --------------- Proposed Regime ---------------
    # Standard deduction remains 75,000.
    taxable_income_proposed = max(salary - 75000, 0)
    # Tax is only applied if taxable income is at least 12,00,000.
    proposed_threshold = 1200001
    proposed_slabs = [
        (400000, 0.00),   # Up to 4,00,000: 0%
        (400000, 0.05),   # Next 4,00,000: 5%
        (400000, 0.10),   # Next 4,00,000: 10%
        (400000, 0.15),   # Next 4,00,000: 15%
        (400000, 0.20),   # Next 4,00,000: 20%
        (400000, 0.25),   # Next 4,00,000: 25%
        (None,   0.30)    # Remaining income: 30%
    ]
    proposed_tax_normal = compute_tax(taxable_income_proposed, proposed_threshold, proposed_slabs)
    
    # Apply marginal tax logic if salary > 12,75,000
    marginal_threshold = 1275000
    if salary > marginal_threshold:
        marginal_tax = salary - marginal_threshold
        proposed_tax = min(marginal_tax, proposed_tax_normal)  # Take the lesser of marginal or normal tax
    else:
        proposed_tax = proposed_tax_normal

    return old_tax, new_tax, proposed_tax

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get values and keep the commas for display
        gross_salary = request.form['gross_salary']
        pension = request.form.get('pension', '0')
        homeloan_int = request.form.get('homeloan_int', '0')
        sec_80c = request.form.get('sec_80c', '0')
        nps = request.form.get('nps', '0')
        
        # Remove commas for calculation and convert to float
        gross_salary_calc = float(gross_salary.replace(',', ''))
        pension_calc = float(pension.replace(',', '') or 0)
        homeloan_int_calc = float(homeloan_int.replace(',', '') or 0)
        sec_80c_calc = float(sec_80c.replace(',', '') or 0)
        nps_calc = float(nps.replace(',', '') or 0)
        
        # Calculate taxes using the cleaned numeric values
        old_tax, new_tax, proposed_tax = calculate_tax(
            gross_salary_calc, pension_calc, homeloan_int_calc, sec_80c_calc, nps_calc)
        
        # Pass both calculated tax values and the original formatted input values to the template
        return render_template('index.html', 
                               old_tax=old_tax, 
                               new_tax=new_tax, 
                               proposed_tax=proposed_tax,
                               gross_salary=gross_salary,
                               pension=pension,
                               homeloan_int=homeloan_int,
                               sec_80c=sec_80c,
                               nps=nps)
    
    # For GET requests, initialize variables to default empty values.
    return render_template('index.html', 
                           old_tax=None, 
                           new_tax=None, 
                           proposed_tax=None,
                           gross_salary='',
                           pension='',
                           homeloan_int='',
                           sec_80c='',
                           nps='')

if __name__ == '__main__':
    app.run(debug=True)
