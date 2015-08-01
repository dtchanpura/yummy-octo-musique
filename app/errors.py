class FlowException(Exception):
    def __init__(self, message):
        super(FlowException, self).__init__(message)
        self.message = message
