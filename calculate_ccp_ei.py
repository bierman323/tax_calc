def calculate_limited_tax(yearly, tax_rate, deduction, frequency):
    """
    Calculate the tax for CPP and EI (individually) and determine the how much is deducted per period

    Param: yearly: (float)
        Yearly Income
    Param: tax_rate: (float)
        The rate that the yearly income is taxed at
    Param: deduction: (float)
        How much of the yearly income is tax free
    Param: frequency: (int)
        How often the income is paid per year

    Return: period_pay: (float)
        The amount that is deducted from each pay
    """
    period_deduction = float("{:.2f}".format(deduction / frequency))
    period_pay = (yearly / frequency) - period_deduction
    period_payment = float("{:.2f}".format(period_pay * tax_rate))

    return period_payment

def calculate_number_of_pay_periods(period_payment, frequency,  max_tax):
    """
    Calculate the number of pay periods that it will take to pay off a tax burden

    Param: period_payment: (float)
        How much is being taken off per pay
    Param: frequency: (int)
        How many payments per year
    Param: max_tax: (float)
        What is the maximum payment per year

    Return: pay_periods: (int)
        The number of pay periods that it will take to pay off the tax burden
    Return: remainder: (float)
        The amount that still needs to be paid off of the tax burden after the pay_periods has expired
    """
    total_pay = period_payment * frequency
    if total_pay > max_tax:
        pay_periods = int(max_tax/period_payment)
        remainder = float("{:.2f}".format(max_tax - (pay_periods * period_payment)))
    else:
        pay_periods = frequency
        remainder = 0
    return pay_periods, remainder

def main():
    # Get inputs from command line
    # Calculate CPP
    # Calculate EI
    # Calculate Federal Tax
    # Calculate Provicial Tax
    # Calculate Deductions while CPP and EI removed
    # Calculate Deductions after CPP and EI
    # Calculate Hourly pay for deductions
    # Calculate Hourly pay based off number of hours
    # Calculate Weekly Pay
    # Calculate Bi Weekly Pay
    # Calcualte Bi Monthly Pay
    # Calcualte Monthly Pay
    print("\n")

if __name__ == "__main__":
    main()
