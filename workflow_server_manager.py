"""Manager for workflow server subprocesses."""

import atexit
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass
class WorkflowConfig:
    """Configuration for a workflow server."""

    name: str
    module: str
    port: int


# Hardcoded list of workflows - add more here as needed
WORKFLOW_CONFIGS = [
    WorkflowConfig(name="Character Generation Flow", module="character_generation_flow", port=8005),
    WorkflowConfig(name="Character Image Flow", module="character_image_flow", port=8006),
    WorkflowConfig(name="Story From Character", module="story_from_character", port=8007),
]


class WorkflowServerManager:
    """Manages workflow server subprocesses."""

    _instance: "WorkflowServerManager | None" = None

    def __init__(self) -> None:
        self.processes: dict[str, subprocess.Popen] = {}

    @classmethod
    def get_instance(cls) -> "WorkflowServerManager":
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.start_all()
            atexit.register(cls._instance.stop_all)
        return cls._instance

    def start_all(self) -> None:
        """Start all workflow servers."""
        for config in WORKFLOW_CONFIGS:
            self._start_server(config)

    def _start_server(self, config: WorkflowConfig) -> None:
        """Start a single workflow server subprocess."""
        if config.module in self.processes:
            msg = f"Server for {config.module} already running"
            logger.info(msg)
            return

        msg = f"Starting server for {config.module} on port {config.port}"
        logger.info(msg)

        env = os.environ.copy()
        env["WORKFLOW_MODULE"] = config.module
        env["GTN_CONFIG_ENABLE_WORKSPACE_FILE_WATCHING"] = "false"

        # Don't pipe stdout/stderr so server logs appear in console
        process = subprocess.Popen(  # noqa: S603
            [
                sys.executable,
                "-m",
                "fastapi",
                "run",
                "workflow_server.py",
                "--port",
                str(config.port),
            ],
            env=env,
        )

        self.processes[config.module] = process

        if not self._wait_for_health(config.port):
            msg = f"Server for {config.module} failed to start within timeout"
            logger.error(msg)
            process.kill()
            del self.processes[config.module]
            return

        msg = f"Server for {config.module} started successfully on port {config.port}"
        logger.info(msg)

    def _wait_for_health(self, port: int, timeout: float = 30.0, interval: float = 0.5) -> bool:
        """Wait for a server's health endpoint to respond."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with httpx.Client(timeout=2.0) as client:
                    response = client.get(f"http://localhost:{port}/health")
                    if httpx.codes.is_success(response.status_code):
                        return True
            except httpx.RequestError:
                pass
            time.sleep(interval)
        return False

    def stop_all(self) -> None:
        """Stop all workflow server subprocesses."""
        for module, process in self.processes.items():
            msg = f"Stopping server for {module}"
            logger.info(msg)
            process.terminate()
            try:
                process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                msg = f"Force killing server for {module}"
                logger.warning(msg)
                process.kill()
        self.processes.clear()

    def get_port(self, module: str) -> int | None:
        """Get the port for a workflow module."""
        for config in WORKFLOW_CONFIGS:
            if config.module == module:
                return config.port
        return None
