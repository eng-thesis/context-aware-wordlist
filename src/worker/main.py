import asyncio

from faststream import FastStream
from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue

from common.logging import get_logger
from model import WordlistGenerator
from model.config import GeneratorConfig
from worker.config import WorkerConfig
from worker.models import (
    TaskStatus,
    WordlistErrorPayload,
    WordlistResult,
    WordlistResultMetadata,
    WordlistResultPayload,
    WordlistTask,
)

log = get_logger(__name__)

worker_config = WorkerConfig()  # type: ignore
log.debug(f"{worker_config = }")

broker = RabbitBroker(worker_config.broker_url)
app = FastStream(broker)

generator_config = GeneratorConfig()  # type: ignore
log.debug(f"{generator_config = }")
generator = WordlistGenerator(generator_config)

tasks_exchange = RabbitExchange("orchestrator.tasks", type=ExchangeType.TOPIC)
results_exchange = RabbitExchange("orchestrator.results", type=ExchangeType.DIRECT)

wordlist_queue = RabbitQueue(
    name="queue.wordlist_service",
    routing_key="wordlist.generate",
    durable=True,
)


@broker.subscriber(queue=wordlist_queue, exchange=tasks_exchange)
async def handle_wordlist_task(msg: WordlistTask) -> None:
    correlation_id = msg.metadata.correlation_id
    url = msg.payload.url

    log.info(f"[{correlation_id}] Received wordlist job for {url}")

    try:
        loop = asyncio.get_event_loop()
        responses = await loop.run_in_executor(
            None,
            lambda: generator.generate_multiple(
                msg.payload.html_content, url, n=msg.payload.n
            ),
        )
        endpoints = list(set().union(*[set(r.endpoints) for r in responses]))

        if msg.payload.input_wordlist:
            endpoints = list(set(endpoints) | set(msg.payload.input_wordlist))

        log.info(f"[{correlation_id}] Generated {len(endpoints)} endpoints for {url}")

        result = WordlistResult(
            metadata=WordlistResultMetadata(
                correlation_id=correlation_id,
                status=TaskStatus.SUCCESS,
            ),
            payload=WordlistResultPayload(
                url=url,
                endpoints=endpoints,
            ),
        )

    except Exception as e:
        log.error(f"[{correlation_id}] {e}")
        result = WordlistResult(
            metadata=WordlistResultMetadata(
                correlation_id=correlation_id,
                status=TaskStatus.ERROR,
            ),
            payload=WordlistErrorPayload(
                error_message=str(e),
            ),
        )

    await broker.publish(
        message=result,
        exchange=results_exchange,
        routing_key="task.completed",
    )


if __name__ == "__main__":
    asyncio.run(app.run())
