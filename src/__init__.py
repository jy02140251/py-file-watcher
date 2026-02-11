import asyncio
from dataclasses import dataclass
from typing import Callable, List, Dict, Any

@dataclass
class Task:
    name: str
    func: Callable
    args: tuple = ()
    kwargs: dict = None
    
    def __post_init__(self):
        self.kwargs = self.kwargs or {}

class Executor:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.tasks: List[Task] = []
        self.results: Dict[str, Any] = {}
    
    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
    
    async def run_async(self) -> Dict[str, Any]:
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def run_with_limit(task: Task):
            async with semaphore:
                if asyncio.iscoroutinefunction(task.func):
                    return await task.func(*task.args, **task.kwargs)
                return task.func(*task.args, **task.kwargs)
        
        results = await asyncio.gather(
            *[run_with_limit(t) for t in self.tasks],
            return_exceptions=True
        )
        
        for task, result in zip(self.tasks, results):
            self.results[task.name] = result
        
        return self.results

class Client:
    def __init__(self):
        self.executor = Executor()
    
    def run(self):
        return asyncio.run(self.executor.run_async())