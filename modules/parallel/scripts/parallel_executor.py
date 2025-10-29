from multiprocessing import Pool

class ParallelExecutor:
    def run(self, func, data):
        with Pool() as pool:
            return pool.map(func, data)
