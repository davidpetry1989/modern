from functools import lru_cache
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .models import DePara, LayoutImportacao


@lru_cache(maxsize=512)
def get_ct_for_model(model):
    return ContentType.objects.get_for_model(model)


def normalize(code: str) -> str:
    return (code or "").strip().lower()


@lru_cache(maxsize=2048)
def resolver(layout_id: int, model, codigo_externo: str):
    """Retorna target_id (ou None) mapeado para (layout, model, codigo_externo)."""
    ct = get_ct_for_model(model)
    code = normalize(codigo_externo)
    try:
        dp = DePara.objects.only("target_id").get(
            layout_id=layout_id, target_ct=ct, codigo_externo=code, ativo=True
        )
        return dp.target_id
    except DePara.DoesNotExist:
        return None


def bulk_upsert(layout_id: int, model, rows):
    """Cria/atualiza vários DePara de uma vez.

    rows: iterable de dicts com chaves codigo_externo, target_id, descricao_externa,
    observacao e ativo.
    """
    ct = get_ct_for_model(model)
    now = timezone.now()
    normalized = {}
    for row in rows:
        code = normalize(row.get("codigo_externo"))
        if not code:
            continue
        normalized[code] = row

    existing_qs = DePara.objects.filter(
        layout_id=layout_id, target_ct=ct, codigo_externo__in=list(normalized.keys())
    )
    existing = {dp.codigo_externo: dp for dp in existing_qs}
    to_create = []
    to_update = []
    for code, data in normalized.items():
        target_id = data.get("target_id")
        descricao = data.get("descricao_externa", "")
        observacao = data.get("observacao", "")
        ativo = data.get("ativo", True)
        if code in existing:
            dp = existing[code]
            dp.target_id = target_id
            dp.descricao_externa = descricao
            dp.observacao = observacao
            dp.ativo = ativo
            dp.updated_at = now
            to_update.append(dp)
        else:
            to_create.append(
                DePara(
                    layout_id=layout_id,
                    target_ct=ct,
                    target_id=target_id,
                    codigo_externo=code,
                    descricao_externa=descricao,
                    observacao=observacao,
                    ativo=ativo,
                    created_at=now,
                    updated_at=now,
                )
            )
    if to_create:
        DePara.objects.bulk_create(to_create)
    if to_update:
        DePara.objects.bulk_update(
            to_update,
            ["target_id", "descricao_externa", "observacao", "ativo", "updated_at"],
        )
    return len(to_create), len(to_update)