import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple

import chromadb
from chromadb.utils import embedding_functions

from infrastructure.config import settings

MANIFEST_PATH = Path(settings.MANIFEST_PATH_STRING)

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _slug(s: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in s).strip("-")[:120]

def build_embed_text(record: Dict[str, Any]) -> str:
    title = (record.get("title") or "").strip()
    summary = (record.get("summary") or "").strip()
    tags = " ".join(record.get("tags", []) or [])
    return f"Title: {title}\nTags: {tags}\nSummary: {summary}"

def compute_record_hash(record: Dict[str, Any]) -> str:
    payload = {
        "title": record.get("title"),
        "summary": record.get("summary"),
        "tags": record.get("tags", []),
    }
    return _sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def load_manifest() -> Dict[str, str]:
    try:
        if MANIFEST_PATH.exists():
            with MANIFEST_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"ERROR loading manifest: {e}", file=sys.stderr)
        print("Using empty manifest.", file=sys.stderr)
    return {}

def save_manifest(manifest: Dict[str, str]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = MANIFEST_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    tmp.replace(MANIFEST_PATH)

def load_records(paths: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in paths:
        fp = Path(p)
        if not fp.exists():
            print(f"WARN: seed file not found: {fp}", file=sys.stderr)
            continue
        try:
            with fp.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    print(f"WARN: {fp} is not a list, skipping", file=sys.stderr)
                    continue
                out.extend(data)
        except Exception as e:
            print(f"ERROR reading {fp}: {e}", file=sys.stderr)
    return out


# ----------------------------- Chroma wiring --------------------------------

def get_collection():
    client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
    collection = client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION,
        embedding_function=embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.OPENAI_API_KEY,
            model_name="text-embedding-3-small"
        ),
        metadata={"hnsw:space": "cosine"}
    )
    print("metric:", collection.metadata)
    return collection

def normalize_metadata(rec: Dict[str, Any]) -> Dict[str, Any]:
    tags_list = rec.get("tags") or []
    tags_str = "|".join(str(t) for t in tags_list)
    return {
        "title": rec.get("title") or "",
        "tags": tags_str,
    }

def diff(manifest: Dict[str, str], records: List[Dict[str, Any]]) -> Tuple[List[Dict], List[str]]:
    """
    Returns:
      to_upsert: list of {id, document, metadata} for new/changed
      to_delete: list of ids to remove (present in manifest but missing now)
    """
    # Build latest id->hash from current files
    latest_hashes: Dict[str, str] = {}
    id_to_payload: Dict[str, Dict[str, Any]] = {}

    for rec in records:
        title = rec.get("title")
        if not title:
            continue
        doc_id = _slug(title)
        h = compute_record_hash(rec)
        latest_hashes[doc_id] = h
        id_to_payload[doc_id] = rec

    # Detect upserts (new or changed)
    to_upsert: List[Dict[str, Any]] = []
    for doc_id, h in latest_hashes.items():
        if manifest.get(doc_id) != h:
            rec = id_to_payload[doc_id]
            to_upsert.append({
                "id": doc_id,
                "document": build_embed_text(rec),
                "metadata": normalize_metadata(rec)
            })

    # Detect deletions (in manifest but not in latest)
    to_delete = [doc_id for doc_id in manifest.keys() if doc_id not in latest_hashes]

    return to_upsert, to_delete, latest_hashes

def apply_changes(collection: chromadb.Collection, to_upsert: List[Dict], to_delete: List[str]) -> None:
    if to_delete:
        try:
            collection.delete(ids=to_delete)
            print(f"Deleted {len(to_delete)} docs from {settings.CHROMA_COLLECTION}")
        except Exception as e:
            print(f"ERROR deleting {len(to_delete)} docs: {e}", file=sys.stderr)

    if to_upsert:
        try:
            collection.upsert(
                ids=[x["id"] for x in to_upsert],
                documents=[x["document"] for x in to_upsert],
                metadatas=[x["metadata"] for x in to_upsert],
            )
            print(f"Upserted {len(to_upsert)} docs into {settings.CHROMA_COLLECTION}")
        except Exception as e:
            print(f"ERROR upserting {len(to_upsert)} docs: {e}", file=sys.stderr)

def run_sync() -> None:
    manifest = load_manifest()
    records = load_records([settings.BOOK_DATA_PATH])

    to_upsert, to_delete, latest_hashes = diff(manifest, records)

    if not to_upsert and not to_delete:
        print("Index up to date; no changes.")
        
        collection = get_collection()
        return

    collection = get_collection()
    apply_changes(collection, to_upsert, to_delete)

    # persist new manifest (only for kept/current ids)
    new_manifest = {**{k: v for k, v in manifest.items() if k not in to_delete}, **latest_hashes}
    save_manifest(new_manifest)
    print(f"Manifest saved to {MANIFEST_PATH}")