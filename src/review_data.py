TASK = {
    "scenario": "A developer is reviewing a small Python function that calculates a discount.",
    "instruction": "Inspect the code and decide whether each AI review finding is valid, useful and supported by evidence.",
    "code": "def apply_discount(price, discount):\n    if discount > 0:\n        return price - price * discount\n    return price\n"
}

FINDINGS = [
    {
        "id": "F-001", "title": "Discount values are not range-checked",
        "severity": "High", "summary": "Discounts greater than 1 or less than 0 are not rejected.",
        "explanation": "A discount greater than 1 can produce a negative price. A negative discount increases the price.",
        "evidence": "The condition checks only whether discount > 0. It does not enforce an upper bound.",
        "suggestion": "Validate that discount is within the expected range, such as 0.0 to 1.0."
    },
    {
        "id": "F-002", "title": "Negative prices are not handled explicitly",
        "severity": "Medium", "summary": "The function does not define how negative prices should be handled.",
        "explanation": "If negative prices are invalid in the domain, the function currently accepts them. This depends on the input contract.",
        "evidence": "There is no validation of price before the calculation.",
        "suggestion": "Confirm the domain contract and validate price if negative values are not permitted."
    },
    {
        "id": "F-003", "title": "Parameter types are undocumented",
        "severity": "Low", "summary": "The function has no type annotations.",
        "explanation": "Type annotations can clarify expected inputs and return values for readers and static analysis tools.",
        "evidence": "The function signature does not annotate its parameters or return value.",
        "suggestion": "Add suitable numeric annotations in line with project conventions."
    }
]
