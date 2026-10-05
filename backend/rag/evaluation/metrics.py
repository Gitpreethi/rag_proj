"""Retrieval and faithfulness metrics for ablation experiments (Phase 19–20)."""


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    if not relevant_ids:
        return 0.0
    top = set(retrieved_ids[:k])
    return len(top & relevant_ids) / len(relevant_ids)


def mrr_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    for rank, doc_id in enumerate(retrieved_ids[:k], start=1):
        if doc_id in relevant_ids:
            return 1.0 / rank
    return 0.0
