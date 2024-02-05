import heapq

class NumberPool:
    _instance = None

    def __new__(cls, max_value=None):
        if cls._instance is None and max_value is not None:
            cls._instance = super(NumberPool, cls).__new__(cls)
            cls._instance.__init_once(max_value)
        elif cls._instance is None and max_value is None:
            raise ValueError("An initial max_value must be provided")
        return cls._instance

    def __init_once(self, max_value):
        self.max_value = max_value
        self.available = list(range(1, max_value + 1))
        heapq.heapify(self.available)
        self.in_use = set()

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            raise Exception("NumberPool instance not initialized. Call __new__ with max_value first.")
        return cls._instance

    def getNextFree(self):
        if not self.available:
            return -1
        next_free = heapq.heappop(self.available)
        self.in_use.add(next_free)
        return next_free

    def close(self, number):
        if number in self.in_use:
            self.in_use.remove(number)
            heapq.heappush(self.available, number)
        # else:
        #     raise ValueError(f"Number {number} was not in use")

# # Example usage
# # Initialize the singleton instance with a max_value the first time
# first_instance = NumberPool(10)

# # Access the singleton instance without directly creating a new one
# singleton_instance = NumberPool.getInstance()

# # This will not create a new instance, just return the existing one
# another_reference = NumberPool.getInstance()

# print(first_instance is singleton_instance)  # True
# print(singleton_instance is another_reference)  # True

# # Use the instance
# number = singleton_instance.getNextFree()
# print(f"Got number: {number}")
