import argparse, json
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class Taxes:
    income: float = 50000
    hourly_pay: float = 25
    weekly_hours: float = 40
    pay_periods: int = 26
    tax_year: int = datetime.now().year
    weeks_worked: int = 52
    cpp: dict = field(default_factory=dict)
    ei: dict = field(default_factory=dict)
    deductions: dict = field(default_factory=dict)
    bracket: dict = field(default_factory=dict)

def get_args(data):
    parser = argparse.ArgumentParser(description="pay")
    parser.add_argument('-i', dest='income',help='Annual Income, default is 50K', type=float)
    parser.add_argument('-p', dest='pay', help='hourly rate of pay. default is $25', type=float)
    parser.add_argument('-m', dest='hours', help='average hours per week. default is 40', type=float)
    parser.add_argument('-n', dest='periods', help='number of pay periods. default is 26', type=int)
    parser.add_argument('-y', dest='year', help='tax year. default is current year', type=int)
    parser.add_argument('-w', dest='weeks', help='number or weeks in a year. Default is 52')

    args = parser.parse_args()

    if not args.income and not args.pay:
        parser.print_help()
        exit(0)

    if args.pay:
        data.hourly_pay = args.pay
        data.income = 0
    if args.hours:
        data.weekly_hours = args.hours
    if args.income:
        data.income = args.income
    if args.periods:
        data.pay_periods = args.periods
    if args.year:
        data.tax_year = args.year
    if args.weeks:
        data.weeks_worked = args.weeks 
    
    # Calculate income
    if data.income == 0:
        data.income = data.hourly_pay * data.weekly_hours * data.weeks_worked

def calculate_cpp(gross_income, cpp_values):
    # Gross Income * Cpp Percent
    # least amount of calculation or cpp max
    taxable = gross_income - cpp_values["cpp_untaxed"]
    if taxable > 0:
        cpp2 = 0
        secondary_rate = cpp_values.get("secondary_rate", 0)
        calculated_cpp = round((gross_income-cpp_values["cpp_untaxed"]) * cpp_values["cpp_rate"], 2)
        if calculated_cpp > cpp_values["cpp_max"]:
            calculated_cpp = cpp_values["cpp_max"]
            if "secondary_rate" in cpp_values:
                more_to_tax = gross_income - cpp_values["cpp_untaxed"]-cpp_values["maximum_pensionable_cpp1"]
                cpp2 = more_to_tax * secondary_rate
                if cpp2 > cpp_values["secondary_max"]:
                    cpp2 = cpp_values["secondary_max"]
                calculated_cpp = calculated_cpp + cpp2
    else:
        calculated_cpp = 0
        cpp2 = 0
        secondary_rate =0
    return calculated_cpp, cpp2, cpp_values["cpp_rate"], secondary_rate

def calculate_ei(gross_income, ei_percent, ei_max, ei_untaxed):
    # Gross Income * Cpp Percent
    # least amount of calculation or cpp max
    calculated_ei = round((gross_income-ei_untaxed) * ei_percent, 2)
    if calculated_ei > ei_max:
        return ei_max
    elif calculated_ei <= 0:
        return 0
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
    
    if total_tax < 0:
      total_tax = 0
    
    return round(total_tax, 2)


def read_in_tax_table():
    # Read in the tax json file. it should be in the same location as this file
    with open("tax_rates.json", 'r') as f:
        tax_rates = json.load(f)
    return tax_rates
        
def main():
    # Setup a the data class
    data = Taxes()
    get_args(data)
    # Get the tax tables
    tax_table = read_in_tax_table()
    
    print(f'\n\nFor the year {data.tax_year} on ${data.income} you will pay the following: \n')
    # Calculate CPP
    cpp_contribution, cpp2, cpp_rate, ccp_rate2 =calculate_cpp(data.income, 
                                   tax_table["cpp"][str(data.tax_year)])
    cpp1 = round(cpp_contribution - cpp2, 2)
    print(f'CPP1:${cpp1}  CPP2:${cpp2}  Total CPP:${cpp_contribution}')

    # Calculate EI
    ei_contribution=calculate_ei(data.income,
                                 tax_table["ei"][str(data.tax_year)]["ei_rate"],
                                 tax_table["ei"][str(data.tax_year)]["ei_max"],
                                 tax_table["ei"][str(data.tax_year)]["ei_untaxed"])
    print(f'EI contributions: ${ei_contribution}')
    # Calculate Personal Tax Deduction
    personal_amount = calculate_personal_deduction(data.income,
                                                   tax_table["income"][str(data.tax_year)]["personal deduction"]["threshold"],
                                                   tax_table["income"][str(data.tax_year)]["personal deduction"]["divisor"],
                                                   tax_table["income"][str(data.tax_year)]["personal deduction"]["supplemental"],
                                                   tax_table["income"][str(data.tax_year)]["personal deduction"]["minimum"],
                                                   tax_table["income"][str(data.tax_year)]["personal deduction"]["maximum"])
    print(f'Personal deduction: ${personal_amount}')
    # Calculate Tax
    tax_deducted_annually = calculate_annual_tax(data.income,
                                                 tax_table["income"][str(data.tax_year)],
                                                 personal_amount)
    print(f'Total tax deducted: ${tax_deducted_annually}')

    take_home_pay = round(data.income - cpp_contribution - ei_contribution - tax_deducted_annually, 2)
    print(f'Your take home pay will be: ${take_home_pay}')
    monthly_pay = round(take_home_pay / 12, 2)
    print(f'Your monthly pay will be: ${monthly_pay}')
    # Calculate Deductions while CPP and EI removed
    # Calculate Deductions after CPP and EI
    # Calculate Hourly pay for deductions
    # Calculate Hourly pay based off number of hours
    hourly_wage = round(data.income / (data.weekly_hours * data.weeks_worked), 2)
    print(f"Your hourly wage is: {hourly_wage}")
    # Calculate Weekly Pay
    weekly_pay = round(take_home_pay / data.weeks_worked)
    print(f"Your take home pay per week average is: {weekly_pay}")
    # Calculate Bi Weekly Pay
    bi_weekly_pay = weekly_pay *2
    print(f"Bi-Weekly take home pay: {bi_weekly_pay}")
    # Calculate Bi Monthly Pay

if __name__ == "__main__":
    main()
