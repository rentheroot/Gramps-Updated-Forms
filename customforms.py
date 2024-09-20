class TemplateOperations:

    def __init__(self):
        pass
    
    # Determine if string is actually an integer
    def check_int(self, s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()
    
    # Type aware concatenate
    def add(self, var_1, var_2):
        
        # Prioritize addition
        if self.check_int(str(var_1)) is True and self.check_int(str(var_2)) is True:
            result = var_1 + var_2

        # Otherwise Concatenate as strings
        else:
            result = str(var_1) + str(var_2)
        
        return result
    
    def subtract(self, var_1, var_2):
        result = var_1 - var_2
        return result
    
    def multiply(self, var_1, var_2):
        result = var_1 * var_2
        return result
    
    def divide(self, var_1, var_2):
        result = var_1 / var_2
        return result
    
    def equal(self, var_1, var_2):

        # equal
        if var_1 == var_2:
            result = True

        # not equal
        else:
            result = False

        return result

    def not_equal(self, var_1, var_2):

        # not equal
        if var_1 == var_2:
            result = False

        # equal
        else:
            result = True

        return result
    
    def less_than(self, var_1, var_2):

        # is less than
        if var_1 < var_2:
            result = True

        # is not less than
        else:
            result = False

        return result
    
    def greater_than(self, var_1, var_2):

        # is greater than
        if var_1 > var_2:
            result = True

        # is not greater than
        else:
            result = False

        return result
    
    def less_than_or_equal(self, var_1, var_2):

        # is less than or equal to
        if var_1 <= var_2:
            result = True

        # is not less than or equal to
        else:
            result = False

        return result
    
    def greater_than_or_equal(self, var_1, var_2):

        # is greater than or equal to
        if var_1 >= var_2:
            result = True

        # is not greater than or equal to
        else:
            result = False

        return result