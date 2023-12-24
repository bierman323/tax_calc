import argparse, json

def get_args():
    parser = argparse.ArgumentParser(description="pay")
    parser.add_argument('-i', dest='income',help='Annual Income', type=float)
    parser.add_argument('-p', dest='pay', help='hourly rate of pay', type=float)
    parser.add_argument('-m', dest='hours', help='average hours per week', type=float)
    parser.add_argument('-n', dest='periods', help='number of pay periods', type=int)
    parser.add_argument('-y', dest='year', help='tax year', type=int)

    return parser.parse_args()

def calculate_cpp(gross_income, cpp_percent, cpp_max, cpp_untaxed):
    # Gross Income * Cpp Percent
    # least amount of calculation or cpp max
    calculated_cpp = round((gross_income-cpp_untaxed) * cpp_percent, 2)
    if calculated_cpp > cpp_max:
        return cpp_max
    else:
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
    # Calculate CPP
    cpp_contribution=calculate_cpp(args.income, 
                                   tax_table["cpp"][str(args.year)]["cpp_rate"],
                                   tax_table["cpp"][str(args.year)]["cpp_max"],
                                   tax_table["cpp"][str(args.year)]["cpp_untaxed"])

    # Calculate EI
    ei_contribution=calculate_ei(args.income,
                                 tax_table["ei"][str(args.year)]["ei_rate"],
                                 tax_table["ei"][str(args.year)]["ei_max"],
                                 tax_table["ei"][str(args.year)]["ei_untaxed"])
    # Calculate Personal Tax Deduction
    personal_amount = calculate_personal_deduction(args.income,
                                                   tax_table["income"][str(args.year)]["personal deduction"]["threshold"],
                                                   tax_table["income"][str(args.year)]["personal deduction"]["divisor"],
                                                   tax_table["income"][str(args.year)]["personal deduction"]["supplemental"],
                                                   tax_table["income"][str(args.year)]["personal deduction"]["minimum"],
                                                   tax_table["income"][str(args.year)]["personal deduction"]["maximum"])
    print(f'The personal deduction is: ${personal_amount}')
    # Calculate Tax
    # Calculate Deductions while CPP and EI removed
    # Calculate Deductions after CPP and EI
    # Calculate Hourly pay for deductions
    # Calculate Hourly pay based off number of hours
    # Calculate Weekly Pay
    # Calculate Bi Weekly Pay
    # Calcualte Bi Monthly Pay
    # Calcualte Monthly Pay

if __name__ == "__main__":
    main()
