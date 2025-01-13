import argparse, json

def get_args():
    parser = argparse.ArgumentParser(description="pay")
    parser.add_argument('-i', dest='income',help='Annual Income', type=float, default=58000.00)
    parser.add_argument('-p', dest='pay', help='hourly rate of pay', type=float, default=27.00)
    parser.add_argument('-m', dest='hours', help='average hours per week', type=float, default=40)
    parser.add_argument('-n', dest='periods', help='number of pay periods', type=int, default=26)
    parser.add_argument('-y', dest='year', help='tax year', type=int, default=2023)

    return parser.parse_args()

def calculate_cpp(gross_income, cpp_values):
    # Gross Income * Cpp Percent
    # least amount of calculation or cpp max
    calculated_cpp = round((gross_income-cpp_values["cpp_untaxed"]) * cpp_values["cpp_rate"], 2)
    if calculated_cpp > cpp_values["cpp_max"]:
        calculated_cpp = cpp_values["cpp_max"]
        if "secondary_rate" in cpp_values:
            more_to_tax = gross_income - cpp_values["cpp_untaxed"]-cpp_values["maximum_pensionable_cpp1"]
            cpp2 = more_to_tax * cpp_values["secondary_rate"]
            if cpp2 > cpp_values["secondary_max"]:
                cpp2 = cpp_values["secondary_max"]
            calculated_cpp = calculated_cpp + cpp2
    return calculated_cpp

def calculate_ei(gross_income, ei_percent, ei_max, ei_untaxed):
    # Gross Income * Cpp Percent
    # least amount of calculation or cpp max
    calculated_ei = round((gross_income-ei_untaxed) * ei_percent, 2)
    if calculated_ei > ei_max:
        return ei_max
    else:
        return calculated_ei

def calculate_personal_deduction(gross_income, threshold, divisor, supplemental, min_amount, max_amount):
    # gross income - threshold = x / divisor = x * multiplier
    # supplemental amount (max - min) - x
    # zero or less returns minimum personal amount
    # maximum is the maximum amount
    calculated_amount = ((gross_income - threshold)/divisor)*supplemental
    extra = supplemental - calculated_amount
    if extra > 0:
        total_amount = extra + min_amount
        if total_amount > max_amount:
            return max_amount
        else:
            return round(total_amount, 2)
    else:
        return min_amount

def calculate_bracket_tax(taxable_income, tax_dict):
    if taxable_income > tax_dict["upper"]:
        bracket_income = tax_dict["upper"] - tax_dict["lower"]
    else:
        bracket_income = taxable_income - tax_dict["lower"]
    return round(bracket_income * tax_dict["tax_on_income"], 2)
    
def calculate_annual_tax(gross_income, tax_values, personal_deduction):
    less_personal_amount= round(personal_deduction * tax_values["bracket1"]["income"]["tax_on_income"], 2)
    total_tax = 0 - less_personal_amount
    for bracket in tax_values:
        if "bracket" in bracket:
            if tax_values[bracket]["income"]["lower"] < gross_income:
                total_tax += calculate_bracket_tax(gross_income,
                                                    tax_values[bracket]["income"])
    
    return round(total_tax, 2)


def read_in_tax_table():
    # Read in the tax json file. it should be in the same location as this file
    with open("tax_rates.json", 'r') as f:
        tax_rates = json.load(f)
    return tax_rates
        
def main():
    # Get inputs from command line
        # inputs that are needed:
        #   Annual Income (optional)
        #   Hourly pay (optional)
        #   Average hours worked per week
        #   Number of pay periods
        #   Year
    args = get_args()
    # Get the tax tables
    tax_table = read_in_tax_table()
    print(f'For the year {args.year} on ${args.income} you will pay the following')
    # Calculate CPP
    cpp_contribution=calculate_cpp(args.income, 
                                   tax_table["cpp"][str(args.year)])
    print(f'CPP deduction: ${cpp_contribution}')

    # Calculate EI
    ei_contribution=calculate_ei(args.income,
                                 tax_table["ei"][str(args.year)]["ei_rate"],
                                 tax_table["ei"][str(args.year)]["ei_max"],
                                 tax_table["ei"][str(args.year)]["ei_untaxed"])
    print(f'EI contributions: ${ei_contribution}')
    # Calculate Personal Tax Deduction
    personal_amount = calculate_personal_deduction(args.income,
                                                   tax_table["income"][str(args.year)]["personal deduction"]["threshold"],
                                                   tax_table["income"][str(args.year)]["personal deduction"]["divisor"],
                                                   tax_table["income"][str(args.year)]["personal deduction"]["supplemental"],
                                                   tax_table["income"][str(args.year)]["personal deduction"]["minimum"],
                                                   tax_table["income"][str(args.year)]["personal deduction"]["maximum"])
    print(f'Personal deduction: ${personal_amount}')
    # Calculate Tax
    tax_deducted_annually = calculate_annual_tax(args.income,
                                                 tax_table["income"][str(args.year)],
                                                 personal_amount)
    print(f'Total tax deducted: ${tax_deducted_annually}')

    take_home_pay = round(args.income - cpp_contribution - ei_contribution - tax_deducted_annually, 2)
    print(f'Your take home pay will be: ${take_home_pay}')
    monthly_pay = round(take_home_pay / 12, 2)
    print(f'Your monthly pay will be: ${monthly_pay}')
    # Calculate Deductions while CPP and EI removed
    # Calculate Deductions after CPP and EI
    # Calculate Hourly pay for deductions
    # Calculate Hourly pay based off number of hours
    # Calculate Weekly Pay
    # Calculate Bi Weekly Pay
    # Calculate Bi Monthly Pay
    # Calculate Monthly Pay

if __name__ == "__main__":
    main()
