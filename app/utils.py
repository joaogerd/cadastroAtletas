from datetime import datetime

# Decorator to manage routing logic based on argument types
def overloaded_function(func):
    """
    A decorator that routes the call to different functions based on the types and number of arguments.
    
    This decorator checks the arguments passed to the calculate_age_category function and decides
    whether to call calculate_adjusted_years, category, or getCat function.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """
    def wrapper(*args, **kwargs):
        try:

            # Logic for calculate_adjusted_years and category functions
            if len(args) == 1 and isinstance(args[0], str):
                return calculate_adjusted_years(*args, **kwargs)
            elif len(args) == 2 and all(isinstance(arg, int) for arg in args):
                return category(*args, **kwargs)
            else:
                raise ValueError
        except ValueError:
            # Construct a detailed error message
            arg_types = ', '.join([f'{type(arg)}' for arg in args])
            error_msg = (f"Invalid arguments for {func.__name__}: "
                         f"Arguments ({arg_types}) do not match expected types for "
                         f"any of the routed functions (calculate_adjusted_years, category, getCat).")
            raise ValueError(error_msg)
            
    return wrapper



@overloaded_function
def calculate_age_category(*args, **kwargs):
    """
    Generic function to calculate age or age category based on the input type.
    It uses the overloaded_function decorator to route the call to the appropriate function.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        int or str: The calculated age or age category.
    """
    pass

def age(born):
    """
    Calculate age based on the birthdate.

    Parameters:
        born (str): The birthdate in the format "%d/%m/%Y" (e.g., "01/01/2000").

    Returns:
        int: The calculated age.

    Example:
    >>> age("01/01/2000")
    23
    """
    born = datetime.strptime(born, "%d/%m/%Y").date()
    today = datetime.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
def category(year, v, even=None):
    """
    Calculate an age category based on the difference between 'year' and 'v'.

    This function can optionally round the age to the nearest even or odd number, depending on the 'even' parameter.
    If 'even' is None, it returns the age without adjustment. The function includes sanity checks to ensure
    that 'year' and 'v' are integers and that 'year' is not less than 'v'.

    Parameters:
        year (int): The current year.
        v (int): The birth year or a reference year for age calculation.
        even (bool, optional): Adjusts the result to an even number if True, to an odd number if False,
                               and no adjustment if None.

    Returns:
        int: The calculated age category.

    Raises:
        ValueError: If 'year' or 'v' are not integers or if 'year' is less than 'v'.
    """
    # Sanity checks
    if not isinstance(year, int) or not isinstance(v, int):
        raise ValueError("Both 'year' and 'v' must be integers")
    if year < v:
        raise ValueError("'year' must be greater than or equal to 'v'")

    idade = year - v

    # Handling the edge case where the difference is 0
    if idade == 0:
        return 0 if even is None else 1

    # Correcting the adjustment logic
    if even is None:
        return idade
    if even:
        return idade + (idade % 2 != 0)  # Adjust to even
    else:
        return idade + (idade % 2 == 0)  # Adjust to odd

def overloaded_function(func):
    """
    A decorator that routes the call to different functions based on the types and number of arguments.
    
    This decorator checks the arguments passed to the calculate_age_category function and decides
    whether to call calculate_adjusted_years, category, or getCat function.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """
    def wrapper(*args, **kwargs):
        try:
            # Specific logic for getCat function
            if len(args) in [1, 2] and isinstance(args[0], int):
                # Check if 'even' is explicitly passed in kwargs
                if 'even' not in kwargs:
                    # Default 'even' to True if not provided
                    kwargs['even'] = True if len(args) == 1 else args[1]
                return getCat(*args, **kwargs)

            # Logic for calculate_adjusted_years and category functions
            if len(args) == 1 and isinstance(args[0], str):
                return calculate_adjusted_years(*args, **kwargs)
            elif len(args) == 2 and all(isinstance(arg, int) for arg in args):
                return category(*args, **kwargs)
            else:
                raise ValueError
        except ValueError:
            # Construct a detailed error message
            arg_types = ', '.join([f'{type(arg)}' for arg in args])
            error_msg = (f"Invalid arguments for {func.__name__}: "
                         f"Arguments ({arg_types}) do not match expected types for "
                         f"any of the routed functions (calculate_adjusted_years, category, getCat).")
            raise ValueError(error_msg)
            
    return wrapper



def getCat(dtNascimento, even=True):
    """
    Determine the age category based on the birth year using calculate_age_category.

    Parameters:
        dtNascimento (int): The birth year (e.g., 2000).
        even (bool, optional): If True, adjusts the result to be an even number.
                               If False, adjusts the result to be an odd number.

    Returns:
        str: The calculated age category.
    """
    # Using calculate_age_category to calculate the adjusted age
    idade = calculate_age_category(datetime.now().year, dtNascimento, even=even)

    # Determine the category based on age
    if idade <= 10:
        categoria = 'initiation'
    else:
        categoria = f'sub-{idade}'

    return categoria

