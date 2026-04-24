from datetime import timedelta
from temporalio import workflow

from activities import say_hello, fetch_cat_images


@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            say_hello, name, start_to_close_timeout=timedelta(seconds=5)
        )


@workflow.defn
class CatWorkflow:
    @workflow.run
    async def run(self, limit: int) -> list:
        # call activity
        results = await workflow.execute_activity(
            fetch_cat_images, limit, start_to_close_timeout=timedelta(seconds=10)
        )
        return results
