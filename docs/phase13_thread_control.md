# Phase 13: Sovereign Thread Control

This phase introduces per-thread governance. The `threads` package stores a registry of active timelines along with a simple guard for locking and unlocking thread execution. A predictive scheduler can reprioritize based on lock state and last execution time, while a rollback engine demonstrates recovery hooks.
