"""Admin endpoints — multi-dataset import registry, guarded by X-Admin-Token.

Backward-compatible aliases for the original single-dataset endpoints are
retained so existing frontends/tests keep working while they migrate.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends

from core.security import require_admin_token
from core import datasets as ds

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin_token)],
)


# ---- Multi-dataset (new) ---------------------------------------------------
@router.get("/datasets")
async def list_datasets():
    return await ds.list_datasets()


@router.get("/datasets/{key}/info")
async def dataset_info(key: str):
    return await ds.dataset_info(key)


@router.post("/datasets/{key}/import")
async def dataset_import(key: str):
    return await ds.import_dataset(key)


@router.post("/datasets/{key}/reset")
async def dataset_reset(key: str):
    return await ds.reset_dataset(key)


@router.post("/datasets/reset-all")
async def reset_all_datasets():
    return await ds.reset_all_datasets()


# ---- Legacy aliases (backward-compat for /open-dataset/*) ------------------
@router.get("/open-dataset/info")
async def legacy_info():
    return await ds.dataset_info("uci")


@router.post("/open-dataset/import")
async def legacy_import():
    return await ds.import_dataset("uci")


@router.post("/open-dataset/reset")
async def legacy_reset():
    return await ds.reset_dataset("uci")
