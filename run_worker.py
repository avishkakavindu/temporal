import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import GreetingWorkflow, CatWorkflow
from activities import say_hello, fetch_cat_images


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="main-task-queue",
        workflows=[GreetingWorkflow, CatWorkflow],
        activities=[say_hello, fetch_cat_images],
    )
    print("Workers started. Watching for tasks...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

""" 
To get cats:
`temporal workflow execute --type CatWorkflow --task-queue main-task-queue --input 5`

To get a greeting:
`temporal workflow execute --type GreetingWorkflow --task-queue main-task-queue --input '"Avishka"'`
"""
