# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
WORKDIR /app

FROM base AS builder
COPY requirements.txt ./
RUN pip wheel -r requirements.txt -w /wheels

FROM base
COPY --from=builder /wheels /wheels
COPY src /app/src
COPY modules /app/modules
COPY addons/sterling_os/run.sh /app/run.sh
COPY addons/sterling_os/config.json /app/config.json
COPY scripts/scaffold_phases.py /app/scaffold_phases.py
RUN pip install /wheels/*.whl
RUN python /app/scaffold_phases.py
ENTRYPOINT ["./run.sh"]
