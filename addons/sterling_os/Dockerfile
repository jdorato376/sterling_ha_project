# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
WORKDIR /app

FROM base AS builder
COPY addons/sterling_os/requirements.txt ./
RUN pip wheel -r requirements.txt -w /wheels

FROM base
COPY --from=builder /wheels /wheels
COPY addons/sterling_os/ /app/
RUN pip install /wheels/*.whl
RUN chmod +x /app/run.sh
ENTRYPOINT ["/app/run.sh"]
