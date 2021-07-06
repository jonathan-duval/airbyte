#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import io
import os
from pathlib import Path

import docker
from source_acceptance_test.utils import ConnectorRunner


class TestEnvAttributes:
    def create_dockerfile(self, text, tag):
        # nano ~/.docker/config.json credsStore-> credStore to enable on MAC
        client = docker.from_env()
        fileobj = io.BytesIO()
        fileobj.write(text)

        fileobj.seek(0)
        args = {
            "path": os.path.abspath("."),
            "fileobj": fileobj,
            "tag": tag,
            "forcerm": True,
            "rm": True,
        }
        image, iterools_tee = client.images.build(**args)
        docker_runner = ConnectorRunner(image_name=tag, volume=Path("."))
        return docker_runner

    def test_build_dockerfile_valid(self):
        dockerfile_text = b"""
            FROM python:3.7-slim
            RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*
            ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
            ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
            """
        docker_runner = self.create_dockerfile(dockerfile_text, 'my-valid-one')

        assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT"), "AIRBYTE_ENTRYPOINT must be set in dockerfile"
        assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT") == " ".join(
            docker_runner.entry_point
        ), "env should be equal to space-joined entrypoint"

    def test_build_dockerfile_no_env(self):
        dockerfile_text = b"""
            FROM python:3.7-slim
            RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*
            ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
            """
        docker_runner = self.create_dockerfile(dockerfile_text, 'my-no-env-one')
        assert not docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT"), "this test should fail if AIRBYTE_ENTRYPOINT defined"

    def test_build_dockerfile_ne_properties(self):
        dockerfile_text = b"""
            FROM python:3.7-slim
            RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*
            ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
            ENTRYPOINT ["python3", "/airbyte/integration_code/main.py"]
            """
        docker_runner = self.create_dockerfile(dockerfile_text, 'ne__one')
        assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT"), "AIRBYTE_ENTRYPOINT must be set in dockerfile"
        assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT") != " ".join(docker_runner.entry_point), (
            "This test should fail if " ".join(ENTRYPOINT)==ENV"
        )
