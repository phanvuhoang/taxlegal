"""
Temporal worker entry point for TaxLegal v4.

Run:
    python -m worker.temporal_worker
    
Environment variables:
    TEMPORAL_HOST       — Temporal server address (default: temporal:7233)
    TEMPORAL_NAMESPACE  — Temporal namespace (default: default)
"""
from __future__ import annotations

import asyncio
import logging
import os

logger = logging.getLogger(__name__)

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "temporal:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
TASK_QUEUE = "taxlegal-advisory"


async def run_worker() -> None:
    """Connect to Temporal and run the worker. Falls back to no-op if not installed."""
    try:
        from temporalio.client import Client
        from temporalio.worker import Worker

        from worker.workflows import TaxAdvisoryWorkflow
        from worker.activities import (
            run_intake_activity,
            run_research_activity,
            run_draft_activity,
            run_sa_review_activity,
            run_partner_review_activity,
            await_human_approval_activity,
            run_delivery_activity,
            run_audit_archive_activity,
        )

        client = await Client.connect(TEMPORAL_HOST, namespace=TEMPORAL_NAMESPACE)

        worker = Worker(
            client,
            task_queue=TASK_QUEUE,
            workflows=[TaxAdvisoryWorkflow],
            activities=[
                run_intake_activity,
                run_research_activity,
                run_draft_activity,
                run_sa_review_activity,
                run_partner_review_activity,
                await_human_approval_activity,
                run_delivery_activity,
                run_audit_archive_activity,
            ],
        )

        logger.info(
            f"Temporal worker starting — host={TEMPORAL_HOST}, "
            f"namespace={TEMPORAL_NAMESPACE}, queue={TASK_QUEUE}"
        )
        await worker.run()

    except ImportError:
        logger.warning("temporalio not installed — Temporal worker disabled.")
        logger.info("To enable durable execution: pip install temporalio")
        # Keep process alive as a no-op service so container stays running
        await asyncio.sleep(float("inf"))

    except Exception as e:
        logger.error(f"Temporal worker error: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )
    asyncio.run(run_worker())
